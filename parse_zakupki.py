#parse_zakupki.gov.ru
from db import database
import requests
from bs4 import BeautifulSoup
import csv
import asyncio


#настройки
db = database('users.db')
URL = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz223=on&af=on&currencyIdGeneral=-1'
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36', 'accept': '*/*'}
HOST = 'https://zakupki.gov.ru/'
FILE = 'torgi.csv'


#Получаем html страницу по указанному URL в настройках
def get_html(url, params=None):
    pass
    r = requests.get(url, headers=HEADERS, params=params)
    return r

#узнаем количество страниц c информацией
def get_pages_count (html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('li', class_='page')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1

#Получаем DIV блоки c информацией со страницы для парсинга
def get_content (html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_=['search-registry-entry-block', 'box-shadow-search-input'])
# Генерируем словарь для собранных данных, дополняем его полученными
    zakupki = []
    for item in items:
        zakupki.append({
            'number': item.find('div',  class_='registry-entry__header-mid__number').find_next('a').get_text(strip=True),
            'type': item.find('div',  class_=['registry-entry__header-top__title', 'text-truncate']).get_text(strip=True).replace("\n" ,"").replace("                                  ", ""),
            'title': item.find('div',  class_='registry-entry__body-value').get_text(strip=True),
            'phase': item.find('div',  class_='registry-entry__header-mid__title').get_text(strip=True),
            'customer': item.find('div',  class_='registry-entry__body-href').find('a').get_text(strip=True),
            'customer_link': item.find('div', class_='registry-entry__body-href').find('a').get('href'),
            'link': item.find('div', class_='registry-entry__header-mid__number').find('a').get('href'),
            'last_date': item.find('div', class_='row').find_next('div', class_='data-block__value').get_text(strip=True),
            'price': item.find('div', class_='price-block__value').get_text(strip=True).replace("₽", "").replace(" ","")
        })

    return zakupki





#Сохраняем полученную инфу в файл
def save_file(items, path):
    with open(path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['Номер',
                         'Тип закупки',
                         'Фаза',
                         'Объект закупки',
                         'Заказчик',
                         'Ссылка на заказчика',
                         'Ссылка на закупку',
                         'Дата окончания подачи заявок',
                         'Цена'])
        for item in items:
            writer.writerow([item['number'],
                             item['type'],
                             item['phase'],
                             item['title'],
                             item['customer'],
                             HOST + item['customer_link'],
                             HOST + item['link'],
                             item['last_date'],
                             item['price']])

#Функция парсинга
class parse:
    def parse_func():
        html = get_html(URL)
        print('Код ответа страницы: ', html.status_code, ' похоже, что все ок, можем собирать информацию.')
        if html.status_code == 200:
            zakupki = []
            pages_count = get_pages_count(html.text)
            for page in range(1, pages_count+1):
                #!ГЕНЕРИРУЕМ И ПОДСТАВЛЯЕМ НОМЕР СТРАНИЦЫ В URL,ЧТОБЫ МЕНЯЛИСЬ СТРАНИЦЫ!
                url_gen = f'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber={page}&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz223=on&af=on&currencyIdGeneral=-1'
                print(f'Парсинг страницы {page} из {pages_count}...')
                html = get_html(url_gen)
                zakupki.extend(get_content(html.text))
                save_file(zakupki, FILE)
            print(f'Получено {len(zakupki)} записей, они записаны в файл {FILE}')
            with db.connection:
                return db.cursor.executemany("""INSERT INTO tenders (number, 
                type,
                title, 
                phase, 
                customer, 
                customer_link, 
                link,
                last_date, 
                price) VALUES (:number,:type,:phase,:title,:customer,:customer_link,:link,:last_date,:price);""", zakupki)
                db.commit()
                db.connection.close()
        else:
            print("Упс, ошибочка. Error!")