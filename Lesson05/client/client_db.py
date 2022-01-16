# import sqlite3
# import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, DateTime, String, MetaData, ForeignKey
from datetime import datetime
from sqlalchemy.orm import mapper, sessionmaker
import time, datetime
from service.service import get_client_params
import sys
# import configparser


class ClientDB:
    def __init__(self, user_name):
        self.sql_engine = None
        try:
            self.sql_engine = create_engine(f'sqlite:///client_{user_name}.sqlite', pool_recycle=3600)
        except Exception as e:
            print(e)

        self.metadata = MetaData()

        known_users = Table('known_users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, nullable=False, unique=True)
                           )

        messages = Table('messages', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('mdatetime', DateTime, default=datetime.datetime.now()),
                         Column('user_id', ForeignKey('users.id')),
                         Column('direction', Integer), # In = 1, Out = 2
                         Column('message', String)
                         )

        self.metadata.create_all(self.sql_engine)

        mapper(self.Users, known_users)
        mapper(self.Messages, messages)

        Session = sessionmaker(bind=self.sql_engine)
        self.session = Session()

    class Users:
        def __init__(self, id, name):
            self.id = id
            self.name = name

        def __repr__(self):
            return f'User: {self.name}'

    # Таблица с сообщениями
    class Messages:
        def __init__(self, id, mdatetime, user_id, direction, message):
            self.id = id
            self.mdatetime = mdatetime
            self.user_id = user_id
            self.direction = direction
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


    # Добавяляем пользователя в список известных пользователей
    def append_user(self, name_user):
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

        return id_user # здесь нужно подумать, что возвращать

    def append_message(self, user_id, direction, message):
        last_id = self.Messages.query(self.Messages.id).order_by(self.Messages.id.desc()).first()
        if last_id is None:
            last_id = 1
        else:
            last_id = last_id[0] + 1

        row = self.Messages(last_id, datetime.datetime.now(), user_id, direction, message)
        self.Messages.add(row)
        self.Messages.commit()


    # Возвращаем в виде списка перечень всех пользователей. Можно добавить условие - только активных пользователей
    # def get_users_list(self, is_active=1):
    #     users_list = []
    #     for item in self.Users.query(self.Users).all():
    #         if is_active:
    #             if item.end_session is None:
    #                 users_list.append(item.name)
    #         else:
    #             users_list.append(item.name)
    #
    #     return users_list


if __name__ == '__main__':
    host, port, user_name = get_client_params(sys.argv, 'client')
    print(host, port, user_name)

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
