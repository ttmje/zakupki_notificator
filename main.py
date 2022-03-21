# Бот телеграмм
import asyncio
from notify import Notify
from parse_zakupki import parse
from db import database
import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import keyboards as kb

# инициализируем соединение с БД
db = database('users.db')

# Задаем уровень логов
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=config.API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# Обработка команды /start
@dp.message_handler(commands=["start"])
async def start_bot(message: types.Message):
    await bot.send_message(message.chat.id,
                           f"Привет! MYSYA 228  \nЭтот бот автоматически забирает информацию по электронным закупкам с сайта zakupki.gov.ru"
                           f"\nСейчас в базе уже {db.show_last_id()} закупок!")
    await message.reply('Ага, я уже работаю над получением закупок!')

# Обработка команды /help
@dp.message_handler(commands=["help"])
async def start_bot(message: types.Message):
    await bot.send_message(message.chat.id, "Привет, я робот-нотификатор.\n"
                                            "Я автоматически собираю информацию о всех закупках с государственного портала zakupki.gov.ru\n"
                                            "/subscribe - Подписаться на рассылку уведомлений  оновыхзакупках\n"
                                            "/unsubscribe - Отписать от рыссылки\n"
                                            "/start - Начать работу с ботом\n"
                                            "/help - Справочная информация\n"
                                            "/last - показать последний торг в базе\n"
                                            "/file - Получить EXCEL файл с информацией о закупках\n"
                                            "/parse - Запустить парсинг всех страниц")

# Обработка команды /last
@dp.message_handler(commands=['last'])
async def send_message(message: types.Message):
    await bot.send_message(message.chat.id, f" Последний торг в базе:\n"
                                            f"ID : {db.show_last_tender().Id}\n"
                                            f"Номер закупки : {db.show_last_tender().Номер}\n"
                                            f"Тип закупки: {db.show_last_tender().Тип}\n"
                                            f"Описание 📝: {db.show_last_tender().Описание}\n"
                                            f"Заказчик 🧑: {db.show_last_tender().Заказчик}\n"
                                            f"Ссылка на заказчика 🔗: {db.show_last_tender().Ссылка_на_заказчика}\n"
                                            f"Ссылка на закупку 🔗: {db.show_last_tender().Ссылка_на_закупку}\n"
                                            f"Дата размещения 📆: {db.show_last_tender().Дата_размещения}\n"
                                            f"Начальная цена 💰: {db.show_last_tender().Цена}\n")

# Обработка команды /file
@dp.message_handler(commands=['file'])
async def send_message(message: types.Message):
    FILE = open('torgi.csv', "rb")
    await bot.send_document(message.chat.id, FILE, caption=f"Полученная информация была записана в этот файл!")

# Активация подписки
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if (not db.user_exists(message.from_user.id)):
        # Если юзера нет в базе, дабавляем его
        db.add_users(message.from_user.id)
    else:
        # если он уже есть, то обновляем ему статус подписки
        db.update_users(message.from_user.id, True)
    await message.answer("Вы успешно подписались на рассылку! \n")

# Активация отписки
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if (not db.user_exists(message.from_user.id)):
        # Если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_users(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        # Если он уже есть, то просто обновляем статус подписки
        db.update_users(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рыссылки.")

# Обработка команды /parse
@dp.message_handler(commands=["parse"])
async def start_bot(message: types.Message):
    await bot.send_message(message.chat.id,
                           "Данная команда принудительно запускает процесс парсинга последних 100 страниц портала закупок, результат будет записан в файл, прошу вас подождать пару минут")
    parse.parse_func()

# Функция нотификации
async def notify_starter():
    await Notify(bot=bot, db=db).sheduler()

# При запуске бота создаем отдельный поток, в котором выполняется функция нотификации
async def on_start_up(x):
    asyncio.create_task(notify_starter())

# запускеаем лонг поллинг
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_start_up)
