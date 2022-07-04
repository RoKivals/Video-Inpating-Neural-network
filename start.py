import os
import cv2
import numpy as np
from PIL import Image
import time


PATH_TO_PYTHON = "C:/Users/USER/pythonProject/Project/new/Scripts/python.exe"

def cropwithoverlap_imgs(path_in, path_out, n_w, n_h, overlap):
    if path_in[-1] != "/":
        path_in += "/"
    if path_out[-1] != "/":
        path_out += "/"

    filenames = os.listdir(path_in)

    if not os.path.exists(path_out):
        os.makedirs(path_out)

    w = 1920 // n_w
    h = 1080 // n_h

    count = 1
    for name in filenames:
        img = cv2.imread(path_in + name)
        count = 1
        for i in range(n_h):
            y = i * h
            for j in range(n_w):
                x = j * w
                if count == 1:
                    crop_img = img[y:y + h + overlap, x:x + w + overlap]
                elif count == 2:
                    crop_img = img[y:y + h + overlap, x - overlap:x + w]
                elif count == 3:
                    crop_img = img[y - overlap:y + h, x:x + w + overlap]
                elif count == 4:
                    crop_img = img[y - overlap:y + h, x - overlap:x + w]
                if not os.path.exists(path_out + str(count)):
                    os.makedirs(path_out + str(count))
                cv2.imwrite(path_out + str(count) + "/" + name, crop_img)
                count += 1


def newcrop():
    path = "examples/result"
    filenames = os.listdir("examples/result/1")
    for name in filenames:
        img1 = cv2.imread("examples/result/1/" + name)
        img2 = cv2.imread("examples/result/2/" + name)
        img3 = cv2.imread("examples/result/3/" + name)
        img4 = cv2.imread("examples/result/4/" + name)

        crop_img1 = img1[0:540, 0:960]
        crop_img2 = img2[0:540, 40:1000]
        crop_img3 = img3[40:580, 0:960]
        crop_img4 = img4[40:580, 40:1000]

        cv2.imwrite("examples/result/1/" + name, crop_img1)
        cv2.imwrite("examples/result/2/" + name, crop_img2)
        cv2.imwrite("examples/result/3/" + name, crop_img3)
        cv2.imwrite("examples/result/4/" + name, crop_img4)


def col():

    filename_frame = os.listdir("./examples/result/1")
    if not os.path.exists("./examples/collage"):
        os.makedirs("./examples/collage")
    for name in filename_frame:
        img1 = cv2.imread("./examples/result/1/" + name)
        img2 = cv2.imread("./examples/result/2/" + name)
        img3 = cv2.imread("./examples/result/3/" + name)
        img4 = cv2.imread("./examples/result/4/" + name)



        Horizontal1=np.hstack([img1,img2])
        Horizontal2=np.hstack([img3,img4])
        Vertical_attachment=np.vstack([Horizontal1,Horizontal2])

        cv2.imwrite("./examples/collage/" + name, Vertical_attachment)


def vid(pathout):
    path = 'examples/collage'
    lst = os.listdir(path)
    lst = sorted(lst)
    listframe = [path + '/' + name for name in lst]
    frames = []
    print(lst)
    for fr in listframe:
        image = cv2.imread(fr)
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        frames.append(image)
    print('Saving videos...')
    res_dir = 'results'  # Название папки для сохранения
    res_name = '_results.mp4'  # Название готового файла
    # old_name = args.video.split('/')[-1]  # Первоначальное название видео
    video_length = 49
    comp_frames = [np.array(f).astype(np.uint8) for f in frames]
    #save_name = old_name.replace('.mp4', res_name) if args.use_mp4 else old_name + res_name
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
    save_path = os.path.join(pathout, 'anime.mp4')
    writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*"mp4v"), 24, (1920, 1080))
    for f in range(video_length):
        comp = comp_frames[f].astype(np.uint8)
        writer.write(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
    writer.release()
    print(f'Finish test! The result video is saved in: {save_path}.')


def cycle(fileinput, fileoutput, maskinput, step, neighbor):
    start_time = time.time()

    if not os.path.exists("examples/v"):
        os.makedirs("examples/v")

    if not os.path.exists("examples/v_mask"):
        os.makedirs("examples/v_mask")

    cropwithoverlap_imgs(fileinput, "examples/v", 2, 2, 40)
    cropwithoverlap_imgs(maskinput, "examples/v_mask", 2, 2, 40)

    os.system(f'{PATH_TO_PYTHON} test1.py -n 1 --step {int(step)} --neighbor_stride {int(neighbor)} --model e2fgvi_hq --video ./examples/v/1 --mask ./examples/v_mask/1  --ckpt release_model/E2FGVI-HQ-CVPR22.pth --width 1000 --height 580')
    os.system(f'{PATH_TO_PYTHON} test1.py -n 2 --step {int(step)} --neighbor_stride {int(neighbor)} --model e2fgvi_hq --video ./examples/v/2 --mask ./examples/v_mask/2  --ckpt release_model/E2FGVI-HQ-CVPR22.pth --width 1000 --height 580')
    os.system(f'{PATH_TO_PYTHON} test1.py -n 3 --step {int(step)} --neighbor_stride {int(neighbor)} --model e2fgvi_hq --video ./examples/v/3 --mask ./examples/v_mask/3  --ckpt release_model/E2FGVI-HQ-CVPR22.pth --width 1000 --height 580')
    os.system(f'{PATH_TO_PYTHON} test1.py -n 4 --step {int(step)} --neighbor_stride {int(neighbor)} --model e2fgvi_hq --video ./examples/v/4 --mask ./examples/v_mask/4  --ckpt release_model/E2FGVI-HQ-CVPR22.pth --width 1000 --height 580')

    video = "examples/v"
    mask = "examples/v_mask"

    newcrop()

    col()

    vid(fileoutput)


    print("--- %s seconds ---" % (time.time() - start_time))
    return 0