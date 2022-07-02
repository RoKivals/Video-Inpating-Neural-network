import numpy as np
import os
import cv2
from PIL import Image


def main():
    path = 'examples/collage_batman'
    lst = os.listdir(path)
    lst = sorted(lst, key=lambda x: int(x[0:-4]))
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
    save_path = os.path.join(res_dir, 'anime.mp4')
    writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*"mp4v"), 23, (1920, 1080))
    for f in range(video_length):
        comp = comp_frames[f].astype(np.uint8)
        writer.write(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
    writer.release()
    print(f'Finish test! The result video is saved in: {save_path}.')

