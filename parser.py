# -*- coding: utf-8 -*-
"""Модуль для парсеринга новостей"""

import requests
import bs4
from rules import SiteRules
import db


class ParseError(Exception):
    """Ошибки парсера"""
    pass


class Parser:
    """Класс парсера ленты новостей"""
    def __init__(self, file_rule):
        self.rules = SiteRules(file_rule)
        self.connect = db.connect_db()

    def parse_news_lenta(self):
        """Парсим ленту новостей"""
        for lenta in self.rules.lenta:
            lenta_content = requests.get(lenta)
            if lenta_content.status_code == 200:
                for item_href in self._get_news(lenta_content.text):
                    self.do_parse(item_href)

    def _get_news(self, content):
        """Получить ссылку на новость из ленты новостей
        Args:
            content(str): контент ленты новостей

        Yields:
            (str): ссылка на новость
        """
        bs_news = bs4.BeautifulSoup(content, "html.parser")
        for _item in bs_news.select(self.rules.news_item):
            href = _item.attrs.get('href')
            yield href

    def do_parse(self, news_href):
        """Парсим новость по ссылке

        Args:
            news_href(str): ссылка на страницу новости

        Raises:
            ParseError: ошибка парсинга новости
        """
        full_url = self.rules.base_url+news_href
        news_content = requests.get(full_url)
        news_content.raise_for_status()
        bs_news_content = bs4.BeautifulSoup(news_content.text, "html.parser")
        try:
            header = bs_news_content.select_one(self.rules.header).text
            content = bs_news_content.select_one(self.rules.content).text
        except (ValueError, AttributeError) as exc:
            print('Error parse url: {} exception {}'.format(full_url, str(exc)))
            raise ParseError('Error parse url: {}'.format(full_url))
        self.put_content(header, content, full_url)

    def put_content(self, header, content, url):
        """Сложить контент в БД

        Args:
            header(str): Заголовок
            content(str): Контент
            url(str): ссылка на новость
        """
        db.put_content(
            self.connect,
            url,
            header,
            content,
            self.rules.source
        )
