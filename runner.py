# -*- coding: utf-8 -*-
import argparse
import time

from src.parser import Parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rule", help="file with parse rules")
    parser.add_argument("-d", "--docker", help="docker pg service")
    args = parser.parse_args()
    if args.rule:
        if args.docker:
            st = Parser(
                args.rule,
                {
                    "host": "postgresql",
                }
            )
        else:
            st = Parser(
                args.rule,
                {"port": "5433"}
            )
        while True:
            st.parse_news_lenta()
            # каждые 30мин
            time.sleep(60*30)
        exit(0)
    else:
        print("Args error")
        exit(1)
