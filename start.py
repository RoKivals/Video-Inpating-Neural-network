import os
import cv2
import numpy as np
from PIL import Image
import time
import test


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
    lst = sorted(lst, key=lambda x: int(x[0:-4]))  # Собираем названия всех фреймов по порядку
    # TODO: Можно попробовать выставить эти кадры по времени создания, а не по имени (в теории это более надёжно)
    frames = []
    for fr in [path + '/' + name for name in lst]:
        image = cv2.imread(fr)
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        frames.append(image)
    print('Saving videos...')
    comp_frames = [np.array(f).astype(np.uint8) for f in frames]
    save_name = save_name + '.mp4'
    # TODO: Вот тут надо определиться с парсером аргументов
    final_path = os.path.join(path_out, save_name)
    writer = cv2.VideoWriter(final_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    for f in range(len(comp_frames)):
        comp = comp_frames[f].astype(np.uint8)
        writer.write(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
    writer.release()
    print(f'Finish test! The result video is saved in: {final_path}.')


# Цикл пропускающий все картинки через нейронку
def Cycle(file_in: str, mask_in: str, video_out: str, step, neighbor, height, width, tmp_vpath: str, tmp_mpath: str, h_cuts: int, w_cuts: int,
          overlap: int, mp4v: bool, mp4m: bool, fps: int, fin_name: str):
    start_time = time.time()
    if not os.path.exists(tmp_vpath):
        os.makedirs(tmp_vpath)
    if not os.path.exists(tmp_mpath):
        os.makedirs(tmp_mpath)
    if mp4v:
        os.makedirs('./Temp/Frames')
        test.ReadFramesFromVideo(mp4v, file_in, './Temp/Frames')
        file_in = './Temp/Frames'
    if mp4m:
        os.makedirs('./Temp/Mask')
        test.ReadFramesFromVideo(mp4m, mask_in, './Temp/Mask')
        mask_in = './Temp/Mask'
    # Режем видео
    CropImages(file_in, tmp_vpath, w_cuts, h_cuts, overlap, width, height)
    # Режем маски
    CropImages(mask_in, tmp_mpath, w_cuts, h_cuts, overlap, width, height)
    # Запускаем нейронку
    test.main_worker(tmp_vpath, tmp_mpath, "release_model/E2FGVI-HQ-CVPR22.pth", w_cuts * h_cuts, "e2fgvi_hq", neighbor, step, 1000, 580)
    GluingImages("./Temp/result", "./Temp/ResultFrame", w_cuts, h_cuts)
    MakingVideo("./Temp/ResultFrame", video_out, fps, (width, height), fin_name)
    print("--- %s seconds ---" % (time.time() - start_time))
    return 0
