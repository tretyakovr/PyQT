from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QLineEdit, qApp
from PyQt5.QtCore import Qt


# Ввод имени пользователя при старте приложения
class GetUserName(QDialog):
    """
    Класс, описывающий окно для ввода имени пользователя и пароля при старте приложения
    """
    def __init__(self):
        super().__init__()

        self.setFixedSize(350, 190)
        self.setWindowTitle('Авторизация')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.username_label = QLabel('Имя пользователя', self)
        self.username_label.move(10, 10)
        self.username_label.setFixedSize(320, 20)

        self.username_edit = QLineEdit(self)
        self.username_edit.move(10, 40)
        self.username_edit.setFixedSize(320, 20)

        self.passwd_label = QLabel('Пароль', self)
        self.passwd_label.move(10, 70)
        self.passwd_label.setFixedSize(320, 20)

        self.passwd_edit = QLineEdit(self)
        self.passwd_edit.setEchoMode(QLineEdit.Password)
        self.passwd_edit.move(10, 100)
        self.passwd_edit.setFixedSize(320, 20)

        self.btn_ok = QPushButton('OK', self)
        self.btn_ok.move(130, 130)
        self.btn_ok.setFixedSize(100, 40)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.move(240, 130)
        self.btn_cancel.setFixedSize(100, 40)
        self.btn_cancel.clicked.connect(qApp.exit)

        # Нужно добавить обработу нажатия клавиши Esc

        self.show()

    # Обработчик кнопки ОК, если поле вводе не пустое, ставим флаг и завершаем приложение.
    def click(self):
        # TODO: по клавише Esc получаем сообщение об ошибке. Нужно искать решение
        # Traceback (most recent call last): File
        # "...client/client.py", line 22, in < module >
        # if username_dlg.ok_pressed: RuntimeError: wrapped C / C + + object of type GetUserName has been deleted
        if self.username_edit.text():
            self.ok_pressed = True
            qApp.exit()
