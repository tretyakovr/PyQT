from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel , qApp
from PyQt5.QtCore import QEvent


# Стартовый диалог с выбором имени пользователя
class UserNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        # self.ok_pressed = False

        self.setWindowTitle('Авторизация')
        self.setFixedSize(400, 100)

        self.label = QLabel('Имя пользователя:', self)
        self.label.move(20, 30)
        # self.label.setFixedSize(150, 10)

        self.client_name = QLineEdit(self)
        self.client_name.move(200, 30)
        self.client_name.setFixedSize(154, 20)

        self.btn_ok = QPushButton('Начать', self)
        self.btn_ok.move(200, 60)
        self.btn_ok.setFixedSize(80, 30)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.move(300, 60)
        self.btn_cancel.setFixedSize(80, 30)
        self.btn_cancel.clicked.connect(qApp.exit)

        self.show()

    # Обработчик кнопки ОК, если поле вводе не пустое, ставим флаг и завершаем приложение.
    def click(self):
        if self.client_name.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    app.exec_()
