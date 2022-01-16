# import sqlite3
# import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, DateTime, String, MetaData, ForeignKey
from datetime import datetime
from sqlalchemy.orm import mapper, sessionmaker
import time, datetime
from service.service import get_server_params
import sys
# import configparser

class ServerDB:
    def __init__(self, db_filename):
        self.sql_engine = None
        try:
            self.sql_engine = create_engine(db_filename, pool_recycle=3600)
        except Exception as e:
            print(e)

        self.metadata = MetaData()

        users = Table('users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String, nullable=False, unique=True)
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

    class Users:
        def __init__(self, id, name):
            self.id = id
            self.name = name

        def __repr__(self):
            return f'User: {self.name}'

    class Sessions:
        def __init__(self, id, user_id, start_session, ip_address, port, end_session):
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

    # def make_engine():
    #     config = configparser.ConfigParser()
    #     config.read('settings.ini')
    #     db_filename = config['DATABASE']['db_filename']
    #
    #     sql_engine = None
    #     try:
    #         sql_engine = create_engine(db_filename, pool_recycle=3600)
    #     except Exception as e:
    #         print(e)
    #
    #     return sql_engine
    #
    # def create_metadata(engine):
    #     # metadata = MetaData()
    #
    #     users = Table('users', metadata,
    #                   Column('id', Integer, primary_key=True),
    #                   Column('name', String, nullable=False, unique=True),
    #                   Column('start_session', DateTime),
    #                   Column('socket', String),
    #                   Column('end_session', DateTime))
    #
    #     login_history = Table('login_history', metadata,
    #                           Column('id', Integer, primary_key=True),
    #                           Column('user_id', ForeignKey('users.id')),
    #                           Column('login_datetime', DateTime, default=datetime.datetime.now()),
    #                           Column('ip_address', String),
    #                           Column('port', Integer))
    #
    #     active_users = Table('active_users', metadata,
    #                          Column('id', Integer, primary_key=True),
    #                          Column('user_id', ForeignKey('users.id')),
    #                          Column('ip_address', String),
    #                          Column('port', Integer),
    #                          Column('login_datetime', DateTime, default=datetime.datetime.now()))
    #
    #     messages = Table('messages', metadata,
    #                      Column('id', Integer, primary_key=True),
    #                      Column('mdatetime', DateTime, default=datetime.datetime.now()),
    #                      Column('from_user_id', ForeignKey('users.id')),
    #                      Column('to_user_id', ForeignKey('users.id')),
    #                      Column('message', String))
    #
    #     metadata.create_all(engine)
    #
    #     mapper(self.Users, users)
    #     mapper(self.LoginHistory, login_history)
    #     mapper(self.ActiveUsers, active_users)
    #     mapper(self.Messages, messages)


    # Регистрируем пользователя в списке пользователей
    def append_user(self, name_user, ip_address, port):
        # Сначала проверяем, есть ли пользователь в базе?
        id_user = 0
        row_user = self.session.query(self.Users).filter_by(name=name_user).first()
        if row_user is None:
            # Определяем следующий свободный id. Допускаю, что есть более лаконичный вариант, но пока так
            id_user = self.session.query(self.Users.id).order_by(self.Users.id.desc()).first()
            if id_user is None:
                id_user = 1
            else:
                id_user = id_user[0] + 1

            row_user = self.Users(id_user, name_user)
            self.session.add(row_user)
            self.session.commit()

        # Добавляем сессию
        id_session = self.session.query(self.Sessions.id).order_by(self.Sessions.id.desc()).first()
        if id_session is None:
            id_session = 1
        else:
            id_session = id_session[0] + 1

        row = self.Sessions(id_session, id_user, datetime.datetime.now(), ip_address, port)
        self.session.add(row)
        self.session.commit()

        return id_user, id_session # здесь нужно подумать, что возвращать


    # Записываем дату/время окончания сессии
    def close_session(self, id_session):
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

    #
    # # Обновляем историю сессий
    # def append_login_history(db_session, id_user, ip_address, port):
    #     # Определяем следующий свободный id
    #     last_id = db_session.query(LoginHistory.id).order_by(LoginHistory.id.desc()).first()
    #     if last_id is None:
    #         last_id = 1
    #     else:
    #         last_id = last_id[0] + 1
    #
    #     row = LoginHistory(last_id, id_user, datetime.datetime.now(), ip_address, port)
    #     db_session.add(row)
    #     db_session.commit()
    #
    #
    def append_message(self, from_user_id, to_user_id, message):
        last_id = self.session.query(self.Messages.id).order_by(self.Messages.id.desc()).first()
        if last_id is None:
            last_id = 1
        else:
            last_id = last_id[0] + 1

        row = self.Messages(last_id, datetime.datetime.now(), from_user_id, to_user_id, message)
        self.Sessions.add(row)
        self.Sessions.commit()


    # Возвращаем в виде списка перечень всех пользователей. Можно добавить условие - только активных пользователей
    # def get_users_list(self, is_active=1):
    def get_users_list(self):
        users_list = []
        for item in self.session.query(self.Users).all():
            # if is_active:
            #     if item.end_session is None:
            #         users_list.append(item.name)
            # else:
            users_list.append(item.name)

        return users_list

    # Возвращает код активной сессии или None, если ее нет
    def get_user_session(self, id_user):
        # Сначала проверяем, есть ли пользователь в базе?
        row_session = self.session.query(self.Sessions).filter(self.Sessions.id_user==id_user, self.Sessions.end_session == None).first()
        if row_session is None:
            # Сессия не найдена. Можно в лог отправить сообщение об ошибке
            return None
        else:
            # Сессия в БД есть
            # Обновляем дату/время завершения сессии
            # row_session = self.Sessions.query(self.Sessions).filter_by(id=id_session).update({'end_session': datetime.datetime.now()})
            # self.session.commit()
            return row_session.id


if __name__ == '__main__':
    hosts, port, db_filename = get_server_params(sys.argv, 'server')
    print(hosts, port, db_filename)

    server_db = ServerDB(db_filename)
    # print(server_db.get_users_list())

    # sql_engine = self.make_engine()


    # create_metadata(sql_engine)

    # Session = sessionmaker(bind=sql_engine)
    # session = Session()
    # print(sql_engine)
    # print(session)

    # For test only
    # for i in range(1, 10):
    #     append_user(session, f'user#{i}')
    #     row_user = Users(i, f'user#{i}', datetime.datetime.now())
    #     session.add(row_user)
    #     time.sleep(1)
    #
    # session.commit()
    #
    # append_user(session, 'test append')
