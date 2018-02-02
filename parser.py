"""Модуль для парсеринга новостей"""

import argparse

import requests
import bs4
from rules import SiteRules


class ParseError(Exception):
    """Ошибки парсера"""
    pass


class Parser:
    """Класс парсера ленты новостей"""
    def __init__(self, file_rule):
        self.rules = SiteRules(file_rule)

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
            raise ParseError('Error parse url: {}'.format(full_url)) from exc
        self.put_content(header, content, full_url)

    # TODO Необходимо реализовать
    def put_content(self, header, content, url):
        """Сложить контент в БД

        Args:
            header(str): Заголовок
            content(str): Контент
            url(str): ссылка на новость
        """
        print(url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rule", help="file with parse rules")
    args = parser.parse_args()
    if args.rule:
        st = Parser(args.rule)
        st.parse_news_lenta()
        exit(0)
    else:
        print("Ошибка. Не передан параметр с правилами парсинга")
        exit(1)
