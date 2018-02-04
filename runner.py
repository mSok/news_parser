# -*- coding: utf-8 -*-
import argparse

from parser import Parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rule", help="file with parse rules")
    args = parser.parse_args()
    if args.rule:
        st = Parser(args.rule)
        st.parse_news_lenta()
        exit(0)
    else:
        print("Args error")
        exit(1)
