# -*- coding: utf-8 -*-
"""Модуль для обработки правил"""
import configparser

class SiteRules:
    """Правила парсинга новостный сайтов"""
    def __init__(self, file_rules):
        cfg = configparser.ConfigParser()
        cfg.read(file_rules)
        try:
            self.source = cfg.get('main', 'source')
            self.lenta = str(cfg.get('main', 'news_lenta')).split(',')
            self.base_url = cfg.get('main', 'base_url')
            self.news_item = cfg.get('main', 'news_item')
            self.content = cfg.get('main', 'content')
            self.header = cfg.get('main', 'header')
            self.rss = cfg.getboolean('main', 'rss')
        except configparser.NoOptionError as exc:
            raise Exception("Incorrect rule file. Exception: {}".format(exc))
