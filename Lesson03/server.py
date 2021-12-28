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


class ServerVerifier(type):
    pass


class Server(metaclass=ServerVerifier):
    hosts = ServerDescr('hosts', str, '')
    port = ServerDescr('port', int, 7777)

    def __init__(self):
        self.hosts = hosts
        self.port = port
        self.socket = None
        self.clients = [] # Список сокетов - подключенных клиентов. Сюда добавляются элементы при установлении
                          # нового соединения
        self.remote_socket = None
        self.address = None
        self.responses = []
        self.read_sockets = []
        self.write_sockets = []
        self.userslist = []

    def create_socket(self):
        self.socket = create_socket('server')
        self.socket.bind((self.hosts, self.port))
        self.socket.listen(5)
        self.socket.settimeout(1)

        return self.socket

    def accept_connection(self):
        try:
            self.remote_socket, self.address = self.socket.accept()
        except OSError as e:
            pass
        else:
            log.info(f'Установлено соединение с {self.remote_socket} {self.address}')
            print(f'Установлено соединение с {self.remote_socket} {self.address}')
            self.clients.append(self.remote_socket)

    def get_username(self, client):
        res = ''
        for i in self.userslist:
            if i['socket'] == client:
                res = i['username']
                break

        # print(res)
        return i['username']

    def exchange_messages(self):
        wait = 5
        self.read_sockets = [] # Список клиентов, читающих сообщения
        self.write_sockets = [] # Список клиентов, отправляющих сообщения
        try:
            self.read_sockets, self.write_sockets, e = select.select(self.clients, self.clients, [], wait)
        except Exception as ex:
            print(f'select exception: {ex}')
            pass  # Ничего не делать, если какой-то клиент отключился

        self.read_messages()  # Получаем сообщения от клиентов
        if self.responses:
            self.write_responses()  # Отправляем полученные сообщения читателям

    def read_messages(self):
        for socket in self.write_sockets:
            try:
                socket.settimeout(2) # !!! эта строка обязательна!
                data = socket.recv(1024)  # Получили сообщение от клиента
                # print(data)

            except OSError as e:
                pass  # отвалились по таймауту

            except:
                pass  # не получили сообщение от клиента

            else:
                if data:
                    msg = decode_msg(data)  # Декодировали сообщение от клиента
                    if msg:
                        if msg['action'] == 'append_user':
                            self.userslist.append({'username': msg['from_user'], 'socket': socket})

                        elif msg['action'] == 'get_users':
                            print(f'Прилетел запрос на получение списка пользователей от {msg["from_user"]}')
                            users_list = ', '.join([user['username'] for user in self.userslist])

                            self.responses.append({'client': socket,
                                                   'from_user': 'server',
                                                   'to_user': msg['from_user'],
                                                   'message': users_list})

                        elif msg['action'] == 'kill_user':
                            print(f'Прилетел запрос на отключение от {msg["from_user"]}')
                            # Удаляем сокет из self.socket и клиента из userslist
                            for index, user in enumerate(self.userslist):
                                if user['username'] == msg['from_user']:
                                    self.clients.remove(user['socket'])
                                    self.userslist.remove(user)
                                    break

                        else:
                            print(f'Прилетело сообщение от {msg["from_user"]} для {msg["to_user"]}')
                            users_list = ', '.join([user['username'] for user in self.userslist])
                            if msg['to_user'] in users_list:
                                self.responses.append({'client': socket,
                                                       'from_user': msg['from_user'],
                                                       'to_user': msg['to_user'],
                                                       'message': msg['msg'].upper()})
                            else:
                                print(f'В списке активных пользователей не найден {msg["to_user"]}')

    def write_responses(self):
        for response in self.responses:
            socket = None
            # Определяем сокет получателя сообщения
            for user in self.userslist:
                if user['username'] == response['to_user']:
                    socket = user['socket']
                    break

            response = encode_msg('message', response['from_user'], response['to_user'], response['message'])
            try:
                socket.send(response)

            except OSError as e:
                pass

            except:
                # Сокет недоступен, клиент отвалился
                log.error('Клиент {} {} отключился'.format(socket.fileno(), socket.getpeername()))
                socket.close()
                self.clients.remove(socket)

        # Отправили все сообщения из списка, список очистили
        self.responses.clear()


@log
def get_logger():
    l = None
    try:
        l = logging.getLogger('server')
    except Exception as e:
        print(f'Возникла ошибка при создании логгера {str(e)}')
        sys.exit(1)
    else:
        l.info(f'Логгер успешно создан: {l}')

    return l


if __name__ == '__main__':
    log = get_logger()
    hosts, port = parse_server_params(sys.argv, 'server')

    # При этом вызове значения hosts и port будут установлены дефолтными значениями и проверены дескриптором?
    server = Server()
    # print(server.__dict__)
    # print(server.__dir__())
    # А здесь мы можем установить параметры hosts и port значениями из командной строки?
    server.hosts = hosts
    server.port = port
    socket = server.create_socket()

    # try:
    #     sql_connection = sqlite3.connect('chat.sqlite')
    # except Exception as e:
    #     print(e)

    try:
        sql_engine = create_engine('sqlite:///chat.sqlite', pool_recycle=3600)
    except Exception as e:
        print(e)

    metadata = MetaData()
    users = Table('users', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('name', String, nullable=False, unique=True),
                  Column('last_login_time', DateTime))

    login_history = Table('login_history', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('user_id', Integer),
                          Column('login_datetime', DateTime(), default=datetime.now),
                          Column('ip_address', String),
                          Column('port', Integer))

    active_users = Table('active_users', metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user_id', Integer),
                         Column('ip_address', String),
                         Column('port', Integer),
                         Column('login_datetime', DateTime(), default=datetime.now))

    metadata.create_all(sql_engine)

    while True:
        server.accept_connection()
        server.exchange_messages()
