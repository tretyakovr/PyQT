import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QMessageBox
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QColor
import hashlib
import binascii
from service.service import get_server_params, AppConfig
import server_db
from server_db import ServerDB
from reg_new_user import RegNewUser

sys.path.append('../')


class MainApp(QMainWindow):
    """
    Класс описывает основное окно программы GUI-версии серверной части
    """
    def __init__(self, parent=None):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(600, 400)
        self.setWindowTitle('Server conf for chat')

        self.data_model = None

        # Здесь одна метка и одна таблица для всех случаев. Буду переименовывать по ситуации
        self.label = QLabel('', self)
        self.label.setFixedSize(240, 20)
        self.label.move(10, 50)

        self.table = QTableView(self)
        self.table.move(10, 80)
        self.table.setFixedSize(580, 310)

        exitAction = QAction(QIcon(''), 'Завершить работу', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        # В интерфейсе можно сделать отдельную кнопку refresh для обновления списка записей.
        # Здесь повторное нажатие на кнопку на панели инструментов вызовет обновление списка
        self.btnAllClients = QAction(QIcon(''), 'All users', self)
        self.btnAllClients.triggered.connect(self.show_all_clients)

        self.btnStat = QAction(QIcon(''), 'Sessions', self)
        self.btnStat.triggered.connect(self.show_sessions)

        self.btnMessages = QAction(QIcon(''), 'Messages', self)
        self.btnMessages.triggered.connect(self.show_messages)

        self.btnServerConf = QAction(QIcon(''), 'Server config', self)
        self.btnServerConf.triggered.connect(self.show_serverconf)

        self.btnRegNewUser = QAction(QIcon(''), 'Reg new user', self)
        self.btnRegNewUser.triggered.connect(self.reg_new_user)

        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.setFixedHeight(40)
        self.toolbar.addAction(exitAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btnAllClients)
        self.toolbar.addAction(self.btnStat)
        self.toolbar.addAction(self.btnMessages)
        self.toolbar.addAction(self.btnRegNewUser)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btnServerConf)

        self.show()

    def show_all_clients(self):
        """
        Метод формирует и отображает содержимое таблицы Users
        :return:
        """
        self.label.setText('All users:')
        self.data_model = QStandardItemModel(self)
        self.data_model.setHorizontalHeaderLabels(['id', 'user name', 'user password'])

        for item in server_db.session.query(server_db.Users).all():
            table_item = []
            table_item.append(QStandardItem(str(item.id)))
            table_item.append(QStandardItem(item.name))
            table_item.append(QStandardItem(str(item.passwd)))
            # Вот тут бред, setEditable устанавливать на каждую ячейку. Почему нет setEditable для всего data_model?
            # Или на худой конец - для отдельной строки или колонки?
            for item in table_item:
                item.setEditable(False)
            self.data_model.appendRow(table_item)

        self.table.setModel(self.data_model)
        self.table.resizeColumnsToContents()

    def show_sessions(self):
        """
        Метод формирует и отображает содержимое таблицы Sessions
        :return:
        """
        self.label.setText('Sessions')

        self.data_model = QStandardItemModel(self)
        self.data_model.setHorizontalHeaderLabels(['id', 'user id', 'start session', 'ip address', 'port', 'end session'])

        for item in server_db.session.query(server_db.Sessions).all():
            table_item = []
            table_item.append(QStandardItem(str(item.id)))
            # Сюда нужно подтянуть user_name
            table_item.append(QStandardItem(str(item.user_id)))
            table_item.append(QStandardItem(str(item.start_session)))
            table_item.append(QStandardItem(item.ip_address))
            table_item.append(QStandardItem(str(item.port)))
            table_item.append(QStandardItem(str(item.end_session)))
            for item in table_item:
                item.setEditable(False)
            self.data_model.appendRow(table_item)

        self.table.setModel(self.data_model)
        self.table.resizeColumnsToContents()

    def show_messages(self):
        """
        Метод формирует и отображает содержимое таблицы Messages
        :return:
        """
        self.label.setText('Messages:')

        self.data_model = QStandardItemModel(self)
        self.data_model.setHorizontalHeaderLabels(['id', 'date time', 'from user id', 'to user id', 'message'])

        for item in server_db.session.query(server_db.Messages).all():
            table_item = []
            table_item.append(QStandardItem(str(item.id)))
            # Сюда нужно подтянуть user_name
            table_item.append(QStandardItem(str(item.mdatetime)))
            table_item.append(QStandardItem(str(item.from_user_id)))
            table_item.append(QStandardItem(str(item.to_user_id)))
            table_item.append(QStandardItem(item.message))
            for item in table_item:
                item.setEditable(False)
            self.data_model.appendRow(table_item)

        self.table.setModel(self.data_model)
        self.table.resizeColumnsToContents()

    def reg_new_user(self):
        """
        Метод вызывает диалоговое окно для регистрации новго пользователя на сервере
        :return:
        """
        global select_dialog
        create_user_dialog = RegNewUser()
        create_user_dialog.btn_ok.clicked.connect(lambda: self.create_new_user(create_user_dialog))
        create_user_dialog.show()

    def create_new_user(self, dialog):
        """
        Метод проверяет корректность данных, введенных в окне регистрации нового пользователя,
        хэширует пароль и сохраняет данные в таблицу Users
        :param dialog: Экземпляр диалогового окна
        :return:
        """
        # Берем из диалога имя пользователя, пароль, подтверждение пароля
        username = dialog.username_edit.text()
        userpasswd = dialog.userpasswd_edit.text()
        passwdconfirm = dialog.passwdconfirm_edit.text()

        if username == '' or userpasswd == '' or passwdconfirm == '':
            QMessageBox.information(self, 'Ошибка!', 'Ошибка при вводе данных! Одно или более полей не заполнены!',
                                    QMessageBox.Ok,
                                    QMessageBox.Ok)
        elif userpasswd != passwdconfirm:
            QMessageBox.information(self, 'Ошибка!', 'Ошибка при вводе данных! Пароль и подтверждение не совпадают!',
                                    QMessageBox.Ok,
                                    QMessageBox.Ok)
            # Вызываем метод, который отправит сообщение на сервер - проверить существование такого пользователя
        elif server_db.check_username(username):
            QMessageBox.information(self, 'Ошибка!', 'Пользователь с указанным именем на сервере уже существует!',
                                    QMessageBox.Ok,
                                    QMessageBox.Ok)
        else:
            # Генерируем хэш пароля, в качестве соли будем использовать логин в
            # нижнем регистре.
            userpasswd = userpasswd.encode('utf-8')
            salt = username.lower().encode('utf-8')
            passwd_hash = hashlib.pbkdf2_hmac('sha512', userpasswd, salt, 100000)
            server_db.reg_new_user(username, binascii.hexlify(passwd_hash))
            QMessageBox.information(self, 'Информация!', 'Пользователь успешно зарегистрирован!',
                                    QMessageBox.Ok,
                                    QMessageBox.Ok)

        # Закрываем диалоговое окно
        dialog.close()

    def show_serverconf(self):
        """
        Метод описывает содержимое окна для ввода параметров приложения
        :return:
        """
        # Функция обработчик открытия окна выбора папки
        # def open_file_dialog():
        #     global dialog
        #     dialog = QFileDialog(self)
        #     path = dialog.getExistingDirectory() # get any file???
        #     path = path.replace('/', '\\')
        #     self.db_path.insert(path)
        # return path

        self.label.setText('Server config:')

        config = AppConfig()
        client_host = config.client_host
        client_port = config.client_port
        client_username = config.client_username
        server_hosts = config.server_hosts
        server_port = config.server_port
        db_filename = config.db_filename

        self.data_model = QStandardItemModel(self)
        self.data_model.setHorizontalHeaderLabels(['param name', 'param value'])

        table_item = []
        cell = QStandardItem('[DATABASE]')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        cell = QStandardItem('')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        self.data_model.appendRow(table_item)

        table_item = []
        cell = QStandardItem('db_filename')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        cell = QStandardItem(db_filename)
        cell.setEditable(True)
        table_item.append(cell)
        self.data_model.appendRow(table_item)
        # И вот тут бы отловить click(), чтобы вызвать диалог выбора файла...

        table_item = []
        cell = QStandardItem('[SERVER]')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        cell = QStandardItem('')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        self.data_model.appendRow(table_item)

        table_item = []
        cell = QStandardItem('hosts')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        cell = QStandardItem(server_hosts)
        cell.setEditable(True)
        table_item.append(cell)
        self.data_model.appendRow(table_item)

        table_item = []
        cell = QStandardItem('port')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        cell = QStandardItem(server_port)
        cell.setEditable(True)
        table_item.append(cell)
        self.data_model.appendRow(table_item)

        table_item = []
        cell = QStandardItem('[CLIENT]')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        cell = QStandardItem('')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        self.data_model.appendRow(table_item)

        table_item = []
        cell = QStandardItem('host')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        cell = QStandardItem(client_host)
        cell.setEditable(True)
        table_item.append(cell)
        self.data_model.appendRow(table_item)

        table_item = []
        cell = QStandardItem('port')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        cell = QStandardItem(client_port)
        cell.setEditable(True)
        table_item.append(cell)
        self.data_model.appendRow(table_item)

        table_item = []
        cell = QStandardItem('username')
        cell.setEditable(False)
        cell.setBackground(QColor('lightGray'))
        table_item.append(cell)
        cell = QStandardItem(client_username)
        cell.setEditable(True)
        table_item.append(cell)
        self.data_model.appendRow(table_item)

        self.table.setModel(self.data_model)
        self.table.setColumnWidth(1, 400)


if __name__ == '__main__':
    hosts, port, db_filename = get_server_params(sys.argv, 'server')
    server_db = ServerDB(db_filename)

    app = QApplication(sys.argv)
    main_app = MainApp()
    sys.exit(app.exec_())
