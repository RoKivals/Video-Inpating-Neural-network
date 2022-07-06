import numpy as np
import os
import cv2
from PIL import Image


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
    print(f'Finish test! The result video is saved in: {final_path}.')
