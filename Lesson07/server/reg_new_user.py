from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import Qt


class RegNewUser(QDialog):
    """
    Класс, описывающий окно для регистрации нового пользователя на сервере
    """
    def __init__(self):
        super().__init__()

        self.setFixedSize(350, 240)
        self.setWindowTitle('Регистрация пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.username_label = QLabel('Имя пользователя', self)
        self.username_label.setFixedSize(320, 20)
        self.username_label.move(10, 10)

        self.username_edit = QLineEdit(self)
        self.username_edit.setFixedSize(320, 20)
        self.username_edit.move(10, 40)

        self.userpasswd_label = QLabel('Пароль', self)
        self.userpasswd_label.setFixedSize(320, 20)
        self.userpasswd_label.move(10, 70)

        self.userpasswd_edit = QLineEdit(self)
        self.userpasswd_edit.setEchoMode(QLineEdit.Password)
        self.userpasswd_edit.setFixedSize(320, 20)
        self.userpasswd_edit.move(10, 100)

        self.passwdconfirm_label = QLabel('Подтверждение', self)
        self.passwdconfirm_label.setFixedSize(320, 20)
        self.passwdconfirm_label.move(10, 130)

        self.passwdconfirm_edit = QLineEdit(self)
        self.passwdconfirm_edit.setEchoMode(QLineEdit.Password)
        self.passwdconfirm_edit.setFixedSize(320, 20)
        self.passwdconfirm_edit.move(10, 160)

        self.btn_ok = QPushButton('OK', self)
        self.btn_ok.setFixedSize(100, 40)
        self.btn_ok.move(130, 190)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 40)
        self.btn_cancel.move(240, 190)
        self.btn_cancel.clicked.connect(self.close)
