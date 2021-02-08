import sqlite3
from collections import namedtuple
class database:


    def __init__(self, database_file):
        """Подключается к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def get_users(self):
        """Получаем активных подписчиков бота"""
        with self.connection:
            id_users = self.cursor.execute("SELECT user_id FROM users WHERE status = '1' ").fetchall()
            id_users = [i[0] for i in id_users]
            return id_users

    def user_exists(self, user_id):
        """Проверяем есть ли юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_users(self, user_id, status=True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `status`) VALUES (?,?)", (user_id, status))

    def update_users(self, user_id, status):
        """Обновляем статус подписки"""
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `status` = ? WHERE `user_id` = ?", (status, user_id))


    def show_last_tender(self):
        """Показываем последний торг из базы"""
        with self.connection:
            last_tender = self.cursor.execute("SELECT * FROM tenders ORDER BY id DESC LIMIT 1").fetchone()
            tender = namedtuple('tender', 'Id Номер Тип Этап Описание Заказчик Ссылка_на_заказчика Ссылка_на_закупку Дата_размещения Цена')
            last_tender = tender(*last_tender)
        return last_tender


    def show_last_id(self):
        """Показываем последний ID в базе = количество торгов в общем"""
        with self.connection:
            id_last_tender = self.cursor.execute("SELECT id FROM tenders ORDER BY id DESC LIMIT 1").fetchone()
            return id_last_tender[0]

    def get_all_tenders(self):
        with self.connection:
            get_all_tenders = self.cursor.execute("SELECT number FROM tenders").fetchall()
            return get_all_tenders

    def close(self):
        """Закрываем соединение с БД """
        self.connection.close()