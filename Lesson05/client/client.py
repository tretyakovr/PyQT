import sys, logging, log.client_log_config, log.server_log_config
# import service
from service.service import encode_msg, decode_msg, create_socket, get_client_params
from decos import log
from threading import Thread
from start_client import UserNameDialog
from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel , qApp



class ClientVerifier(type):
    pass


class Client(metaclass=ClientVerifier):
    def __init__(self, h, p, u):
        self.host = h
        self.port = p
        self.username = u
        self.socket = self.create_socket()

    def create_socket(self):
        self.socket = create_socket('client--')
        self.socket.settimeout(1)

        return self.socket

    def make_connection(self):
        try:
            self.socket.connect((self.host, self.port))
        except Exception as e:
            log.error(f'Возникла ошибка при установке соединения с сервером {str(e)}')
            sys.exit(1)

    @log
    def append_user(self):
        log.info(f'Регистрация пользователя {self.username} на сервер')
        msg = encode_msg('append_user', self.username, 'server', '')

        if not self.socket.send(msg):
            log.error('Ошибка при отправке сообщения на сервер! Работа программы будет зваершена')
            sys.exit(1)

    @log
    def close_connection(self):
        log.info(f'Закрытие соединения с пользователем {self.username}')
        msg = encode_msg('kill_user', self.username, 'server', '')

        if not self.socket.send(msg):
            log.error('Ошибка при отправке сообщения на сервер! Работа программы будет завершена')
            sys.exit(1)

    @log
    def get_users(self):
        log.info(f'Получение списка пользователей')
        msg = encode_msg('get_users', self.username, 'server', '')

        if not self.socket.send(msg):
            log.error('Ошибка при отправке сообщения на сервер! Работа программы будет завершена')
            sys.exit(1)

    @log
    def send_message(self, to_u, message):
        log.info(f'Отправка сообщения для пользователя {to_u}')
        msg = encode_msg('message', self.username, to_u, message)

        if not self.socket.send(msg):
            log.error('Ошибка при отправке сообщения на сервер! Работа программы будет зваершена')
            sys.exit(1)

    #log
    def read_message(self):
        while True:
            try:
                resp = self.socket.recv(1024)
            except OSError as e:
                pass
            except:
                pass
            else:
                if resp:
                    resp = decode_msg(resp)
                    log.info(f'Получено сообщение от {resp["from_user"]}: {resp["msg"]}')
                    print(f'\nПолучено сообщение от {resp["from_user"]}: {resp["msg"]}')

    @log
    def write_message(self):
        # users_list = ''
        while True:
            cmd = input(
                'Выберите команду: 1 - получить список пользователей, 2 - отправить сообщение, 3 - закрыть соединение: ')

            if cmd == '1':
                self.get_users()

            elif cmd == '2':
                to_user = input('Введите имя получателя сообщения: ')
                message = input('Введите сообщение: ')
                self.send_message(to_user, message)

            elif cmd == '3':
                self.close_connection()
                break

        print('И тут как бы соединение должно закрыться вместе со вторым потоком')


@log
def get_logger():
    l = None
    try:
        l = logging.getLogger('client--')
    except Exception as e:
        print(f'Возникла ошибка при создании логгера {str(e)}')
        sys.exit(1)
    else:
        l.info(f'Логгер успешно создан: {l}')

    return l


if __name__ == '__main__':
    log = get_logger()
    app = QApplication([])
    username = UserNameDialog()
    app.exec_()

    print(username)

    host, port, username = get_client_params(sys.argv, 'client')
    client = Client(host, port, username)
    # socket = client.create_socket()
    client.make_connection()

    # Регистрируем пользователя в списке пользователей на сервере
    client.append_user()
    print('Текущий пользователь: ', username)

    # read_thrd = Thread(target=client--.read_message, args=(client--, socket, username))
    read_thrd = Thread(target=client.read_message, args=())
    read_thrd.start()
    # write_thrd = Thread(target=client--.write_message, args=(client--, socket, username))
    write_thrd = Thread(target=client.write_message, args=())
    write_thrd.start()
