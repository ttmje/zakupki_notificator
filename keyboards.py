#Кнопки для бота
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup


button = KeyboardButton('Ок, все понятно, давай начинать.')
button_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button)


# Кнопки "меню" помощь

button1 = KeyboardButton('Показать список доступных команд')
markup1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button1)
markup2 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button1)

