import sys, logging, log.client_log_config, log.server_log_config
# import service
from service import encode_msg, decode_msg, create_socket, parse_client_params
from decos import log
from threading import Thread


@log
def make_connection(s, h, p):
    try:
        s.connect((h, p))
    except Exception as e:
        log.error(f'Возникла ошибка при установке соединения с сервером {str(e)}')
        sys.exit(1)


@log
def close_connection(s, u):
    log.info(f'Закрытие соединения с пользователем {u}')
    msg = encode_msg('kill_user', u, 'server', '')

    if not s.send(msg):
        log.error('Ошибка при отправке сообщения на сервер! Работа программы будет зваершена')
        sys.exit(1)


@log
def get_logger():
    l = None
    try:
        l = logging.getLogger('client')
    except Exception as e:
        print(f'Возникла ошибка при создании логгера {str(e)}')
        sys.exit(1)
    else:
        l.info(f'Логгер успешно создан: {l}')

    return l


@log
def read_message(s, u):
    while True:
        resp = s.recv(1024)
        if resp:
            resp = decode_msg(resp)
            log.info(f'Получено сообщение от {resp["from_user"]}: {resp["msg"]}')
            print(f'\nПолучено сообщение от {resp["from_user"]}: {resp["msg"]}')


@log
def write_message(s, u):
    users_list = ''
    while True:
        cmd = int(input(
            'Выберите команду: 1 - получить список пользователей, 2 - отправить сообщение, 3 - закрыть соединение: '))
        if cmd not in [1, 2, 3]:
            continue

        if cmd == 1:
            get_users(s, u)

        elif cmd == 2:
            to_user = input('Введите имя получателя сообщения: ')
            message = input('Введите сообщение: ')
            send_message(s, u, to_user, message)

        elif cmd == 3:
            close_connection(s, u)
            break


@log
def append_user(s, u):
    log.info(f'Регистрация пользователя {u} на сервер')
    msg = encode_msg('append_user', u, 'server', '')

    if not s.send(msg):
        log.error('Ошибка при отправке сообщения на сервер! Работа программы будет зваершена')
        sys.exit(1)


# @log
def get_users(s, u):
    log.info(f'Получение списка пользователей')
    msg = encode_msg('get_users', u, 'server', '')

    if not s.send(msg):
        log.error('Ошибка при отправке сообщения на сервер! Работа программы будет зваершена')
        sys.exit(1)


def send_message(s, u, to_u, message):
    log.info(f'Отправка сообщения для пользователя {to_u}')
    msg = encode_msg('message', u, to_u, message)

    if not s.send(msg):
        log.error('Ошибка при отправке сообщения на сервер! Работа программы будет зваершена')
        sys.exit(1)


if __name__ == '__main__':
    log = get_logger()
    if log:
        host, port, username = parse_client_params(sys.argv)
        log.info(f'Определены параметры командной строки: host = {host}, port = {port}, username = {username}')

        if host is None or port is None or username is None:
            log.critical(f'Некорректные параметры командной строки: {sys.argv}')
            sys.exit(1)
        else:
            socket = create_socket('client')
            make_connection(socket, host, port)

            # Регистрируем пользователя в списке пользователей на сервере
            append_user(socket, username)
            print('Текущий пользователь: ', username)

            read_thrd = Thread(target=read_message, args=(socket, username))
            read_thrd.start()
            write_thrd = Thread(target=write_message, args=(socket, username))
            write_thrd.start()
