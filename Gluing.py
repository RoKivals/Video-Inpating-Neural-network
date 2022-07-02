import cv2
import numpy as np
import os


def GluingImages(path: str, width: int, height: int):
    if not os.path.exists("examples/collage_batman"):
        os.makedirs("./examples/collage_batman/")
    img = [None] * width * height
    Horizontal = [None] * height
    filename_frame = os.listdir(path)
    for name in filename_frame:
        for i in range(width * height):
            img[i] = cv2.imread(f"./examples/bat_test/new{i + 1}/" + name)
        for i in range(height):
            Horizontal[i] = np.hstack(img[width * i: width * (i + 1)])
        Vertical_attachment = np.vstack(Horizontal)
        cv2.imwrite("./examples/collage_batman/" + name, Vertical_attachment)


def main():
    GluingImages("examples/bat_test/new1", 2, 3)


if __name__ == '__main__':
    main()
