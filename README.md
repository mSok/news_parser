# Скрипт парсит сайты новостей и сохраняет в БД

### Формат правил парсера
Для парсера необходимы правила, которые заполняются в ini файлах и имеют следующий формат:
```ini
[main]
source = 1
base_url = https://ria.ru
news_lenta = https://ria.ru/politics/, https://ria.ru/society/
news_item = .b-list__item > a
header = h1.b-article__title span
content = .b-article__body
rss = false
```
где: 
    `source` - числовой идентификатор источника
    `base_url` - url источника
    `news_lenta` - страница на которой находятся список новостей, т.н. лента
    `news_item` - css класс, которым можно выделить ссылка на на новость в ленте
    `header` - css класс, которым можно выделить заголовок новости непосредственно  на странице новости
    `content` - css класс, самой новости
    `rss` - является ли список новостей rss документом или html

если список новостей это rss документ, то в значении `news_item` необходимо указать XPath до ссылки на саму новость. например: `news_item = //channel//item//link`

### Запуск парсера
- Запуск в докере

    `sudo docker-compose up`

- Запуск из SHELL
    установить необходимые библиотеки 
        `pip3 install -r requirements.txt`
    запустить парсер коммандой
        `python3 runner.py -r ria.ini`

    Параметры запуска приложения runner.py
    usage: runner.py [-h] [-r RULE] [-p PORT] [-H HOST] [-U USER] [-P PASSWORD] [-s SEARCH]
        optional arguments:
            -h, --help show this help message and exit
            -r RULE, --rule RULE  файл с правилами парсинга новостей
            -p PORT, --port PORT  порт БД. default 5432
            -H HOST, --host HOST  host БД. default 127.0.0.1
            -U USER, --user USER  пользователь БД. default postgres
            -P PASSWORD, --password PASSWORD пароль пользователя БД. default postgres
            -s SEARCH, --search SEARCH поиск новости по заголовку

### Поиск новости по БД

    `python3 runner.py -s путин`