# -*- coding: utf-8 -*-
"""Runner для запуска парсера новостей
# примеры вызова:

# парсер коннектится к локальной БД на порт 5433 на localhost
python3 runner.py -r ria.ini -p 5433 -H localhost

# Поиск по БД новостей 
python3 runner.py -s путин -p 5433
"""

import argparse
import time

from src.parser import Parser
from src import db

if __name__ == '__main__':

    conn_parameters = ['port', 'host', 'user', 'password']

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-r", "--rule", help="файл с правилами парсинга новостей")
    arg_parser.add_argument("-p", "--port", help="порт БД. default 5432")
    arg_parser.add_argument("-H", "--host", help="host БД. default 127.0.0.1")
    arg_parser.add_argument("-U", "--user", help="пользователь БД. default postgres")
    arg_parser.add_argument("-P", "--password", help="пароль пользователя БД. default postgres")
    arg_parser.add_argument("-s", "--search", help="поиск новости по заголовку")

    args = arg_parser.parse_args()
    if not args.rule and not args.search:
        print("Args error! Не передан обязательный параметр правил или поиска")
        exit(1)

    # формируем строку подключения к БД
    db_conn = {_k:getattr(args, _k) for _k in vars(args) if _k in conn_parameters and getattr(args, _k)}
    if args.rule:
        _parser = Parser(
            args.rule,
            db_conn
        )
        print('start parser')
        while True:
            _parser.parse_news_lenta()
            # каждые 30мин
            time.sleep(60*30)
    elif args.search:
        connect = db.connect_db(db_conn)
        res = db.get_content(
            connect,
            args.search
        )
        print(res)

    exit(0)
