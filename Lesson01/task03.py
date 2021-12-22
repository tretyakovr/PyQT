# 3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
# Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном
# формате (использовать модуль tabulate).
from task02 import host_range_ping
from tabulate import tabulate


def host_range_ping_tab():
    ping_res = host_range_ping()

    columns = ['Reachable', 'Unreachable']
    print(tabulate(ping_res, headers=columns))


host_range_ping_tab()