#! /usr/bin python3
# -*- coding: utf-8 -*-

from socket import *
import select
import sys, logging, log.client_log_config, log.server_log_config
from service import decode_msg, create_socket, parse_server_params, encode_msg
from decos import log
from serv_descr import ServerDescr
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, DateTime, String, MetaData, ForeignKey
from datetime import datetime
from sqlalchemy.orm import mapper
from PyQt5.QtWidgets import QApplication, QWidget, QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, uic


class User:
    def __init__(self, id, name, last_login_time):
        self.id = id
        self.name = name
        self.last_login_time = last_login_time

    def __repr__(self):
        return f'User: {self.name}, last_login: {self.last_login_time}'


class LoginHistory:
    def __init__(self, id, user_id, login_datetime, ip_address, port):
        self.id = id
        self.user_id = user_id
        self.login_datetime = login_datetime
        self.ip_address = ip_address
        self.port = port

    def __repr__(self):
        return f'User_id: {self.user_id}, login_datetime: {self.login_datetime}'


class ActiveUsers:
    def __init__(self, id, user_id, ip_address, port, login_datetime):
        self.id = id
        self.user_id = user_id
        self.ip_address = ip_address
        self.port = port
        self.login_datetime = login_datetime

    def __repr__(self):
        return f'User_id: {self.user_id}, ip address: {self:ip_address}, port: {port}'


class MainApp(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        uic.loadUi('MainWindow.ui', self)

        self.actionQuit.triggered.connect(QtWidgets.qApp.quit)
        # self.actionClientList.triggered.connect()

if __name__ == '__main__':
    # log = get_logger()
    # hosts, port = parse_server_params(sys.argv, 'server')

    # При этом вызове значения hosts и port будут установлены дефолтными значениями и проверены дескриптором?
    # server = Server()
    # print(server.__dict__)
    # print(server.__dir__())
    # А здесь мы можем установить параметры hosts и port значениями из командной строки?
    # server.hosts = hosts
    # server.port = port
    # socket = server.create_socket()

    # try:
    #     sql_connection = sqlite3.connect('chat.sqlite')
    # except Exception as e:
    #     print(e)

    try:
        sql_engine = create_engine('sqlite:///server.sqlite', pool_recycle=3600)
    except Exception as e:
        print(e)

    metadata = MetaData()
    users = Table('users', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('name', String, nullable=False, unique=True),
                  Column('last_login_time', DateTime))

    login_history = Table('login_history', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('user_id', ForeignKey('users.id')),
                          Column('login_datetime', DateTime(), default=datetime.now),
                          Column('ip_address', String),
                          Column('port', Integer))

    active_users = Table('active_users', metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user_id', ForeignKey('users.id')),
                         Column('ip_address', String),
                         Column('port', Integer),
                         Column('login_datetime', DateTime(), default=datetime.now))

    metadata.create_all(sql_engine)

    mapper(User, users)
    mapper(LoginHistory, login_history)
    mapper(ActiveUsers, active_users)

    # app = QApplication(sys.argv)
    # main_window = QWidget()
    # main_window.resize(300, 200)
    # main_window.move(100, 100)
    # main_window.setWindowTitle('Server app for chat')
    #
    # exitAction = QAction(QIcon('exit.png'), 'Exit', self)
    # exitAction.setShortcut('Ctrl+Q')
    # exitAction.triggered.connect(qApp.quit)
    #
    # main_window.show()

    # main_app = QtWidgets.QApplication(sys.argv)
    # window = uic.loadUi('MainWindow.ui')
    # window.actionQuit.triggered.connect(main_app.quit)
    # window.btnQuit.clicked.connect(app.quit)
    # window.show()
    # sys.exit(main_app.exec_())

    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


    # while True:
    #     server.accept_connection()
    #     server.exchange_messages()

    # sys.exit(app.exec_())
