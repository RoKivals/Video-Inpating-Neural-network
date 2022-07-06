import cv2
from PIL import Image
import numpy as np
import importlib
import os
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib import animation
import torch

from core.utils import to_tensors


class Args:
    def __init__(self):
        self.video = None  # str
        self.mask = None  # str
        self.ckpt = None  # str
        self.number = None  # int
        self.model = None  # str
        self.num_ref = None  # int
        self.neighbor_stride = None  # int
        self.default_fps = None  # int
        self.use_mp4 = None  # bool
        self.ref_length = None  # int
        self.set_size = None  # bool
        self.width = None  # int
        self.height = None  # int

    def setup(self, video, mask, ckpt, number, model, num_ref, neighbor_stride, savefps, ref_length, width, height):
        self.video = video  # str
        self.mask = mask  # str
        self.ckpt = ckpt  # str
        self.number = number  # int
        self.model = model  # str
        self.num_ref = num_ref  # int
        self.neighbor_stride = neighbor_stride  # int
        self.default_fps = savefps  # int
        self.ref_length = ref_length  # int
        self.width = width  # int
        self.height = height  # int


def main_worker(video, mask, ckpt, number, model, neighbor_stride, ref_length, width, height):
    args = Args()
    args.setup(video, mask, ckpt, number, model, -1, neighbor_stride, 24, ref_length, width, height)

    def saving_frames(comp_frames, namedir):
        if namedir[-1] != "/":
            namedir += "/"
        res_dir = "examples/result/" + namedir
        if not os.path.exists(res_dir):
            os.makedirs(res_dir)
        filenames = os.listdir(args.video)
        for i in range(len(comp_frames)):
            comp = comp_frames[i]
            cv2.imwrite(res_dir + filenames[i], cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))

    # sample reference frames from the whole video
    def get_ref_index(f, neighbor_ids, length):
        ref_index = []
        if args.num_ref == -1:
            for i in range(0, length, args.ref_length):
                if i not in neighbor_ids:
                    ref_index.append(i)
        else:
            start_idx = max(0, f - args.ref_length * (args.num_ref // 2))
            end_idx = min(length, f + args.ref_length * (args.num_ref // 2))
            for i in range(start_idx, end_idx + 1, args.ref_length):
                if i not in neighbor_ids:
                    if len(ref_index) > args.num_ref:
                        break
                    ref_index.append(i)
        return ref_index

    # read frame-wise masks
    def read_mask(mpath, size):
        masks = []
        mnames = os.listdir(mpath)
        mnames.sort()
        for mp in mnames:
            m = Image.open(os.path.join(mpath, mp))
            m = m.resize(size, Image.NEAREST)
            m = np.array(m.convert('L'))
            m = np.array(m > 0).astype(np.uint8)
            m = cv2.dilate(m,
                           cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)),
                           iterations=4)
            masks.append(Image.fromarray(m * 255))
        return masks

    #  read frames from video
    def read_frame_from_videos(args):
        vname = args.video
        frames = []
        if args.use_mp4:
            vidcap = cv2.VideoCapture(vname)
            success, image = vidcap.read()
            count = 0
            while success:
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                frames.append(image)
                success, image = vidcap.read()
                count += 1
        else:
            lst = os.listdir(vname)
            lst.sort()
            fr_lst = [vname + '/' + name for name in lst]
            for fr in fr_lst:
                image = cv2.imread(fr)
                image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                frames.append(image)
        return frames

    # resize frames
    def resize_frames(frames, size=None):
        if size is not None:
            frames = [f.resize(size) for f in frames]
        else:
            size = frames[0].size
        return frames, size

    root_video = args.video
    root_mask = args.mask
    print(1)
    for iteration in range(1, args.number+ 1):
        print(1)
        args.video = os.path.join(root_video, str(iteration))
        args.mask = os.path.join(root_mask, str(iteration))
        # set up models
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if args.model == "e2fgvi":
            size = (432, 240)
        elif args.set_size:
            size = (args.width, args.height)
        else:
            size = None

        net = importlib.import_module('model.' + args.model)
        model = net.InpaintGenerator().to(device)
        data = torch.load(args.ckpt, map_location=device)
        model.load_state_dict(data)
        print(f'Loading model from: {args.ckpt}')
        model.eval()

        # prepare datset
        args.use_mp4 = True if args.video.endswith('.mp4') else False
        print(
            f'Loading videos and masks from: {args.video} | INPUT MP4 format: {args.use_mp4}'
        )
        frames = read_frame_from_videos(args)
        frames, size = resize_frames(frames, size)
        h, w = size[1], size[0]
        video_length = len(frames)
        imgs = to_tensors()(frames).unsqueeze(0) * 2 - 1
        frames = [np.array(f).astype(np.uint8) for f in frames]

        masks = read_mask(args.mask, size)
        binary_masks = [
            np.expand_dims((np.array(m) != 0).astype(np.uint8), 2) for m in masks
        ]
        masks = to_tensors()(masks).unsqueeze(0)
        imgs, masks = imgs.to(device), masks.to(device)
        comp_frames = [None] * video_length

        # completing holes by e2fgvi
        print(f'Start test...')
        for f in tqdm(range(0, video_length, args.neighbor_stride)):
            neighbor_ids = [
                i for i in range(max(0, f - args.neighbor_stride),
                                 min(video_length, f + args.neighbor_stride + 1))
            ]
            ref_ids = get_ref_index(f, neighbor_ids, video_length)
            selected_imgs = imgs[:1, neighbor_ids + ref_ids, :, :, :]
            selected_masks = masks[:1, neighbor_ids + ref_ids, :, :, :]
            with torch.no_grad():
                masked_imgs = selected_imgs * (1 - selected_masks)
                mod_size_h = 60
                mod_size_w = 108
                h_pad = (mod_size_h - h % mod_size_h) % mod_size_h
                w_pad = (mod_size_w - w % mod_size_w) % mod_size_w
                masked_imgs = torch.cat(
                    [masked_imgs, torch.flip(masked_imgs, [3])],
                    3)[:, :, :, :h + h_pad, :]
                masked_imgs = torch.cat(
                    [masked_imgs, torch.flip(masked_imgs, [4])],
                    4)[:, :, :, :, :w + w_pad]
                pred_imgs, _ = model(masked_imgs, len(neighbor_ids))
                pred_imgs = pred_imgs[:, :, :h, :w]
                pred_imgs = (pred_imgs + 1) / 2
                pred_imgs = pred_imgs.cpu().permute(0, 2, 3, 1).numpy() * 255
                for i in range(len(neighbor_ids)):
                    idx = neighbor_ids[i]
                    img = np.array(pred_imgs[i]).astype(
                        np.uint8) * binary_masks[idx] + frames[idx] * (
                            1 - binary_masks[idx])
                    if comp_frames[idx] is None:
                        comp_frames[idx] = img
                    else:
                        comp_frames[idx] = comp_frames[idx].astype(
                            np.float32) * 0.5 + img.astype(np.float32) * 0.5

        saving_frames(comp_frames, str(iteration))
