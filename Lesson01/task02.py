# 2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен
# только последний октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.
from task01 import host_ping


def host_range_ping():
    host_list = ['192.168.0.' + str(i) for i in range(100, 200)]

    return host_ping(host_list)


if __name__ == 'main':
    res = host_range_ping()
