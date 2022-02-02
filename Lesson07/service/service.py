import json
import argparse
import configparser
import sys
import logging
import os
from socket import *


class AppConfig:
    """
    Класс описывает конфигурацию приложения, его клиентской и серверной части
    """
    def __init__(self, ini_filename='settings.ini'):
        path = os.path.dirname(os.path.realpath(__file__))
        settings_filename = os.path.join(path, ini_filename)

        self.chat_config = config = configparser.ConfigParser()
        self.chat_config.read(settings_filename)

        self.client_host = config['CLIENT']['host']
        self.client_port = config['CLIENT']['port']
        self.client_username = config['CLIENT']['username']
        self.server_hosts = config['SERVER']['hosts']
        self.server_port = config['SERVER']['port']
        self.db_filename = config['DATABASE']['db_filename']


def get_server_params(logger):
    """
    Функция считывает из конфигурационного файла параметры серверной части приложения
    :param logger: Логгер для протоколирования работы метода
    :return: hosts, port, db_filename - считанные параметры
    """
    # TODO: сделать методом класса
    config = AppConfig()

    hosts, port, db_filename = None, None, None

    parser = argparse.ArgumentParser(description='server parser')
    parser.add_argument('-a')
    parser.add_argument('-p')
    parser.add_argument('-db_filename')
    args = parser.parse_args()

    hosts = args.a or config.server_hosts
    port = int(args.p) if args.p else int(config.server_port)
    db_filename = args.db_filename or config.db_filename

    if hosts is None or port is None or db_filename is None:
        logging.getLogger(logger).critical(f'Некорректные параметры командной строки: {sys.argv}')
        sys.exit(1)
    else:
        logging.getLogger(logger).info(f'Определены параметры командной строки: host = {hosts}, port = {port}')

    return hosts, port, db_filename


def get_client_params(logger):
    """
    Функция считывает из конфигурационного файла параметры клиентской части приложения
    :param logger: Логгер для протоколирования работы метода
    :return: host, post, username - считанные параметры
    """
    # TODO: сделать методом класса
    config = AppConfig()

    host, port, username = None, None, None

    parser = argparse.ArgumentParser(description='client parser')
    parser.add_argument('--addr')
    parser.add_argument('--port')
    parser.add_argument('--username')
    args = parser.parse_args()

    host = args.addr or config.client_host
    port = args.port or int(config.client_port)
    username = args.username or config.client_username

    if host is None or port is None or username is None:
        logging.getLogger(logger).critical(f'Некорректные параметры командной строки: {sys.argv}')
        sys.exit(1)
    else:
        logging.getLogger(logger).info(f'Определены параметры командной строки: host = {host}, port = {port}, username = {username}')

    return host, port, username


def encode_msg(msg):
    """
    Функция получает на входе сообщение, кодирует его в UTF-8 и сериализует
    :param msg: Сообщение в виде dict (допустимые форматы сообщений необходимо где-то описать)
    :return: Сериализованное кодированное сообщение
    """
    return json.dumps(msg).encode('utf-8')


def decode_msg(msg):
    """
    Функция получает на входе сериализованное кодированное в UTF-8 сообщение,
    десериализует его и декожирует
    :param msg: Сообщение
    :return: Декодированное сообщение в виде dict
    """
    # Столкнулись с проблемой при декодировании пустых сообщений
    try:
        msg = msg.decode('utf-8')
    except Exception as e:
        print(f'Decode message error: {e}')

    res = ''
    if msg:
        try:
            res = json.loads(msg)
        except Exception as e:
            print(f'JSON loads error: {e}. Message: {msg}')

    return res


def create_socket(logger):
    """
    Функция создает сокет для обмена сообщениями
    :param logger: Логгер для протоколирования работы функции
    :return: Созданный сокет
    """
    # TODO: проверить, есть подозрение, что вызов отсюда уже не используется
    s = None
    try:
        s = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
    except Exception as e:
        logging.getLogger(logger).error(f'Ошибка при создании сокета {str(e)}')
        sys.exit(1)
    else:
        logging.getLogger(logger).info(f'Сокет успешно создан: {s}')

    return s
