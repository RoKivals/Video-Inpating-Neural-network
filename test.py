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
from main import Args




# Сохранение кадров после обработки с помощью нейронной сети
def saving_frames(comp_frames, namedir, args):
    res_dir = os.path.join("./Temp/result/", namedir)
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
    filenames = os.listdir(args.video)
    for i in range(len(comp_frames)):
        comp = comp_frames[i]
        cv2.imwrite(os.path.join(res_dir, filenames[i]), cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))


# sample reference frames from the whole video
def get_ref_index(f, neighbor_ids, length, args):
    ref_index = []
    if args.num_ref == -1:
        for i in range(0, length, args.step):
            if i not in neighbor_ids:
                ref_index.append(i)
    else:
        start_idx = max(0, f - args.step * (args.num_ref // 2))
        end_idx = min(length, f + args.step * (args.num_ref // 2))
        for i in range(start_idx, end_idx + 1, args.step):
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
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)), iterations=4)
        masks.append(Image.fromarray(m * 255))
    return masks


# Считываем фреймы из видео
def ReadFramesFromVideo(id: int, file_in, tmp_out=" "):
    if id == 0:
        vname = file_in.video
        frames = []
        vidcap = cv2.VideoCapture(vname)
        success, image = vidcap.read()
        count = 0
        while success:
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            cv2.imwrite(tmp_out, image)  # TODO здесь нужно название добавить
    if id == 1:
        frames = []
        lst = os.listdir(file_in)
        lst.sort()
        fr_lst = [os.path.join(file_in, name) for name in lst]
        for fr in fr_lst:
            image = cv2.imread(fr)
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            frames.append(image)
        return frames


# Изменение разрешения
def resize_frames(frames, size=None):
    if size is not None:
        frames = [f.resize(size) for f in frames]
    else:
        size = frames[0].size
    return frames, size


'''

'''


def main_worker(args, width, height, app):
    root_video = args.tmp_vpath
    root_mask = args.tmp_mpath
    for iteration in range(1, args.number + 1):
        video = os.path.join(root_video, str(iteration))
        mask = os.path.join(root_mask, str(iteration))
        # set up models
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if args.set_size:
            size = (width, height)
        else:
            size = None
        net = importlib.import_module('model.' + args.model)
        model = net.InpaintGenerator().to(device)
        data = torch.load(args.ckpt, map_location=device)
        model.load_state_dict(data)
        model.eval()
        frames = ReadFramesFromVideo(1, video)
        frames, size = resize_frames(frames, size)
        h, w = size[1], size[0]
        video_length = len(frames)
        imgs = to_tensors()(frames).unsqueeze(0) * 2 - 1
        frames = [np.array(f).astype(np.uint8) for f in frames]
        masks = read_mask(mask, size)
        binary_masks = [np.expand_dims((np.array(m) != 0).astype(np.uint8), 2) for m in masks]
        masks = to_tensors()(masks).unsqueeze(0)
        imgs, masks = imgs.to(device), masks.to(device)
        comp_frames = [None] * video_length
        # completing holes by e2fgvi
        for f in tqdm(range(0, video_length, args.neighbor_stride)):
            neighbor_ids = [i for i in range(max(0, f - args.neighbor_stride), min(video_length, f + args.neighbor_stride + 1))]
            ref_ids = get_ref_index(f, neighbor_ids, video_length, args)
            selected_imgs = imgs[:1, neighbor_ids + ref_ids, :, :, :]
            selected_masks = masks[:1, neighbor_ids + ref_ids, :, :, :]
            with torch.no_grad():
                masked_imgs = selected_imgs * (1 - selected_masks)
                mod_size_h = 60
                mod_size_w = 108
                h_pad = (mod_size_h - h % mod_size_h) % mod_size_h
                w_pad = (mod_size_w - w % mod_size_w) % mod_size_w
                masked_imgs = torch.cat([masked_imgs, torch.flip(masked_imgs, [3])], 3)[:, :, :, :h + h_pad, :]
                masked_imgs = torch.cat([masked_imgs, torch.flip(masked_imgs, [4])], 4)[:, :, :, :, :w + w_pad]
                pred_imgs, _ = model(masked_imgs, len(neighbor_ids))
                pred_imgs = pred_imgs[:, :, :h, :w]
                pred_imgs = (pred_imgs + 1) / 2
                pred_imgs = pred_imgs.cpu().permute(0, 2, 3, 1).numpy() * 255
                for i in range(len(neighbor_ids)):
                    idx = neighbor_ids[i]
                    img = np.array(pred_imgs[i]).astype(
                        np.uint8) * binary_masks[idx] + frames[idx] * (1 - binary_masks[idx])
                    if comp_frames[idx] is None:
                        comp_frames[idx] = img
                    else:
                        comp_frames[idx] = comp_frames[idx].astype(np.float32) * 0.5 + img.astype(np.float32) * 0.5
        saving_frames(comp_frames, str(iteration), args)
        app.progressBar.setValue(app.progressBar.value() + 60 // args.number)
