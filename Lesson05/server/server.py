import select
import sys, logging, log.client_log_config, log.server_log_config
from service.service import decode_msg, get_server_params, encode_msg, create_socket
from decos import log
from serv_descr import ServerDescr
from server_db import ServerDB


class ServerVerifier(type):
    pass


class Server(metaclass=ServerVerifier):
    hosts = ServerDescr('hosts', str, '')
    port = ServerDescr('port', int, 7777)

    def __init__(self):
        self.hosts = hosts
        self.port = port
        self.server_socket = None
        self.sockets = [] # Список сокетов - подключенных клиентов. Сюда добавляются элементы при установлении
                          # нового соединения
        self.remote_socket = None
        self.address = None
        self.responses = []
        self.read_sockets = []
        self.write_sockets = []
        self.usersdict = {} # Словарь вида {username1: socket1, username2: socket2, ...}
        self.user_session = {}
        self.create_socket()

    def create_socket(self):
        self.server_socket = create_socket('server')
        self.server_socket.bind((self.hosts, self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(0.1)

    # По имени пользователя определяем сокет получателя сообщения
    def get_client_socket(self, username):
        if username in self.usersdict.keys():
            return self.usersdict[username]

        log.info(f'В активных сокетах нет клиента с именем {username}')
        return None

    def accept_connection(self):
        try:
            self.remote_socket, self.address = self.server_socket.accept()
        except OSError as e:
            pass
        else:
            log.info(f'Установлено соединение с {self.remote_socket} {self.address}')
            self.sockets.append(self.remote_socket)

    def exchange_messages(self):
        wait = 5
        self.read_sockets = [] # Список клиентов, читающих сообщения
        self.write_sockets = [] # Список клиентов, отправляющих сообщения
        try:
            self.read_sockets, self.write_sockets, e = select.select(self.sockets, self.sockets, [], wait)
        except Exception as ex:
            print(f'select exception: {ex}')
            pass  # Ничего не делать, если какой-то клиент отключился

    def read_messages(self):
        for client_socket in self.write_sockets:
            try:
                client_socket.settimeout(0.1) # !!! эта строка обязательна!
                data = client_socket.recv(1024)  # Получили сообщение от клиента

            except OSError as e:
                pass  # отвалились по таймауту

            except:
                pass  # не получили сообщение от клиента

            else:
                if data:
                    msg = decode_msg(data)  # Декодировали сообщение от клиента
                    if msg:
                        if msg['action'] == 'append_user':
                            # TODO: вынести в отдельный метод
                            # Добавили username:socket в словарь
                            self.usersdict[msg['from_user']] = client_socket
                            print(self.usersdict)

                            # Добавили в БД пользователя и получили его id
                            id_user, id_session = server_db.append_user(msg['from_user'], self.address[0], self.address[1])
                            self.user_session[msg['from_user']] = id_session

                        elif msg['action'] == 'get_users':
                            # TODO: вынести в отдельный метод
                            # Обрабатываем запрос на получение списка пользователей
                            # UPD: устарело! Было актуально для cli-версии
                            loc_userslist = server_db.get_users_list()
                            self.responses.append({'action': 'userslist',
                                                   'from_user': 'server',
                                                   'to_user': msg['from_user'],
                                                   'message': ', '.join(loc_userslist)})

                        elif msg['action'] == 'get_users_status':
                            # TODO: вынести в отдельный метод
                            # Запрос на получение статуса пользователей (онлайн/офлайн)
                            loc_userslist = msg['userslist'].split(',')
                            loc_online_userslist = []

                            for item in loc_userslist:
                                if server_db.get_user_session(server_db.get_user_id(item)):
                                    loc_online_userslist.append(item)

                            # В ответ отправляем только список online-пользователей
                            self.responses.append({'action': 'get_users_status',
                                                   'from_user': 'server',
                                                   'to_user': msg['from_user'],
                                                   'userslist': ','.join(loc_online_userslist)})

                        elif msg['action'] == 'kill_user':
                            # TODO: вынести в отдельный метод
                            # Прилетел запрос на отключение от {msg["from_user"]}')

                            # Удаляем клиента из self.usersdict
                            del self.usersdict[msg["from_user"]]

                            # Закрываем сессию в Users
                            server_db.close_session(self.user_session[msg['from_user']])

                            # Обнуляем номер сессии в словаре
                            self.user_session[msg['from_user']] = 0

                        elif msg['action'] == 'check_username':
                            # TODO: вынести в отдельный метод
                            # Проверяем существование пользователя на сервере
                            is_user_exists = server_db.check_username(msg['username'])

                            # Формируем ответ
                            self.responses.append({'action': 'check_username',
                                                   'from_user': 'server',
                                                   'to_user': msg['from_user'],
                                                   'username': msg['username'],
                                                   'message': is_user_exists})

                            # Сохраняем сообщение сообщение в БД
                            server_db.append_message(msg['from_user'], msg['to_user'], msg['username'])

                        else:
                            # TODO: вынести в отдельный метод
                            # Обрабатываем обычное сообщение
                            loc_userslist = server_db.get_users_list()
                            if msg['to_user'] in loc_userslist:
                                self.responses.append({'action': 'message',
                                                       'from_user': msg['from_user'],
                                                       'to_user': msg['to_user'],
                                                       'message': msg['message'].upper()})

                                # Сохраняем сообщение в БД
                                server_db.append_message(msg['from_user'], msg['to_user'], msg['message'])
                            else:
                                print(f'В списке активных пользователей не найден {msg["to_user"]}')

    def write_responses(self):
        for response in self.responses:
            client_socket = self.get_client_socket(response['to_user'])
            if client_socket is None:
                print(f'Клиент {response["to_user"]} отвалился, сокет недоступен')
                # TODO: вынести в отдельный метод
                # Удаляем клиента из self.usersdict
                try:
                    del self.usersdict[response['to_user']]
                except:
                    pass

                # Удаляем из self.sockets
                try:
                    self.sockets.remove(client_socket)
                except:
                    pass

                # Закрываем сессию в Users
                server_db.save_user_end_session(response['to_user'])
            else:
                response = encode_msg(response)
                try:
                    client_socket.send(response)

                except:
                    # Фактически здесь exception не срабатывает. Нужно сделать получение от клиента подтверждения о
                    # получении сообщения. Только тогда можно быть уверенным, что сообщение доставлено
                    # Эта ситуация может возникнуть при нештатном завершении сессии клиента
                    # Сокет недоступен, клиент отвалился
                    log.error('Клиент {} {} отключился'.format(client_socket.fileno(), client_socket.getpeername()))
                    print(f'Клиент {response["to_user"]} отвалился, сокет недоступен')
                    client_socket.close()

                    # Удаляем клиента из self.usersdict
                    del self.usersdict[response['to_user']]

                    # Удаляем из self.sockets
                    self.sockets.remove(client_socket)

                    # Закрываем сессию в Users
                    server_db.save_user_end_session(self.db_session, response['to_user'])
                else:
                    # Сообщение успешно отправлено
                    pass

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
    hosts, port, db_filename = get_server_params(sys.argv, 'server')

    server_db = ServerDB(db_filename)

    server = Server()
    server.hosts = hosts
    server.port = port

    while True:
        # Проверяем новые соединения
        server.accept_connection()

        # Ищем "работающие" сокеты
        server.exchange_messages()

        # Читаем сообщения из сокетов
        server.read_messages()  # Получаем сообщения от клиентов

        # Отправляем ответы
        server.write_responses()  # Отправляем полученные сообщения читателям
