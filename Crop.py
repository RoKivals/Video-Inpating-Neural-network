import cv2
import os

'''
path_in - путь, откуда берутся файлы для нарезки
path_out - путь, куда будут сохранены нарезанные файлы
width_cuts - кол-во нарезок ширины
height_cuts - кол-во нарезок высоты
'''


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

CropImages("./examples/batman/batman", "examples/i/", 4, 4)
