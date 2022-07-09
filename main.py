import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий

import start
from PyQt5 import QtWidgets
import design  # Это наш конвертированный файл дизайна


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):

        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.pushButton_start.clicked.connect(self.func_start)
        self.pushButton_fileinput.clicked.connect(self.func_fileinput)
        self.pushButton_fileoutput.clicked.connect(self.func_fileoutput)
        self.pushButton_maskinput.clicked.connect(self.func_maskinput)

    def func_fileinput(self):

        self.lineEdit_fileinput.clear()

        if self.radioButton_frames_for_video.isChecked():
            directory_fileinput = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        else:
            directory_fileinput = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите файл", filter="Video (*.mp4)")[0]

        if directory_fileinput:
            print(directory_fileinput)
            self.lineEdit_fileinput.setText(directory_fileinput)

    def func_fileoutput(self):
        fileoutput = QtWidgets.QFileDialog.getSaveFileName(self, "Выберите файл", filter="Video (*.mp4)")[0]
        if fileoutput:
            self.lineEdit_fileoutput.setText(fileoutput)

    def func_maskinput(self):
        self.lineEdit_maskinput.clear()
        if self.radioButton_frames_for_mask.isChecked():
            directory_maskinput = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        else:
            directory_maskinput = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите файл", filter="Video (*.mp4)")[0]

        if directory_maskinput:
            self.lineEdit_maskinput.setText(directory_maskinput)

    def func_start(self):
        if self.lineEdit_fileinput.text() == "":
            text = "Error: заполните FILEINPUT"
            self.error(text)
        elif self.lineEdit_fileoutput.text() == "":
            text = "Error: заполните FILEOUTPUT"
            self.error(text)
        elif self.lineEdit_maskinput.text() == "":
            text = "Error: заполните MASKINPUT"
            self.error(text)
        else:
            try:
                self.error("")
                video_out = "/".join(self.lineEdit_fileoutput.text().split("/")[:-1])
                print(video_out)
                fin_name = self.lineEdit_fileoutput.text().split("/")[-1]
                # TODO: в gui замутить считывание имени для результата и добавить его передачу в 63 строку
                args = Args()
                args.setup(self.lineEdit_fileinput.text(), self.lineEdit_maskinput.text(), video_out,
                           int(self.spinBox_step.text()), int(self.spinBox_neighbor.text()), int(self.spinBox_height.text()),
                           int(self.spinBox_width.text()), int(self.spinBox_crop_height.text()), int(self.spinBox_crop_width.text()),
                           int(self.spinBox_crop_overlap.text()), self.radioButton_use_mp4_for_video.isChecked(),
                           self.radioButton_use_mp4_for_mask.isChecked(), int(self.spinBox_FPS.text()), fin_name)
                start.Cycle(args, self)
                self.error("Красава ебать у тебя получилось")
            except BaseException as er:
                text = "Error"
                self.error(text)

    def error(self, text):
        self.label_error.setText(text)


class Args:
    def __init__(self):
        self.video = None  # str
        self.mask = None  # str
        self.ckpt = "release_model/E2FGVI-HQ-CVPR22.pth"  # str
        self.step = None
        self.video_out = None
        self.neighbor_stride = None  # int
        self.width = None  # int
        self.height = None  # int
        self.tmp_vpath = "./Temp/V"
        self.tmp_mpath = "./Temp/V_mask"
        self.h_cuts = None
        self.w_cuts = None
        self.overlap = None
        self.number = None  # int
        self.model = "e2fgvi_hq"  # str
        self.num_ref = -1  # int
        self.mp4v = None
        self.mp4m = None
        self.fps = None
        self.final_name = None
        self.set_size = None  # bool

    def setup(self, video: str, mask: str, video_out: str, step: int, neighbor_stride: int, height: int, width: int, h_cuts: int, w_cuts: int,
              overlap: int, mp4v: bool, mp4m: bool, fps: int, fin_name: str):
        self.video = video
        self.mask = mask
        self.video_out = video_out
        self.step = step
        self.neighbor_stride = neighbor_stride
        self.height = height
        self.width = width
        self.h_cuts = h_cuts
        self.w_cuts = w_cuts
        self.overlap = overlap
        self.mp4v = mp4v
        self.mp4m = mp4m
        self.fps = fps
        self.final_name = fin_name
        self.number = w_cuts * h_cuts


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()# Создаём объект класса ExampleApp # Показываем окно
    window.show()
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
