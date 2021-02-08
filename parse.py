#parser

import requests
from bs4 import BeautifulSoup
import csv



#Настройки

URL = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz223=on&af=on&currencyIdGeneral=-1&publishDateFrom=08.01.2021'
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36', 'accept': '*/*'}
HOST = 'https://zakupki.gov.ru/'
FILE = 'avito.csv'


def get_html(url, params=None):
    pass
    r = requests.get(url, headers=HEADERS, params=params)
    return r

#узнаем количество страниц
def get_pages_count (html):
    soup = BeautifulSoup(html, 'html.parser')
    # присваиваем переменной pagination все СПАНы класса pagination-item-1WyVp
    pagination = soup.find('span', id='true')
    if pagination:
        # Вычитаем последнюю страниц и страницу c нзванием "след."
        return int(pagination[-2].get_text())
    else:
        return 1

#Получаем блоки для парсинга
def get_content (html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='CardStyles__MainInfoContainer-sc-18miw4v-1 eQkaPG')
# Генерируем словарь для собранных данных, дополняем его полученными
    avito = []
    for item in items:
        avito.append({
            'title': item.find('span', class_='EllipsedSpan__WordBreakSpan-sc-1fhhmku-0 cQAGbs').get_text(strip=True),
            'link': HOST + item.find('a', class_='ui header CardStyles__MainInfoNameHeader-sc-18miw4v-7 hCKFJH').get('href'),
            'price': item.find('div', class_='ui blue header CardStyles__PriceInfoNumber-sc-18miw4v-8 jxnnHQ').get_text(strip=True)
        })
        KOL = len(avito)
    return avito

#Сохраняем полученную инфу в файл

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['Название', 'Ссылка', 'Цена'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['price']])

#Функция парсинга
def parse_func():
    html = get_html(URL)
    print('Код ответа страницы: ', html.status_code, ' похоже, что все ок, можем собирать информацию.')
    if html.status_code == 200:
        avito = []
        pages_count = get_pages_count(html.text)

        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            avito.extend(get_content(html.text))
            save_file(avito, FILE)
        print(f'Получено {len(avito)} записей, они записаны в файл')
