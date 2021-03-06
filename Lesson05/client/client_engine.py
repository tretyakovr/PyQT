import sys
import threading
import time
from socket import *
from PyQt5.QtCore import pyqtSignal, QObject
from service.service import encode_msg, decode_msg
from decos import log
import logging


socket_lock = threading.Lock()


class ClientEngine(threading.Thread, QObject):
    # Здесь описания сигналов, по которым будут генериться реакции, правильно?
    new_user = pyqtSignal()
    user_not_exist = pyqtSignal()
    new_message = pyqtSignal()
    update_users_status = pyqtSignal()

    def __init__(self, host, port, client_db, username):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.host = host
        self.port = port
        self.client_db = client_db
        self.username = username
        self.user_id = self.client_db.get_user_id(self.username)
        self.online_userslist = []

        self.logger_name = 'client'
        self.get_logger()

        self.socket = self.create_socket()
        self.make_connection()

        self.register_user_on_server()
        self.running = True

    @log
    def get_logger(self):
        self.logger = None
        try:
            self.logger = logging.getLogger(self.logger_name)
        except Exception as e:
            print(f'Возникла ошибка при создании логгера {str(e)}')
            sys.exit(1)
        else:
            self.logger.info(f'Логгер успешно создан: {self.logger}')

    @log
    def create_socket(self):
        s = None
        try:
            s = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
        except Exception as e:
            self.logger.error(f'Ошибка при создании сокета {str(e)}')
            sys.exit(1)
        else:
            self.logger.info(f'Сокет успешно создан: {s}')

        return s

    @log
    def make_connection(self):
        try:
            self.socket.connect((self.host, self.port))
        except Exception as e:
            self.logger.error(f'Возникла ошибка при установке соединения с сервером {str(e)}')
            sys.exit(1)

    @log
    def send_message(self, msg):
        # Принудительно делаем секундную паузу, так как при старте клиента в сокет летят сразу два сообщения
        # и сервер падает. Вероятно, нужно делать очередь на отправку сообщений по аналогии с responses у сервера
        # time.sleep(1)
        with socket_lock:
            self.socket.settimeout(0.5)
            if not self.socket.send(msg):
                self.logger.error('Ошибка при отправке сообщения на сервер! Работа программы будет зваершена')
                sys.exit(1)
            # self.receive_answer()
            # self.process_server_ans(get_message(self.transport))
            self.logger.info(f'Отправлено сообщение на сервер')

    @log
    def register_user_on_server(self):
        self.logger.info(f'Регистрация пользователя {self.username} на сервере')
        msg = encode_msg({'action': 'append_user', 'from_user': self.username, 'to_user': 'server'})
        self.send_message(msg)

    @log
    def prepare_message_to_send(self, from_user, to_user, message):
        self.logger.info(f'Отправка сообщения пользователю {to_user}')
        msg = encode_msg({'action': 'message', 'from_user': from_user, 'to_user': to_user, 'message': message})
        self.send_message(msg)

    @log
    def read_message(self):
        resp = None
        try:
            resp = self.socket.recv(1024)
        except Exception:
            pass
        else:
            if resp:
                resp = decode_msg(resp)
                self.logger.info(resp)

        return resp

    @log
    def check_username(self, username):
        # Вызывается при добавлении нового пользователя
        self.logger.info(f'Проверка существования пользователя')
        msg = encode_msg({'action': 'check_username', 'from_user': self.username, 'to_user': 'server', 'username': username})
        self.send_message(msg)

    @log
    def get_users_status(self, userslist):
        self.logger.info(f'Получение статуса пользователя (онлайн/офлайн)')
        msg = encode_msg({'action': 'get_users_status', 'from_user': self.username, 'to_user': 'server', 'userslist': userslist})
        self.send_message(msg)

    @log
    def parse_message(self, msg):
        # Потрошим сообщение
        if msg['action'] == 'check_username':
            # Ответ на запрос проверки существования пользователя
            if msg['message']:
                self.logger.info(f'Успешная проверка пользователя {msg["username"]}')

                # Добавяляем пользователя в локальную БД
                self.client_db.append_user(msg['username'])

                # И генерим событие, по которому обновится список известных пользователей
                self.new_user.emit()
            else:
                # Такого пользователя на сервере не существует
                # Генерим событие, чтобы отобразить messagebox. Отсюда messagebox вызвать не можем
                self.user_not_exist.emit()

        elif msg['action'] == 'get_users_status':
            # Получили ответ на запрос о статусе клиентов
            self.online_userslist = msg['userslist'].split(',')

            # Генерим событие
            self.update_users_status.emit()

        elif msg['action'] == 'message':
            # Обычное сообщение
            # Проверяем существование и добавляем пользователя в known_users
            self.client_db.append_user(msg['from_user'])

            # Сохраняем сообщение в локальную базу
            self.client_db.append_message(msg['from_user'], 1, msg['message'])

            # Генерим событие, чтобы обновить список сообщений в окне
            self.new_message.emit()

    @log
    def run(self):
        self.logger.info('Запущен процесс - приёмник собщений с сервера.')
        while self.running:
            # Отдыхаем секунду и снова пробуем захватить сокет.
            # если не сделать тут задержку, то отправка может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with socket_lock:
                self.socket.settimeout(0.5)
                message = self.read_message()
                if message:
                    self.logger.info(f'Принято сообщение с сервера: {message}')
                    self.parse_message(message)

    def engine_shutdown(self):
        self.running = False
        msg = encode_msg({'action': 'kill_user', 'from_user': self.username, 'to_user': 'server'})
        self.send_message(msg)

        self.logger.debug('Транспорт завершает работу.')
        time.sleep(0.5)
