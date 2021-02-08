import asyncio
import parse_zakupki
from db import database
from study import db


class Notify:

    def __init__(self, bot, db):
        self.bot = bot
        self.array = [db.get_all_tenders()]
        self.db = db

    async def get_data(self):
        r = parse_zakupki.get_html(parse_zakupki.URL)
        data = parse_zakupki.get_content(r.text)
        to_notify = []
        buffer = []
        for item in data:
            if item['number'] not in self.array:
                to_notify.append(item)
                buffer.append(item['number'])
            else:
                break

        self.array.extend(buffer)
        with self.db.connection:
             self.db.cursor.executemany("""INSERT INTO tenders (number, 
                                                            type,
                                                            title, 
                                                            phase, 
                                                            customer, 
                                                            customer_link, 
                                                            link,
                                                            last_date, 
                                                            price) VALUES (:number,:type,:phase,:title,:customer,:customer_link,:link,:last_date,:price);""",to_notify)
        print(to_notify)
        return to_notify

    async def sheduler(self):
        while True:
            parse_zakupki.get_html(parse_zakupki.URL)
            data = await self.get_data()
            for item in data:
                await self.sendler(item)

            await asyncio.sleep(30)
            pass

    async def sendler(self, item):
        users = self.db.get_users()
        for user in users:
            try:
                await self.bot.send_message(user, f"Оповещение!\n"
                                                          f"Номер закупки : {item['number']}\n"
                                                          f"Тип закупки: {item['type']}\n"
                                                          f"Этап закупки: {item['phase']}\n"
                                                          f"Описание 📝: {item['title']}\n"
                                                          f"Заказчик 🧑: {item['customer']}\n"
                                                          f"Ссылка на заказчика 🔗: {item['customer_link']}\n"
                                                          f"Ссылка на закупку 🔗: {item['link']}\n"
                                                          f"Дата размещения 📆: {item['last_date']}\n"
                                                          f"Начальная цена 💰: {item['price']}\n"
                                            )
            except Exception as e:
                print(e)
