#! /usr/bin python3
# -*- coding: utf-8 -*-

from socket import *
import select
import sys, logging, log.client_log_config, log.server_log_config
from service import decode_msg, create_socket, parse_server_params, encode_msg
from decos import log
from serv_descr import ServerDescr


class ServerVerifier(type):
    pass


class Server(metaclass=ServerVerifier):
    hosts = ServerDescr('hosts', str, '')
    port = ServerDescr('port', int, 7777)

    # def __init__(self, h, p):
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
    # print('Server descr: ', server.hosts, server.port)
    print(server.__dict__)
    # А здесь мы можем установить параметры hosts и port значениями из командной строки?
    server.hosts = hosts
    server.port = port
    socket = server.create_socket()

    while True:
        server.accept_connection()
        server.exchange_messages()
