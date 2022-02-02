from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel , qApp


# ??? а где эта форма используется???

# Стартовый диалог с выбором имени пользователя
class UserNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        # self.ok_pressed = False

        self.setWindowTitle('Авторизация')
        self.setFixedSize(400, 180)

        self.username_label = QLabel('Имя пользователя:', self)
        self.username_label.move(20, 30)
        self.username_label.setFixedSize(200, 20)

        self.username_edit = QLineEdit(self)
        self.username_edit.move(20, 60)
        self.username_edit.setFixedSize(200, 20)

        self.passwd_label = QLabel('Пароль:', self)
        self.passwd_label.move(20, 90)
        self.passwd_label.setFixedSize(200, 20)

        self.passwd_edit = QLineEdit(self)
        self.passwd_edit.setEchoMode(QLineEdit.Password)
        self.passwd_edit.move(20, 120)
        self.passwd_edit.setFixedSize(200, 20)

        self.btn_ok = QPushButton('Начать', self)
        self.btn_ok.move(200, 150)
        self.btn_ok.setFixedSize(80, 30)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.move(300, 150)
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
