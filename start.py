import os
import cv2
import numpy as np
from PIL import Image
import time
import test


PATH_TO_PYTHON = "C:/Users/USER/pythonProject/Project/new/Scripts/python.exe"

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


def GluingImages(path_in: str, ex_path: str, width: int, height: int):
    if not os.path.exists(ex_path):
        os.makedirs(ex_path)
    img = [None] * width * height
    Horizontal = [None] * height
    filename_frame = os.listdir(os.path.join(path_in, 'new1'))
    for name in filename_frame:
        for i in range(width * height):
            img[i] = cv2.imread(f"./{path_in}/new{i + 1}/" + name)
        for i in range(height):
            Horizontal[i] = np.hstack(img[width * i: width * (i + 1)])
        Vertical_attachment = np.vstack(Horizontal)
        cv2.imwrite(f"./{ex_path}/" + name, Vertical_attachment)

        cv2.imwrite("./examples/collage/" + name, Vertical_attachment)

# создание видео из готовых кадров
def making_video(path: str, len: int, fps: int, size: tuple):
    lst = os.listdir(path)  # Путь, где лежат готовые фреймы
    lst = sorted(lst, key=lambda x: int(x[0:-4]))  # Собираем названия всех фреймов по порядку
    # TODO: Можно попробовать выставить эти кадры по времени создания, а не по имени (в теории это более надёжно)
    frames = []

    for fr in [path + '/' + name for name in lst]:
        image = cv2.imread(fr)
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        frames.append(image)
    print('Saving videos...')

    res_dir = 'results'  # Название папки для сохранения
    res_name = '_results.mp4'  # Название готового файла
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    # old_name = args.video.split('/')[-1]  # Первоначальное название видео
    comp_frames = [np.array(f).astype(np.uint8) for f in frames]

    # TODO: Вот тут надо определиться с парсером аргументов
    save_name = 'anime.mp4'  # old_name.replace('.mp4', res_name) if args.use_mp4 else old_name + res_name
    final_path = os.path.join(res_dir, save_name)
    writer = cv2.VideoWriter(final_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    for f in range(len):
        comp = comp_frames[f].astype(np.uint8)
        writer.write(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
    writer.release()
    print(f'Finish test! The result video is saved in: {save_path}.')


def cycle(fileinput, fileoutput, maskinput, step, neighbor, height, width):
    start_time = time.time()

    video = "examples/v"
    mask = "examples/v_mask"

    if not os.path.exists(video):
        os.makedirs(video)

    if not os.path.exists(video):
        os.makedirs(mask)

    cropwithoverlap_imgs(fileinput, video, 2, 2, 40, height, width)
    cropwithoverlap_imgs(maskinput, mask, 2, 2, 40, height, width)

    test.main_worker(video, mask, "release_model/E2FGVI-HQ-CVPR22.pth", 4, "e2fgvi_hq", neighbor, step, 1000, 580)

    newcrop()

    col()

    vid(fileoutput)


    print("--- %s seconds ---" % (time.time() - start_time))
    return 0