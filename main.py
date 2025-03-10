# from parsers.parser_v1_api_request import IndexAPIParser
# from parsers.parser_v2_selenium_bs4 import IndexSeleniumParser
from parsers.parser_v3_request_bs4 import IndexRequestsParser

# Создаем парсер для индекса TIPOUS с набором данных для графика за год
# Важно! У Тинькова набор данных за полгода и год это один и тот же набор. Их всего два: year и all
tipous_parser = IndexRequestsParser(index='tipous', period='year')

# Выводим последние 10 точек
for point in tipous_parser.get_data(last=10):
    print(str(point.timestamp), point.value)

# Записываем в БД последние 15 точек
tipous_parser.save_to_db(last=15)

print('*' * 10, 'separator', '*' * 10)

# Для примера, создадим еще парсер для индекса GOLD с набором за все время
gold_parser = IndexRequestsParser(index='gold', period='all')

# Выводим последние 7 точек
for point in gold_parser.get_data(last=7):
    print(str(point.timestamp), point.value)

# Записываем в БД последние 10 точек
gold_parser.save_to_db(last=10)