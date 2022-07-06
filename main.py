import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий

import start
from PyQt5 import QtWidgets

import design  # Это наш конвертированный файл дизайна


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.pushButton_start.clicked.connect(self.func_start)
        self.pushButton_fileinput.clicked.connect(self.func_fileinput)
        self.pushButton_fileoutput.clicked.connect(self.func_fileoutput)
        self.pushButton_maskinput.clicked.connect(self.func_maskinput)

    def func_fileinput(self):
        self.lineEdit_fileinput.clear()  # На случай, если в списке уже есть элементы
        directory_fileinput = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории

        if directory_fileinput:  # не продолжать выполнение, если пользователь не выбрал директорию
            print(directory_fileinput)
            self.lineEdit_fileinput.setText(directory_fileinput)

    def func_fileoutput(self):
        self.lineEdit_fileoutput.clear()  # На случай, если в списке уже есть элементы
        directory_fileoutput = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории

        if directory_fileoutput:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.lineEdit_fileoutput.setText(directory_fileoutput)

    def func_maskinput(self):
        self.lineEdit_maskinput.clear()  # На случай, если в списке уже есть элементы
        directory_maskinput = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории

        if directory_maskinput:  # не продолжать выполнение, если пользователь не выбрал директорию
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
                self.error()
                start.cycle(self.lineEdit_fileinput.text(), self.lineEdit_fileoutput.text(), self.lineEdit_maskinput.text(), self.spinBox_step.text(),
                            self.spinBox_neighbor.text())
                self.error("Красава ебать у тебя получилось")
            except BaseException as er:
                text = "Error"
                self.error(text)

    def error(self, text):
        self.label_error.setText(text)


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
