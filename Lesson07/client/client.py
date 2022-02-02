import sys
from service.service import get_client_params
from PyQt5.QtWidgets import QApplication
from client_db import ClientDB
from client_engine import ClientEngine
from client_gui import MainApp
from get_username import GetUserName


# Определяем параметры командной строки
host, port, username = get_client_params(sys.argv, 'client')

# Стартуем приложение
app = QApplication(sys.argv)

# Запрашиваем имя пользователя, если его не было в параметрах командной строки
if not username:
    username_dlg = GetUserName()
    app.exec_()

    # Здесь неадекватная реакция при нажатии клавиши Esc
    if username_dlg.ok_pressed:
        username = username_dlg.username_edit.text()
        userpasswd = username_dlg.passwd_edit.text()
        del username_dlg
    else:
        exit(0)

# Для пользователя подключаем его БД
client_db = ClientDB(username)

# Клиентский движок
client_engine = ClientEngine(host, port, client_db, username, userpasswd)
if client_engine.user_authenticate:
    client_engine.setDaemon(True)
    client_engine.start()

    main_app = MainApp(client_engine, client_db)
    sys.exit(app.exec_())

    client_engine.engine_shutdown()
    client_engine.join()
else:
    print('Ошибка аутентификации пользователя!')
