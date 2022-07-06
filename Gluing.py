import cv2
import numpy as np
import os

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
    filename_frame = os.listdir(os.path.join(path_in, 'new1'))
    for name in filename_frame:
        for i in range(width * height):
            img[i] = cv2.imread(f"./{path_in}/new{i + 1}/" + name)
        for i in range(height):
            Horizontal[i] = np.hstack(img[width * i: width * (i + 1)])
        Vertical_attachment = np.vstack(Horizontal)
        cv2.imwrite(f"./{ex_path}/" + name, Vertical_attachment)


def main():
    GluingImages("examples/bat_test", "result", 2, 3)


if __name__ == '__main__':
    main()
