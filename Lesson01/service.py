from socket import *
import sys
import json
import logging
from decos import log
import argparse
import random

# USERSLIST = {}


@log
def parse_client_params(params):
    host, port, username = None, None, None

    parser = argparse.ArgumentParser(description='client parser')
    parser.add_argument('--addr')
    parser.add_argument('--port')
    parser.add_argument('--username')
    args = parser.parse_args()

    host = args.addr or 'localhost'
    port = args.port or 7777
    username = args.username or 'user' + str(random.randint(1, 1000))

    return host, port, username


@log
def parse_server_params(params):
    hosts, port = None, None

    if len(params) == 1:
        hosts = ''
        port = 7777

    elif len(params) == 3:
        if params[1] == '-a':
            hosts = params[2]
            port = 7777
        elif params[1] == '-p':
            hosts = ''
            port = params[2]

    elif len(params) == 5:
        if params[1] == '-a':
            hosts = params[2]
        elif params[1] == '-p':
            port = params[2]

        if params[3] == '-a':
            hosts = params[4]
        elif params[3] == '-p':
            port = params[4]

    return hosts, port


@log
def encode_msg(action, from_user, to_user, msg):
    '''

    :param action: append_user, get_users, kill_user, message
    :param from_user:
    :param to_user:
    :param msg:
    :return:
    '''
    msg = {'action': action,
           'from_user': from_user,
           'to_user': to_user,
           'msg': msg}
    # if msg == 'close_connection':
    #     msg = {'action': 'quit',
    #            'message': msg}
    # else:
    #     msg = {'action': 'msg',
    #            'message': msg}

    return json.dumps(msg).encode('utf-8')


@log
def encode_reply(reply):
    if reply == 'quit':
        reply = {'action': 'quit',
                 'status': 600}
    else:
        reply = {'action': 'reply',
                 'status': 200,
                 'message': reply}

    return json.dumps(reply).encode('utf-8')


# @log
def decode_msg(msg):
    return json.loads(msg.decode('utf-8'))


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

