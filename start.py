import os
import cv2
import numpy as np
from PIL import Image
import time
import test
import main
from main import Args


def CropImages(path_in: str, path_out: str, width_cuts: int, height_cuts: int, overlap: int, width: int, height: int):
    if path_in[-1] != "/":
        path_in += "/"
    if path_out[-1] != "/":
        path_out += "/"

    filenames = os.listdir(path_in)

    if not os.path.exists(path_out):
        os.makedirs(path_out)

    # Находим высоту и ширину для каждого разделения
    block_width = width // width_cuts
    block_height = height // height_cuts
    count = 1
    for name in filenames:
        img = cv2.imread(path_in + name)
        count = 1  # Нумерация разделения (слева направо, сверху вниз)
        for i in range(height_cuts):
            curr_y = i * block_height
            for j in range(width_cuts):
                curr_x = j * block_width
                # Обработка левой границы
                if count % width_cuts == 1:
                    # Левый верхний угол
                    if count == 1:
                        crop_img = img[curr_y:curr_y + block_height + overlap, curr_x:curr_x + block_width + overlap]
                    # Левый нижний угол
                    elif count == width_cuts * (height_cuts - 1) + 1:
                        crop_img = img[curr_y - overlap:curr_y + block_height, curr_x:curr_x + block_width + overlap]
                    # Сама стенка
                    else:
                        crop_img = img[curr_y - overlap:curr_y + block_height + overlap, curr_x:curr_x + block_width + overlap]
                # Обработка верхней границы
                elif count <= width_cuts:
                    # Правый верхний угол
                    if count == width_cuts:
                        crop_img = img[curr_y:curr_y + block_height + overlap, curr_x - overlap:curr_x + block_width]
                    # Сама стенка
                    else:
                        crop_img = img[curr_y:curr_y + block_height + overlap, curr_x - overlap:curr_x + block_width + overlap]
                # Обработка правой границы
                elif count % width_cuts == 0:
                    # Правый нижний угол
                    if count == width_cuts * height_cuts:
                        crop_img = img[curr_y - overlap:curr_y + block_height, curr_x - overlap:curr_x + block_width]
                    # Сама стенка
                    else:
                        crop_img = img[curr_y - overlap:curr_y + block_height + overlap, curr_x - overlap:curr_x + block_width]
                # Обработка нижней границы
                elif width_cuts * (height_cuts - 1) + 1 < count < height_cuts * width_cuts:
                    # Сама стенка
                    crop_img = img[curr_y - overlap:curr_y + block_height, curr_x - overlap:curr_x + block_width + overlap]
                # Обработка внутренних блоков
                else:
                    crop_img = img[curr_y - overlap:curr_y + block_height + overlap, curr_x - overlap:curr_x + block_width + overlap]
                if not os.path.exists(path_out + str(count)):
                    os.makedirs(path_out + str(count))
                cv2.imwrite(path_out + str(count) + "/" + name, crop_img)
                count += 1


'''
path_in - путь до папки, в которой лежат все остальные папки с нарезанными кадрами
ex_path - выходной путь, то есть куда будет сохранено конечное видео
width - кол-во нарезок по вертикали
height - кол-во нарезок по горизонтали
'''


def GluingImages(path_in: str, ex_path: str, width: int, height: int):
    if not os.path.exists(ex_path):
        os.makedirs(ex_path)
    img = [None] * width * height
    Horizontal = [None] * height
    filename_frame = os.listdir(os.path.join(path_in, '1'))
    for name in filename_frame:
        for i in range(width * height):
            img[i] = cv2.imread(f"./{path_in}/{i + 1}/" + name)
        for i in range(height):
            Horizontal[i] = np.hstack(img[width * i: width * (i + 1)])
        Vertical_attachment = np.vstack(Horizontal)
        cv2.imwrite(f"./{ex_path}/" + name, Vertical_attachment)


