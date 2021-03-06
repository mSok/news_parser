# -*- coding: utf-8 -*-
"""Модуль для работы с БД Postgres.

# создаем подключение к локальной БД
connect = db.connect_db({
    'host':'127.0.0.1',
    'port': '5433'
    })
# вставляем контент
db.put_content(
    connect,
    'http://localhost/news1',
    'Заголовок для новости о новости',
    'Сама новость с очень важным контентом...',
    0
)
"""
import logging
from collections import ChainMap

import psycopg2
from psycopg2.extras import LoggingConnection
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

DEFAULT_DB_NAME = 'news'

DEFAULT_DB_SETTINGS = {
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": 5432,
    "database": DEFAULT_DB_NAME,
}


class DBConnectionError(Exception):
    """Ошибки подключения"""
    pass


class MigrateError(Exception):
    """Ошибки миграции"""
    pass

class DBError(Exception):
    """Ошибка БД"""
    pass


def connect_db(conn_data={}):
    """Подключение к БД, если БД нет - создаст и смигрирует структуру.

    Args:
        conn_data(dict): данные для подключения к БД.
            Переданные параметры переписывают значения по умолчанию.
    Raises:
        DBConnectionError: ошибки подключения.
    Returns:
        (psycopg2.connect): коннект к БД.
    """
    conn = None
    _is_new = False
    chain_conf = ChainMap(conn_data, DEFAULT_DB_SETTINGS)
    db_name = chain_conf.get('database')
    try:
        conn = psycopg2.connect(
            database="postgres",
            user=chain_conf.get('user'),
            password=chain_conf.get('password'),
            host=chain_conf.get('host'),
            port=chain_conf.get('port'),
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute("SELECT datname FROM pg_database WHERE datname = %s;", (db_name,))
        fetch_db = cursor.fetchall()
        if not fetch_db:
            cursor.execute("CREATE DATABASE {};".format(db_name))
            _is_new = True
        conn.close()
    except psycopg2.DatabaseError as exc:
        raise DBConnectionError('Ошибка создания БД. {}'.format(str(exc)))
    db_con = psycopg2.connect(connection_factory=LoggingConnection, **chain_conf)
    db_con.initialize(logger)
    if _is_new:
        _migrate_db(db_con)
    return db_con


def _migrate_db(conn):
    """Пересоздает структуру БД. (Внимание) дропает таблицу перед созданием.

    Raises:
        MigrateError: ошибки миграции.
    Args:
        conn(psycopg2.connect): подключение к БД.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("""
        DROP TABLE IF EXISTS news;
        CREATE TABLE news
            (
            id serial,
            url text NOT NULL,
            header text,
            ts_header tsvector,
            content text,
            create_date timestamp with time zone  DEFAULT now(),
            source integer,
            CONSTRAINT pk_id PRIMARY KEY (id),
            CONSTRAINT uniq_url UNIQUE (url)
        )
            WITH (OIDS = FALSE);
        CREATE INDEX ind_search_title
           ON public.news using gin(ts_header);
        SET default_text_search_config = russian;
        """)
        conn.commit()
    except psycopg2.DatabaseError as exc:
        raise MigrateError('Ошибка создания структуры БД {}'.format(str(exc)))


def put_content(conn, url, header, content, source):
    """Запись контента
    Raises:
        DBError: Ошибки БД при создании.
    Args:
        conn(psycopg2.connect): подключение к БД.
        url, header, content, source - данные новости.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO news(url, header, ts_header, content, source)
            VALUES (%(url)s, %(header)s,to_tsvector(%(header)s), %(content)s, %(source)s)
            ON CONFLICT (url)
            DO UPDATE
            SET
                header = %(header)s,
                content = %(content)s,
                ts_header = to_tsvector(%(header)s),
                source = %(source)s
            ;
            """,
            {
                'url': url,
                'header': header.strip(),
                'content': content.strip(),
                'source': source
            }
        )
    except psycopg2.DatabaseError as exc:
        raise DBError('Ошибка вставки контента {}'.format(str(exc)))
    conn.commit()


def get_content(conn, search_string):
    """Поиск контента по заголовку новости
    Args:
        conn(psycopg2.connect): подключение к БД.
        search_string: строка для поиска
    Returns:
        list of tuples: результат
    """

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT *
            FROM news
            WHERE ts_header @@ to_tsquery('{}:* ');
            """.format(search_string)
        )
        return cursor.fetchall()
    except psycopg2.DatabaseError as exc:
        raise DBError('Ошибка синтаксиса {}'.format(str(exc)))
    conn.commit()
