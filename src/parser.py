# -*- coding: utf-8 -*-
"""Модуль для парсеринга новостей"""

import requests
import bs4
from lxml import etree

from src import db
from src.rules import SiteRules



class ParseError(Exception):
    """Ошибки парсера"""
    pass


class Parser:
    """Базовый класс парсера ленты новостей"""
    def __init__(self, file_rule, db_connect={}):
        self.rules = SiteRules(file_rule)
        self.is_rss = self.rules.rss
        self.connect = db.connect_db(db_connect)

    def parse_news_lenta(self):
        """Парсим ленту новостей"""
        for lenta in self.rules.lenta:
            lenta_content = requests.get(lenta)
            if lenta_content.status_code == 200:
                if self.is_rss:
                    _lst_news = self._get_news_rss(lenta_content.text)
                else:
                    _lst_news = self._get_news(lenta_content.text)
                for item_href in _lst_news:
                    self.do_parse(item_href)

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

    def _get_news_rss(self, content):
        """Получить ссылку на новость из ленты новостей
        Args:
            content(str): контент ленты новостей

        Yields:
            (str): ссылка на новость
        """
        bs_news = etree.XML(content.encode('utf-8'))
        for _item in bs_news.xpath(self.rules.news_item):
            yield _item.text

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
