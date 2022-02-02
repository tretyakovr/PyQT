import sys
import logging
import traceback as tb


def log(func):
    def wrap(*args, **kwargs):
        if str(sys.argv).find('client') == -1:
            l = logging.getLogger('server')
        else:
            l = logging.getLogger('client')

        call_str = tb.format_stack()[0]
        n_pos = call_str.find('\n')

        l.info(f'Декоратор: обращение к функции {func.__name__} с параметрами {args}, {kwargs}')
        l.info(f'вызвано из функции {call_str[n_pos + 1 ::]}')
        # Здесь наверное можно было еще поиграться с форматированием, но, как минимум, вызвавшую функцию я смог определить

        f = func(*args, **kwargs)
        return f
    return wrap
