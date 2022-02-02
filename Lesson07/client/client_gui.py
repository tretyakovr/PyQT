import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QTextEdit, QWidget
from PyQt5.QtWidgets import QPushButton, QAbstractItemView, QMessageBox, QTableView
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QColor, QBrush
from PyQt5.QtCore import pyqtSlot, QEvent, Qt
from add_contact import AddContactDialog

sys.path.append('../')


class MainApp(QMainWindow):
    """
    Описание класса основного окна клиентской программы
    """
    def __init__(self, client_engine, client_db, parent=None):
        super().__init__()
        self.client_engine = client_engine
        self.client_db = client_db

        # Связка между сигналом и методом экземпляра движка?
        self.client_engine.new_user.connect(self.new_user)
        self.client_engine.user_not_exist.connect(self.user_not_exist)
        self.client_engine.new_message.connect(self.new_message)
        self.client_engine.update_users_status.connect(self.update_users_status)

        # Текущий пользователь в списке известных пользователей (текущий чат)
        self.current_user = None
        self.current_user_id = 0

        self.initUI()

    def initUI(self):
        self.setFixedSize(800, 630)
        self.setWindowTitle('Client chat')

        self.known_users_model = None
        self.tv_known_users = QTableView(self)
        self.tv_known_users.move(10, 50)
        self.tv_known_users.setFixedSize(160, 540)
        self.tv_known_users.clicked.connect(self.select_active_user)

        # Устанавливаем способ выделения внутри таблицы: вся строка
        self.tv_known_users.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.messages_model = None
        self.tv_messages = QTableView(self)
        self.tv_messages.move(180, 50)
        self.tv_messages.setFixedSize(610, 400)

        self.te_message = QTextEdit(self)
        self.te_message.move(180, 460)
        self.te_message.setFixedSize(610, 80)

        self.btn_send = QPushButton(self)
        self.btn_send.move(690, 550)
        self.btn_send.setFixedSize(100, 40)
        self.btn_send.setText('Отправить')
        self.btn_send.clicked.connect(self.send_message)

        exitAction = QAction(QIcon(''), 'Завершить работу', self)
        exitAction.setShortcut('Ctrl+Q')
        # exitAction.triggered.connect(qApp.quit)
        # TODO: есть предопределенное собитие в def event() и триггер. Что-то здесь лишнее
        exitAction.triggered.connect(self.close_app)

        self.btnRefreshKnownUsers = QAction(QIcon(''), 'Refresh', self)
        self.btnRefreshKnownUsers.triggered.connect(self.refresh_users_status)

        self.btnAppendUser = QAction(QIcon(''), 'Append user', self)
        self.btnAppendUser.triggered.connect(self.append_user)

        self.btnDeleteUser = QAction(QIcon(''), 'Delete user', self)
        self.btnDeleteUser.triggered.connect(self.delete_user)

        # toolbar
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.setFixedHeight(40)
        self.toolbar.addAction(exitAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.btnRefreshKnownUsers)
        self.toolbar.addAction(self.btnAppendUser)
        self.toolbar.addAction(self.btnDeleteUser)

        # statusbar
        self.statusBar()

        # Подгружаем из БД список известных пользователей
        self.show_known_users()

        self.show()

    def refresh_window(self):
        """
        Метод, обновляющий основное окно программы
        Здесь включаются/выключаются поля в зависимости от того, выбран ли текущий пользователь
        :return:
        """
        if self.current_user is None:
            self.btnDeleteUser.setDisabled(True)
            self.tv_messages.setDisabled(True)
            self.te_message.setDisabled(True)
            self.btn_send.setDisabled(True)
        else:
            self.btnDeleteUser.setDisabled(False)
            self.tv_messages.setDisabled(False)
            self.te_message.setDisabled(False)
            self.btn_send.setDisabled(False)

        self.statusBar().showMessage(f'Текущий пользователь: {self.client_engine.username}, '
                                     f'текущий чат: {self.current_user}')

    def refresh_users_status(self):
        """
        Метод, обновляющий статус известных клиентов (online/offline)
        Формирует запрос со списком клиентов и отправляет его на сервер
        :return:
        """
        loc_userslist = []
        for item in self.client_db.session.query(self.client_db.KnownUsers).all():
            loc_userslist.append(item.name)

        # Отправляем запрос на сервер о статусе клиентов
        # Затем из полученных сообщений расшифруем статус и обновим таблицу
        self.client_engine.get_users_status(','.join(loc_userslist))

    def show_known_users(self):
        """
        Метод, описывающий список известных клиентов
        :return:
        """
        self.known_users_model = QStandardItemModel(self)

        for item in self.client_db.session.query(self.client_db.KnownUsers).all():
            table_item = []
            table_item.append(QStandardItem(str(item.id)))
            table_item.append(QStandardItem(item.name))
            if item.name in self.client_engine.online_userslist:
                t_item = QStandardItem('online')
                t_item.setForeground(QBrush(QColor('darkgreen')))
                table_item.append(t_item)
            else:
                table_item.append(QStandardItem('offline'))
                # Потом здесь будет семафорчик, зеленый - online, красный - offline

            # Вот тут бред, setEditable устанавливать на каждую ячейку. Почему нет setEditable для всего data_model?
            # Или на худой конец - для отдельной строки или колонки?
            for item in table_item:
                item.setEditable(False)
            self.known_users_model.appendRow(table_item)

        # Связываем модель с таблицей
        self.tv_known_users.setModel(self.known_users_model)

        # Прячем вертикальные и горизонтальные заголовки
        self.tv_known_users.horizontalHeader().hide()
        self.tv_known_users.verticalHeader().hide()

        # Прячем колонку с id
        self.tv_known_users.setColumnWidth(0, 0)

        # Колонку с username растягиваем на всю ширину
        self.tv_known_users.setColumnWidth(1, 100)
        self.tv_known_users.setColumnWidth(2, 60)

        # Прячем сетку
        self.tv_known_users.setShowGrid(False)

        # Обновляем окно
        self.refresh_window()

    def select_active_user(self):
        """
        Метод, срабатывающий при щелчке на известном пользователе
        Обновляет список сообщений и окно программы
        :return:
        """
        self.current_user = self.tv_known_users.currentIndex().data()
        self.current_user_id = self.client_db.get_user_id(self.current_user)
        self.show_messages()
        self.refresh_window()

    def append_user(self):
        """
        Метод, вызывающий окно для воода имени пользователя для добавления в список известных пользователей
        :return:
        """
        global select_dialog
        select_dialog = AddContactDialog()
        select_dialog.btn_find.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        """
        Метод - обработчик добавления, сообщает серверу имя пользователя, обновляет таблицу и список контактов
        :param item - объект диалогового окна:
        :return:
        """
        # Берем из диалога имя пользователя
        new_contact = item.username_edit.text()

        # Вызываем метод, который отправит сообщение на сервер - проверить существование такого пользователя
        self.client_engine.check_username(new_contact)

        # Закрываем диалоговое окно
        item.close()

    def delete_user(self):
        """
        Метод удаляет пользователя из списка известных пользователей
        :return:
        """
        if self.current_user and \
                QMessageBox.question(self, 'Подтвердите удаление записи',
                                     f'Действительно удалить из списка известных пользователей {self.current_user}?',
                                     QMessageBox.Yes|QMessageBox.No,
                                     QMessageBox.No) == QMessageBox.Yes:
            self.client_db.delete_known_user(self.current_user)
            self.show_known_users()
            self.current_user = None
            self.current_user_id = 0
            self.refresh_window()

    def show_messages(self):
        """
        Метод обновляет список сообщений при выборе контакта в списке известных пользователей
        :return:
        """
        self.messages_model = QStandardItemModel(self)

        for item in self.client_db.session.query(self.client_db.Messages).filter(self.client_db.Messages.user_id == self.current_user_id).all():
            # TODO: предыдущая строка валится на предупреждение. Нужно исправлять
            # SAWarning: implicitly coercing SELECT object to scalar subquery; please use the
            # .scalar_subquery() method to produce a scalar subquery
            table_item = []
            if item.direction == 1:
                row_item = QStandardItem(f'Входящее, {item.mdatetime}: \n {item.message}')
                row_item.setBackground(QBrush(QColor(255, 213, 213)))
                row_item.setTextAlignment(Qt.AlignLeft)
            else:
                row_item = QStandardItem(f'Исходящее,  {item.mdatetime}: \n {item.message}')
                row_item.setTextAlignment(Qt.AlignRight)
                row_item.setBackground(QBrush(QColor(204, 255, 204)))
            row_item.setEditable(False)
            table_item.append(row_item)

            self.messages_model.appendRow(table_item)

        self.tv_messages.setModel(self.messages_model)

        # Прячем вертикальные и горизонтальные заголовки
        self.tv_messages.horizontalHeader().hide()
        self.tv_messages.verticalHeader().hide()

        # Колонку с username растягиваем на всю ширину
        self.tv_messages.setColumnWidth(0, 610)

        # Растягиваем высоту строк по содержимому
        self.tv_messages.resizeRowsToContents()

        # Обновляем окно
        self.refresh_window()

    def send_message(self):
        """
        Метод, срабатывающий при нажатии на кнопку отправки введенного сообщения
        :return:
        """
        # Сохраняем сообщение в локальной базе данных
        self.client_db.append_message(self.current_user, 2, self.te_message.toPlainText())

        # `Отдаем сообщение движку для отправки в сокет
        self.client_engine.prepare_message_to_send(self.client_engine.username,
                                                   self.current_user, self.te_message.toPlainText())

        # Очищаем поле для ввода сообщения
        self.te_message.clear()

        # Обновляем историю сообщений
        self.show_messages()

        # Обновляем окно
        self.refresh_window()

    def close_app(self):
        """
        Метод закрытия окноа программы
        :return:
        """
        self.client_engine.engine_shutdown()
        qApp.quit()

    def event(self, e):
        if e.type() == QEvent.Close:
            self.close_app()

        # Событие отправляется дальше
        return QWidget.event(self, e)

    @pyqtSlot()
    def new_user(self):
        self.show_known_users()

    @pyqtSlot()
    def user_not_exist(self):
        """
        Слот выводит на экран сообщение об отсутствии пользователя на сервере
        :return:
        """
        QMessageBox.information(self, 'Ошибка!', 'Пользователь с указанным именем на сервере отсутствует',
                                QMessageBox.Ok,
                                QMessageBox.Ok)

    @pyqtSlot()
    def new_message(self):
        """
        Слот срабатывает при поступлении новго сообщения
        :return:
        """
        self.show_known_users()
        self.show_messages()

    @pyqtSlot()
    def update_users_status(self):
        """
        Слот, срабатывающий при обновлении статусо пользователей
        :return:
        """
        self.show_known_users()
