from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, DateTime, String, MetaData, ForeignKey
from datetime import datetime
from sqlalchemy.orm import mapper, sessionmaker
import time, datetime


class ServerDB:
    """
    Класс описывает серверную БД приложения
    Users - таблица со список всех зарегистрированных на сервере клиентов
    Sessions - таблица содержит перечень всех сессий клиентов
    Messages - таблица содержит всю историю сообщений
    """
    class Users:
        def __init__(self, id, name, passwd):
            self.id = id
            self.name = name
            self.passwd = passwd

        def __repr__(self):
            return f'User: {self.name}'

    class Sessions:
        def __init__(self, id, user_id, start_session, ip_address, port, end_session=None):
            self.id = id
            self.user_id = user_id
            self.start_session = start_session
            self.ip_address = ip_address
            self.port = port
            self.end_session = end_session

        def __repr__(self):
            return f'User_id: {self.user_id}, login_datetime: {self.start_session}'

    # Таблица с сообщениями
    class Messages:
        def __init__(self, id, mdatetime, from_user_id, to_user_id, message):
            self.id = id
            self.mdatetime = mdatetime
            self.from_user_id = from_user_id
            self.to_user_id = to_user_id
            self.message = message
            # Тут можно подойти творчески, добавить признаки доставки сообщения, прочтения сообщения,
            # отложенного сообщения, доставки сообщения в строго определенное время, ...

    def __init__(self, db_filename):
        self.sql_engine = None
        try:
            self.sql_engine = create_engine(db_filename, pool_recycle=3600)
        except Exception as e:
            print(e)

        self.metadata = MetaData()

        users = Table('users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String, nullable=False, unique=True),
                      Column('passwd', String, nullable=False)
                      )

        sessions = Table('sessions', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user_id', ForeignKey('users.id')),
                         Column('start_session', DateTime, default=datetime.datetime.now()),
                         Column('ip_address', String),
                         Column('port', Integer),
                         Column('end_session', DateTime)
                         )

        messages = Table('messages', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('mdatetime', DateTime, default=datetime.datetime.now()),
                         Column('from_user_id', ForeignKey('users.id')),
                         Column('to_user_id', ForeignKey('users.id')),
                         Column('message', String)
                         )

        self.metadata.create_all(self.sql_engine)

        mapper(self.Users, users)
        mapper(self.Sessions, sessions)
        mapper(self.Messages, messages)

        Session = sessionmaker(bind=self.sql_engine)
        self.session = Session()

    def append_user(self, name_user, passwd):
        """
        Метод регистрирует в таблице Users нового пользователя
        UPD: устаревший метод(!), начиная с Lesson06 не используется (???)
        :param name_user: Имя пользователя
        :param passwd: Схэшированный пароль пользователя
        :return: id пользователя
        """
        # Сначала проверяем, есть ли пользователь в базе?
        id_user = 0
        row_user = self.session.query(self.Users).filter_by(name=name_user).first()
        if row_user is None:
            # Определяем следующий свободный id. Допускаю, что есть более лаконичный вариант, но пока так
            row_user = self.session.query(self.Users.id).order_by(self.Users.id.desc()).first()
            if row_user is None:
                id_user = 1
            else:
                id_user = row_user[0] + 1

            row_user = self.Users(id_user, name_user, passwd)
            self.session.add(row_user)
            self.session.commit()
        else:
            id_user = row_user.id

        return id_user

    def append_session(self, id_user, ip_address, port):
        """
        Метод добавляет сессию пользователя в таблицу Sessions
        :param id_user: Имя пользователя
        :param ip_address: ip-адрес клиента
        :param port: Порт клиента
        :return: id сессии
        """
        # Добавляем сессию
        id_session = self.session.query(self.Sessions.id).order_by(self.Sessions.id.desc()).first()
        if id_session is None:
            id_session = 1
        else:
            id_session = id_session[0] + 1

        row = self.Sessions(id_session, id_user, datetime.datetime.now(), ip_address, port)
        self.session.add(row)
        self.session.commit()

        return id_session # здесь нужно подумать, что возвращать

    # Регистрация нового пользователя из графического интерфейса сервера, без добавления сессии
    def reg_new_user(self, name_user, passwd):
        """
        Метод, добавляющий пользователя в таблицу Users
        :param name_user: Имя пользователя
        :param passwd: Схэшированный пароль
        :return:
        """
        # Сначала проверяем, есть ли пользователь в базе?
        id_user = 0
        row_user = self.session.query(self.Users).filter_by(name=name_user).first()
        if row_user is None:
            # Определяем следующий свободный id. Допускаю, что есть более лаконичный вариант, но пока так
            row_user = self.session.query(self.Users.id).order_by(self.Users.id.desc()).first()
            if row_user is None:
                id_user = 1
            else:
                id_user = row_user[0] + 1

            row_user = self.Users(id_user, name_user, passwd)
            self.session.add(row_user)
            self.session.commit()

    def close_session(self, id_session):
        """
        Метод записывает дату/время окончания сессии
        :param id_session: id сессии
        :return:
        """
        # Сначала проверяем, есть ли пользователь в базе?
        row_session = self.session.query(self.Sessions).filter_by(id=id_session).first()
        if row_session is None:
            # Сессия не найдена. Можно в лог отправить сообщение об ошибке
            pass
        else:
            # Сессия в БД есть
            # Обновляем дату/время завершения сессии
            row_session = self.session.query(self.Sessions).filter_by(id=id_session).update({'end_session': datetime.datetime.now()})
            self.session.commit()

    def append_message(self, from_user_id, to_user_id, message):
        """
        Метод сохраняет в таблицу Messages новое сообщение
        :param from_user_id: id отправителя сообщения
        :param to_user_id: id получателя сообщения
        :param message: Текст сообщения
        :return:
        """
        # Здесь исправить!
        last_id = self.session.query(self.Messages.id).order_by(self.Messages.id.desc()).first()
        if last_id is None:
            last_id = 1
        else:
            last_id = last_id[0] + 1

        row = self.Messages(last_id, datetime.datetime.now(), from_user_id, to_user_id, message)
        self.session.add(row)
        self.session.commit()

    # Возвращаем в виде списка перечень всех пользователей. Можно добавить условие - только активных пользователей
    # def get_users_list(self, is_active=1):
    def get_users_list(self):
        """
        Метод возвращает в виде списка список всех пользователей из таблицы Users
        Метод использовался в CLI-версии программы
        В GUI-версии не используется
        :return: Список пользователей
        """
        users_list = []
        for item in self.session.query(self.Users).all():
            # if is_active:
            #     if item.end_session is None:
            #         users_list.append(item.name)
            # else:
            users_list.append(item.name)

        return users_list

    # Запрашиваем пароль пользователя из БД
    def get_user_passwd(self, username):
        """
        Функция по имени пользователя возвращает схэшированный пароль
        :param username: Имя пользователя
        :return: Пароль
        """
        row_users = self.session.query(self.Users).filter(self.Users.name==username).first()
        if row_users is None:
            return False
        else:
            return row_users.passwd

    def check_username(self, username):
        """
        Метод проверяет существование пользователя на сервере, в случае успеха возвращает его id
        :param username: Имя пользователя
        :return: id пользователя
        """
        row_users = self.session.query(self.Users).filter(self.Users.name==username).first()
        if row_users is None:
            return False
        else:
            return row_users.id

    def get_user_id(self, username):
        """
        Метод по имени пользователя возвращает его id
        :param username: Имя пользователя
        :return: id пользователя
        """
        row_users = self.session.query(self.Users).filter(self.Users.name==username).first()
        if row_users is None:
            return False
        else:
            return row_users.id

    def get_user_session(self, id_user):
        """
        Метод возвращает id активной сессии пользователя
        :param id_user: id пользователя
        :return: id сессии
        """
        # Сначала проверяем, есть ли пользователь в базе?
        row_session = self.session.query(self.Sessions).filter(self.Sessions.user_id==id_user, self.Sessions.end_session == None).first()
        if row_session is None:
            # Сессия не найдена. Можно в лог отправить сообщение об ошибке
            return None
        else:
            # Сессия в БД есть
            return row_session.id

    def save_user_end_session(self, id_user):
        """
        Странный метод
        :param id_user:
        :return:
        """
        pass
