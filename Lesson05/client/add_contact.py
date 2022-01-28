from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import Qt


# Диалог ввода имени пользователя для добавления
# Максимально облегченный модуль, только поле для ввода имени пользователя.
# Намеренно не делаю выпадающий список, так как, если на сервере количество пользователей > 20,
# выпадающий список будет неудобным для использования
class AddContactDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setFixedSize(350, 120)
        self.setWindowTitle('Добавление контакта')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.username_label = QLabel('Имя пользователя', self)
        self.username_label.setFixedSize(320, 20)
        self.username_label.move(10, 10)

        self.username_edit = QLineEdit(self)
        self.username_edit.setFixedSize(320, 20)
        self.username_edit.move(10, 40)

        self.btn_find = QPushButton('Найти', self)
        self.btn_find.setFixedSize(100, 40)
        self.btn_find.move(130, 70)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 40)
        self.btn_cancel.move(240, 70)
        self.btn_cancel.clicked.connect(self.close)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = AddContactDialog()
#     window.show()
#     app.exec_()
