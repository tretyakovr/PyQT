#! /usr/bin python3
# -*- coding: utf-8 -*-

from socket import *
import select
import sys, logging, log.client_log_config, log.server_log_config
from service import decode_msg, create_socket, encode_reply, parse_server_params, encode_msg
from decos import log

USERSLIST = []

@log
def send_msg(c, m):
    m = encode_reply(m)
    c.send(m)


@log
def exchange_msg(c):
    while True:
        msg = c.recv(1024)
        msg = decode_msg(msg)
        log.info(f'Получено сообщение от клиента: {msg["message"]}')
        send_msg(c, 'Уведомление об успешном получении сообщения')

        if msg['action'] == 'quit':
            break


@log
def close_connection(c):
    log.info('Останавливаем сервер')
    c.close()
    log.info('Свервер остановлен')


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


def read_messages(w_sockets, all_clients):
    responses = []  # Список ответов на сообщения

    for socket in w_sockets:
        try:
            data = socket.recv(4096)  # Получили сообщениеот клиента

        except OSError as e:
            pass # отвалились по таймауту

        except:
            pass # не получили сообщение от клиента

        else:
            if data:
                msg = decode_msg(data) # Декодировали сообщение от клиента
                if msg['action'] == 'append_user':
                    USERSLIST.append({'username': msg['from_user'], 'socket': socket})

                elif msg['action'] == 'get_users':
                    print(f'Прилетел запрос на получение списка пользователей от {msg["from_user"]}')
                    users_list = ', '.join([user['username'] for user in USERSLIST])

                    responses.append({'client': socket,
                                      'from_user': 'server',
                                      'to_user': msg['from_user'],
                                      'message': users_list})

                elif msg['action'] == 'kill_user':
                    print(f'Прилетел запрос на отключение от {msg["from_user"]}')
                    for index, user in enumerate(USERSLIST):
                        if user['username'] == msg['from_user']:
                            USERSLIST.remove(user)
                            break

                else:
                    print(f'Прилетело сообщение от {msg["from_user"]} для {msg["to_user"]}')
                    users_list = ', '.join([user['username'] for user in USERSLIST])
                    if msg['to_user'] in users_list:
                        responses.append({'client': socket,
                                          'from_user': msg['from_user'],
                                          'to_user': msg['to_user'],
                                          'message': msg['msg'].upper()})
                    else:
                        print(f'В списке активных пользователей не найден {msg["to_user"]}')

    return responses


def write_responses(responses, r_clients, all_clients):
    for response in responses:
        socket = None
        # Определяем сокет получателя сообщения
        for user in USERSLIST:
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
            all_clients.remove(socket)

    # Отправили все сообщения из списка, список очистили
    responses.clear()


if __name__ == '__main__':
    log = get_logger()
    if log:
        hosts, port = parse_server_params(sys.argv)
        log.info(f'Определены параметры командной строки: host = {hosts}, port = {port}')

        if hosts is None or port is None:
            log.critical(f'Некорректные параметры командной строки: {sys.argv}')
        else:
            socket = create_socket('server')
            socket.bind((hosts, port))
            socket.listen(5)
            socket.settimeout(1)

            clients = []

            while True:
                try:
                    conn, address = socket.accept()
                except OSError as e:
                    pass
                else:
                    log.info(f'Установлено соединение с {conn} {address}')
                    clients.append(conn)
                finally:
                    # Проверить наличие событий ввода-вывода
                    wait = 5
                    r = [] # Список клиентов, читающих сообщения
                    w = [] # Список клиентов, отправляющих сообщения
                    try:
                        r, w, e = select.select(clients, clients, [], wait)
                    except Exception as e:
                        pass  # Ничего не делать, если какой-то клиент отключился

                    responses = read_messages(r, clients)  # Получаем сообщения от клиентов
                    if responses:
                        write_responses(responses, w, clients)  # Отправляем полученные сообщения читателям
