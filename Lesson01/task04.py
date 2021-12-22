import server
import client
import subprocess
from os import *

pathOfFile=path.dirname(__file__)
pathServer=path.join(pathOfFile, "server.py")
pathClient=path.join(pathOfFile, "client.py")

while True:
    cmd = input('Выберите действие: "1" - запустить сервер, "2" - запустить клиент, "3" - завершить работу: ')
    if cmd == "3":
        break
    elif cmd == "1":
        SERVER = subprocess.Popen(
            f'osascript -e \'tell application "Terminal" to do'
            f' script "python3 {pathServer}"\'', shell=True)
    elif cmd == "2":
        CLIENT = subprocess.Popen(
            f'osascript -e \'tell application "Terminal" to do'
            f' script "python3 {pathClient}"\'', shell=True)
    else:
        continue
