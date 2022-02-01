import os
import logging
from logging.handlers import TimedRotatingFileHandler

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

logger = logging.getLogger('client')

# Формат строки для вывода сообщений
strfmt = '%(asctime)s.%(msecs)03d %(levelname)-10s %(name)-10s %(message)s'

# Устанавливаем формат даты
datefmt = '%d-%m-%Y %H:%M:%S'
formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)
fh = TimedRotatingFileHandler(PATH, when='M', interval=10, encoding='utf-8')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.setLevel(logging.INFO)
logger.propagate = False
