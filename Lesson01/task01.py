# 1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
# Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста
# или ip-адресом. В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего
# сообщения («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью
# функции ip_address().
import subprocess
from ipaddress import ip_address


def host_ping(hosts):
    ping_count = 4
    cmd = ['ping', '-c', str(ping_count)]
    res = {'Reachable': [], 'Unreachable': []}

    for host in hosts:
        args = cmd.copy()
        args.append(host)
        ping_result = subprocess.call(args)

        print(host, ': УЗЕЛ ДОСТУПЕН' if ping_result == 0 else ': УЗЕЛ НЕДОСТУПЕН')
        if ping_result == 0:
            res['Reachable'].append(host)
        else:
            res['Unreachable'].append(host)

        print('\n')

    return res


# В задании не понял последнее предложение на счет функции ip_address. В функцию ip_address необходимо передать строку с
# ip-адресом, а потом полученный объект преобразовать обратно в строку?
if __name__ == 'main':
    host_list = ['yandex.ru', 'youtube.com', str(ip_address('212.122.1.2')), str(ip_address('8.8.8.8')), 'aaa']
    res = host_ping(host_list)
