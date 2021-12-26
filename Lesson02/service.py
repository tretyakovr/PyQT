from socket import *
import sys
import json
import logging
from decos import log
import argparse
import random


@log
def parse_client_params(params, logger):
    host, port, username = None, None, None

    parser = argparse.ArgumentParser(description='client parser')
    parser.add_argument('--addr')
    parser.add_argument('--port')
    parser.add_argument('--username')
    args = parser.parse_args()

    host = args.addr or 'localhost'
    port = args.port or 7777
    username = args.username or 'user' + str(random.randint(1, 1000))

    if host is None or port is None or username is None:
        logging.getLogger(logger).critical(f'Некорректные параметры командной строки: {sys.argv}')
        sys.exit(1)
    else:
        logging.getLogger(logger).info(f'Определены параметры командной строки: host = {host}, port = {port}, username = {username}')

    return host, port, username


@log
def parse_server_params(params, logger):
    hosts, port = None, None

    parser = argparse.ArgumentParser(description='server parser')
    parser.add_argument('-a')
    parser.add_argument('-p')
    args = parser.parse_args()

    hosts = args.a or ''
    port = args.p or 7777

    if hosts is None or port is None:
        logging.getLogger(logger).critical(f'Некорректные параметры командной строки: {sys.argv}')
        sys.exit(1)
    else:
        logging.getLogger(logger).info(f'Определены параметры командной строки: host = {hosts}, port = {port}')

    return hosts, port


@log
def encode_msg(action, from_user, to_user, msg):
    # msg = {'action': action,
    #        'from_user': from_user,
    #        'to_user': to_user,
    #        'msg': msg}

    return json.dumps({'action': action,
                       'from_user': from_user,
                       'to_user': to_user,
                       'msg': msg}).encode('utf-8')


# @log
def decode_msg(msg):
    # Столкнулись с проблемой при декодировании пустых сообщений
    try:
        msg = msg.decode('utf-8')
    except Exception as e:
        print(f'Decode message error: {e}')

    # print(f'msg = {msg}')

    res = ''
    if msg:
        try:
            res = json.loads(msg)
        except Exception as e:
            print(f'JSON loads error: {e}')

    return res


@log
def create_socket(logger):
    s = None
    try:
        s = socket(AF_INET,SOCK_STREAM)  # Создать сокет TCP
    except Exception as e:
        logging.getLogger(logger).error(f'Ошибка при создании сокета {str(e)}')
        sys.exit(1)
    else:
        logging.getLogger(logger).info(f'Сокет успешно создан: {s}')

    return s
