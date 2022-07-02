import cv2
import os


def crop_imgs(path_in, path_out, n_w, n_h):
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
                crop_img = img[y:y + h, x:x + w]
                if not os.path.exists(path_out + str(count)):
                    os.makedirs(path_out + str(count))
                cv2.imwrite(path_out + str(count) + "/" + name, crop_img)
                count += 1


crop_imgs("./examples/batman/batman", "examples/i/", 4, 4)
