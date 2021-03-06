#! /usr/bin python3
# -*- coding: utf-8 -*-

# from sqlalchemy.orm import sessionmaker
import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QFileDialog
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import Qt
import configparser

import server_db
from server_db import *


class MainApp(QMainWindow):
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

        self.btnStat = QAction(QIcon(''), 'Login history', self)
        self.btnStat.triggered.connect(self.show_stat)

        self.btnMessages = QAction(QIcon(''), 'Messages', self)
        self.btnMessages.triggered.connect(self.show_messages)

        self.btnServerConf = QAction(QIcon(''), 'Server config', self)
        self.btnServerConf.triggered.connect(self.show_serverconf)

        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.setFixedHeight(40)
        self.toolbar.addAction(exitAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btnAllClients)
        self.toolbar.addAction(self.btnStat)
        self.toolbar.addAction(self.btnMessages)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btnServerConf)

        self.show()

    def show_all_clients(self):
        self.label.setText('All users:')
        self.data_model = QStandardItemModel(self)
        self.data_model.setHorizontalHeaderLabels(['id', 'user name', 'start session', 'end session'])

        for item in session.query(Users).all():
            table_item = []
            table_item.append(QStandardItem(str(item.id)))
            table_item.append(QStandardItem(item.name))
            table_item.append(QStandardItem(str(item.start_session)))
            table_item.append(QStandardItem(str(item.end_session)))
            # Вот тут бред, setEditable устанавливать на каждую ячейку. Почему нет setEditable для всего data_model?
            # Или на худой конец - для отдельной строки или колонки?
            for item in table_item:
                item.setEditable(False)
            self.data_model.appendRow(table_item)

        self.table.setModel(self.data_model)
        self.table.resizeColumnsToContents()

    def show_stat(self):
        self.label.setText('Login history:')

        self.data_model = QStandardItemModel(self)
        self.data_model.setHorizontalHeaderLabels(['id', 'user id', 'login datetime', 'ip address', 'port'])

        for item in session.query(LoginHistory).all():
            table_item = []
            table_item.append(QStandardItem(str(item.id)))
            # Сюда нужно подтянуть user_name
            table_item.append(QStandardItem(str(item.user_id)))
            table_item.append(QStandardItem(str(item.login_datetime)))
            table_item.append(QStandardItem(item.ip_address))
            table_item.append(QStandardItem(str(item.port)))
            for item in table_item:
                item.setEditable(False)
            self.data_model.appendRow(table_item)

        self.table.setModel(self.data_model)
        self.table.resizeColumnsToContents()

    def show_messages(self):
        self.label.setText('Messages:')

        self.data_model = QStandardItemModel(self)
        self.data_model.setHorizontalHeaderLabels(['id', 'date time', 'from user id', 'to user id', 'message'])

        for item in session.query(Messages).all():
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

    def show_serverconf(self):
        # Функция обработчик открытия окна выбора папки
        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory() # get any file???
            path = path.replace('/', '\\')
            # self.db_path.insert(path)
            return path

        self.label.setText('Server config:')

        config = configparser.ConfigParser()
        config.read('settings.ini')
        client_host = config['CLIENT']['host']
        client_port = config['CLIENT']['port']
        client_username = config['CLIENT']['username']
        server_hosts = config['SERVER']['hosts']
        server_port = config['SERVER']['port']
        db_filename = config['DATABASE']['db_filename']

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
    sql_engine = server_db.make_engine()
    server_db.create_metadata(sql_engine)

    Session = sessionmaker(bind=sql_engine)
    session = Session()

    app = QApplication(sys.argv)
    main_app = MainApp()
    sys.exit(app.exec_())
