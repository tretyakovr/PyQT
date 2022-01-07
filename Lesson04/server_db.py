#! /usr/bin python3
# -*- coding: utf-8 -*-

import sqlite3
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, DateTime, String, MetaData, ForeignKey
from datetime import datetime
from sqlalchemy.orm import mapper, sessionmaker
import time, datetime


class Users:
    def __init__(self, id, name, start_session, socket, end_session):
        self.id = id
        self.name = name
        self.start_session = start_session
        self.socket = socket # Ошибочное (?) предположение, что целесообразно хранить сокет в БД
        self.end_session = end_session

    def __repr__(self):
        return f'User: {self.name}, last_login: {self.start_session}'


class LoginHistory:
    def __init__(self, id, user_id, login_datetime, ip_address, port):
        self.id = id
        self.user_id = user_id
        self.login_datetime = login_datetime
        self.ip_address = ip_address
        self.port = port

    def __repr__(self):
        return f'User_id: {self.user_id}, login_datetime: {self.login_datetime}'


# Отошел от требований к ДЗ
# В таблице Users: "активность" пользователя определяется по незаполненности поля end_session
# ActiveUsers удалить?
class ActiveUsers:
    def __init__(self, id, user_id, ip_address, port, login_datetime):
        self.id = id
        self.user_id = user_id
        self.ip_address = ip_address
        self.port = port
        self.login_datetime = login_datetime

    def __repr__(self):
        return f'User_id: {self.user_id}, ip address: {self:ip_address}, port: {self.port}'


# Таблица с сообщениями. Еще в работе
class Messages:
    def __init__(self, id, mdatetime, from_user_id, to_user_id, message):
        self.id = id
        self.mdatetime = mdatetime
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.message = message
        # Тут можно подойти творчески, добавить признаки доставки сообщения, прочтения сообщения,
        # отложенного сообщения...

def make_engine():
    sql_engine = None
    try:
        sql_engine = create_engine('sqlite:///server.sqlite', pool_recycle=3600)
    except Exception as e:
        print(e)

    return sql_engine


def create_metadata(engine):
    metadata = MetaData()

    users = Table('users', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('name', String, nullable=False, unique=True),
                  Column('start_session', DateTime),
                  Column('socket', String),
                  Column('end_session', DateTime))

    login_history = Table('login_history', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('user_id', ForeignKey('users.id')),
                          Column('login_datetime', DateTime, default=datetime.datetime.now()),
                          Column('ip_address', String),
                          Column('port', Integer))

    active_users = Table('active_users', metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user_id', ForeignKey('users.id')),
                         Column('ip_address', String),
                         Column('port', Integer),
                         Column('login_datetime', DateTime, default=datetime.datetime.now()))

    messages = Table('messages', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('mdatetime', DateTime, default=datetime.datetime.now()),
                     Column('from_user_id', ForeignKey('users.id')),
                     Column('to_user_id', ForeignKey('users.id')),
                     Column('message', String))

    metadata.create_all(engine)

    mapper(Users, users)
    mapper(LoginHistory, login_history)
    mapper(ActiveUsers, active_users)
    mapper(Messages, messages)


# Регистрируем пользователя в списке пользователей
def append_user(db_session, name_user, socket):
    # Сначала проверяем, есть ли пользователь в базе?
    row_user = db_session.query(Users).filter_by(name=name_user).first()
    if row_user is None:
        # Определяем следующий свободный id. Допускаю, что есть более лаконичный вариант, но пока так
        id_user = db_session.query(Users.id).order_by(Users.id.desc()).first()
        if id_user is None:
            id_user = 1
        else:
            id_user = id_user[0] + 1

        # И записываю дату/время начала сессии. Конец сессии пустой
        row_user = Users(id_user, name_user, datetime.datetime.now(), socket, None)
        db_session.add(row_user)
        db_session.commit()
    else:
        # Пользователь в БД есть
        id_user = row_user.id
        # Обновляем дату/время начала сессии, окончание сессии - пусто
        row_user = db_session.query(Users).filter_by(name=name_user).update({'start_session': datetime.datetime.now(),
                                                                             'end_session': None})
        db_session.commit()

    return id_user


# Записываем дату/время окончания сессии
def save_user_end_session(db_session, name_user):
    # Сначала проверяем, есть ли пользователь в базе?
    row_user = db_session.query(Users).filter_by(name=name_user).first()
    if row_user is None:
        # Можно в лог отправить сообщение об ошибке
        pass
    else:
        # Пользователь в БД есть
        # Обновляем дату/время завершения сессии
        row_user = db_session.query(Users).filter_by(name=name_user).update({'end_session': datetime.datetime.now()})
        db_session.commit()


# Обновляем историю сессий
def append_login_history(db_session, id_user, ip_address, port):
    # Определяем следующий свободный id
    last_id = db_session.query(LoginHistory.id).order_by(LoginHistory.id.desc()).first()
    if last_id is None:
        last_id = 1
    else:
        last_id = last_id[0] + 1

    row = LoginHistory(last_id, id_user, datetime.datetime.now(), ip_address, port)
    db_session.add(row)
    db_session.commit()


def append_message(db_session, from_user_id, to_user_id, message):
    last_id = db_session.query(Messages.id).order_by(Messages.id.desc()).first()
    if last_id is None:
        last_id = 1
    else:
        last_id = last_id[0] + 1

    row = Messages(last_id, datetime.datetime.now(), from_user_id, to_user_id, message)
    db_session.add(row)
    db_session.commit()


# Возвращаем в виде списка перечень всех пользователей. Можно добавить условие - только активных пользователей
def get_users_list(db_session, is_active=1):
    users_list = []
    for item in db_session.query(Users).all():
        if is_active:
            if item.end_session is None:
                users_list.append(item.name)
        else:
            users_list.append(item.name)

    return users_list


if __name__ == '__main__':
    sql_engine = make_engine()
    create_metadata(sql_engine)

    Session = sessionmaker(bind=sql_engine)
    session = Session()
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