# создание видео из готовых кадров
def MakingVideo(path: str, path_out: str, fps: int, size: tuple, save_name: str):
    lst = os.listdir(path)  # Путь, где лежат готовые фреймы
    lst.sort()  # Собираем названия всех фреймов по порядку
    # TODO: Можно попробовать выставить эти кадры по времени создания, а не по имени (в теории это более надёжно)
    frames = []
    for fr in [os.path.join(path, name) for name in lst]:
        image = cv2.imread(fr)  
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        frames.append(image)
    print('Saving videos...')
    comp_frames = [np.array(f).astype(np.uint8) for f in frames]
    # TODO: Вот тут надо определиться с парсером аргументов
    final_path = os.path.join(path_out, save_name)
    writer = cv2.VideoWriter(final_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    for f in range(len(comp_frames)):
        comp = comp_frames[f].astype(np.uint8)
        writer.write(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
    writer.release()
    print(f'Finish test! The result video is saved in: {final_path}.')


def CropOverlaps(path, width_cuts: int, height_cuts: int, overlap:int, width: int, height: int):
    dirnames = os.listdir(path)
    count = 1
    for dir in dirnames:
        dir_path = os.path.join(path, dir)
        filenames = os.listdir(dir_path)
        block_width = width
        block_height = height
        for file in filenames:
            img = cv2.imread(os.path.join(dir_path, file))
            for i in range(height_cuts):
                curr_y = 0
                for j in range(width_cuts):
                    curr_x = 0
                    # Обработка левой границы
                    if count % width_cuts == 1:
                        # Левый верхний угол
                        if count == 1:
                            crop_img = img[curr_y:curr_y + block_height, curr_x:curr_x + block_width]
                        # Левый нижний угол
                        elif count == width_cuts * (height_cuts - 1) + 1:
                            crop_img = img[curr_y + overlap:curr_y + block_height + overlap, curr_x:curr_x + block_width]
                        # Сама стенка
                        else:
                            crop_img = img[curr_y + overlap:curr_y + block_height + overlap, curr_x:curr_x + block_width]
                    # Обработка верхней границы
                    elif count <= width_cuts:
                        # Правый верхний угол
                        if count == width_cuts:
                            crop_img = img[curr_y:curr_y + block_height, curr_x + overlap:curr_x + block_width + overlap]
                        # Сама стенка
                        else:
                            crop_img = img[curr_y + overlap:curr_y + block_height + overlap, curr_x + overlap:curr_x + block_width + overlap]
                    # Обработка правой границы
                    elif count % width_cuts == 0:
                        # Правый нижний угол
                        if count == width_cuts * height_cuts:
                            crop_img = img[curr_y + overlap:curr_y + block_height + overlap, curr_x + overlap:curr_x + block_width + overlap]
                        # Сама стенка
                        else:
                            crop_img = img[curr_y + overlap:curr_y + block_height - overlap, curr_x + overlap:curr_x + block_width]
                    # Обработка нижней границы
                    elif width_cuts * (height_cuts - 1) + 1 < count < height_cuts * width_cuts:
                        # Сама стенка
                        crop_img = img[curr_y + overlap:curr_y + block_height, curr_x + overlap:curr_x + block_width - overlap]
                    # Обработка внутренних блоков
                    else:
                        crop_img = img[curr_y + overlap:curr_y + block_height - overlap, curr_x + overlap:curr_x + block_width - overlap]

                    cv2.imwrite(os.path.join(dir_path, file), crop_img)

        count += 1


# Цикл пропускающий все картинки через нейронку
def Cycle(args: main.Args):
    start_time = time.time()
    if not os.path.exists(args.tmp_vpath):
        os.makedirs(args.tmp_vpath)
    if not os.path.exists(args.tmp_mpath):
        os.makedirs(args.tmp_mpath)
    if args.mp4v:
        os.makedirs('./Temp/Frames')
        test.ReadFramesFromVideo(args.mp4v, args.video, './Temp/Frames')
        args.video = './Temp/Frames'
    if args.mp4m:
        os.makedirs('./Temp/Mask')
        test.ReadFramesFromVideo(args.mp4m, args.mask, './Temp/Mask')
        args.mask = './Temp/Mask'
    # # Режем видео
    CropImages(args.video, args.tmp_vpath, args.w_cuts, args.h_cuts, args.overlap, args.width, args.height)
    # Режем маски
    CropImages(args.mask, args.tmp_mpath, args.w_cuts, args.h_cuts, args.overlap, args.width, args.height)
    # Запускаем нейронку
    block_width = args.width // args.w_cuts
    block_height = args.height // args.h_cuts
    block_height_with_overlap = block_height + args.overlap
    block_width_with_overlap = block_width + args.overlap

    test.main_worker(args, block_width_with_overlap, block_height_with_overlap)
    CropOverlaps("./Temp/result", args.w_cuts, args.h_cuts, args.overlap, block_width, block_height)
    GluingImages("./Temp/result", "./Temp/ResultFrame", args.w_cuts, args.h_cuts)
    MakingVideo("./Temp/ResultFrame", args.video_out, args.fps, (args.width, args.height), args.final_name)
    print("--- %s seconds ---" % (time.time() - start_time))
    return 0
