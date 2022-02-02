from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, DateTime, String, MetaData, ForeignKey
from datetime import datetime
from sqlalchemy.orm import mapper, sessionmaker
import datetime


class ClientDB:
    """
    Класс для описания локальной БД клиента. Состоит из таблиц:
    KnownUsers - список известных пользователей
    Messages - локальное хранилище сообщений
    """
    class KnownUsers:
        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return f'User: {self.name}'

    # Таблица с сообщениями
    class Messages:
        def __init__(self, mdatetime, user_id, direction, message):
            self.mdatetime = mdatetime
            self.user_id = user_id
            self.direction = direction
            self.message = message
            # Тут можно подойти творчески, добавить признаки доставки сообщения, прочтения сообщения,
            # отложенного сообщения, доставки сообщения в строго определенное время, ...

    def __init__(self, user_name):
        self.sql_engine = None
        try:
            self.sql_engine = create_engine(f'sqlite:///client_{user_name}.db3',
                                            pool_recycle=3600,
                                            connect_args={'check_same_thread': False})
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
                         Column('user_id', ForeignKey('known_users.id')),
                         Column('direction', Integer),  # In = 1, Out = 2
                         Column('message', String)
                         )

        self.metadata.create_all(self.sql_engine)

        mapper(self.KnownUsers, known_users)
        mapper(self.Messages, messages)

        Session = sessionmaker(bind=self.sql_engine)
        self.session = Session()

    # Добавяляем пользователя в список известных пользователей
    def append_user(self, name_user):
        if not self.session.query(self.KnownUsers).filter_by(name=name_user).count():
            known_users_row = self.KnownUsers(name_user)
            self.session.add(known_users_row)
            self.session.commit()

    # Получить id пользователя по его имени из локальной (!) БД
    def get_user_id(self, name_user):
        return self.session.query(self.KnownUsers.id).filter_by(name=name_user)

    def delete_known_user(self, name_user):
        self.session.query(self.KnownUsers).filter_by(name=name_user).delete()
        self.session.commit()
        # Здесь важный нюанс! Если удаляем из known_users пользователя, удалять ли каскадно его сообщения?
        # Получается, нарушена ссылочная целостность
        # С другой стороны, все эти сообщения есть на сервере и их можно (при улучшении интерфейса) с сервера запросить

    def append_message(self, name_user, direction, message):
        user_id = self.get_user_id(name_user)
        messages_row = self.Messages(datetime.datetime.now(), user_id, direction, message)
        self.session.add(messages_row)
        self.session.commit()
