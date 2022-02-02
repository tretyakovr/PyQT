import unittest
import json
from socket import *
from service import create_socket, decode_msg, encode_msg, parse_client_params, parse_server_params


class TestCreateSocket(unittest.TestCase):
    def setUp(self):
        self.s = create_socket()

    def tearDown(self):
        self.s.close()

    def test_type_socket(self):
        self.assertEqual(isinstance(self.s, socket), True,
                         'Ошибка при создании сокета: некорректный тип возвращаемого значения')

    def test_empty_socket(self):
        self.assertNotEqual(self.s, None, 'Ошибка при создании сокета: возвращено пустое значение')


# class TestMakeConnection(unittest.TestCase):
#     def setUp(self):
#         self.server_hosts = ''
#         self.server_port = 7777
#         self.server_socket = create_socket()
#         self.server_socket.bind((self.server_hosts, self.server_port))
#         self.server_socket.listen(5)
#
#         self.client_host = 'localhost'
#         self.client_port = 7777
#         self.client_socket = create_socket()
#
#     def tearDown(self):
#         self.server_socket.close()
#         self.client_socket.close()
#
#     def test_make_connection(self):
#         # Здесь проверяется установка соединения с заранее известным сервером
#         # Т.е. при работе в реальных полевых условиях он бесполезен
#         # Это в продолжение моего сообщения на портале
#         self.assertEqual(make_connection(self.client_socket, self.client_host, self.client_port), True,
#                          'Ошибка при установлении соединения')


class TestDecodeMsg(unittest.TestCase):
    def setUp(self):
        self.msg = {'action': 'reply',
                    'status': 200,
                    'message': 'reply message'}
        self.encode_msg = json.dumps(self.msg).encode('utf-8')

    def test_check_type_input_params(self):
        self.assertEqual(isinstance(self.encode_msg, bytes), True,
                         f'Ошибка типа входного параметра: тип параметра не bytes. {type(self.encode_msg)}')

    def test_decode_msg(self):
        self.decode_msg = decode_msg(self.encode_msg)
        self.assertEqual(self.decode_msg, self.msg,
                         'Ошибка декодирования сообщения: исходное и декодированное сообщения не совпадают')


class TestEncodeMsg(unittest.TestCase):
    def setUp(self):
        self.empty_msg = {'action': 'quit'}
        self.encode_empty_msg = json.dumps(self.empty_msg).encode('utf-8')

        self.msg = {'action': 'msg',
                    'message': 'msg'}
        self.encode_msg = json.dumps(self.msg).encode('utf-8')

    def test_encode_empty_msg(self):
        self.assertEqual(encode_msg(''), self.encode_empty_msg,
                         'Ошибка кодирования пустого сообщения: тестовое и кодированное сообщение не совпадают')

    def test_encode_msg(self):
        self.assertEqual(encode_msg('msg'), self.encode_msg,
                         'Ошибка кодирования не пустого сообщения: тестовое и кодированное сообщение не совпадают')


class TestParseClientParams(unittest.TestCase):
    def test_no_params(self):
        self.assertEqual(parse_client_params(['script_name']), ('localhost', 7777),
                         'Client.test_no_params: ошибка определения host, port')

    def test_host_only(self):
        self.assertEqual(parse_client_params(['script_name', 'addr', 'localhost']), ('localhost', 7777),
                         'Client.test_host_only: ошибка определения host, port')

    def test_port_only(self):
        self.assertEqual(parse_client_params(['script_name', 'port', 1111]), ('localhost', 1111),
                         'Client.test_port_only: ошибка определения host, port')

    def test_host_and_port(self):
        self.assertEqual(parse_client_params(['script_name', 'addr', '127.0.0.1', 'port', 2222]), ('127.0.0.1', 2222),
                         'Client.test_host_and_port: ошибка определения host, port')


class TestParseServerParams(unittest.TestCase):
    def test_no_params(self):
        self.assertEqual(parse_server_params(['script_name']), ('', 7777),
                         'Server.test_no_params: ошибка определения host, port')

    def test_hosts_only(self):
        self.assertEqual(parse_server_params(['script_name', '-a', 'any_hosts']), ('any_hosts', 7777),
                         'Server.test_hosts_only: ошибка определения host, port')

    def test_port_only(self):
        self.assertEqual(parse_server_params(['script_name', '-p', 1111]), ('', 1111),
                         'Server.test_port_only: ошибка определения host, port')

    def test_hosts_and_port(self):
        self.assertEqual(parse_server_params(['script_name', '-a', 'any_hosts', '-p', 2222]), ('any_hosts', 2222),
                         'Server.test_hosts_and_port: ошибка определения host, port')

# Сознательно не сделал тесты для encode_reply, эту функцию позже заменю на encode_msg

if __name__ == '__main__':
    unittest.main()
