from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import random
import requests
import sqlite3
import datetime
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup


users = {}   # Данные о пользователе

weather = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=341ff1410c35f02ad283bd301cfd9001'

wiki_search = 'https://ru.wikipedia.org/w/api.php?action=opensearch&search={}&prop=info&format=json&inprop=url'

cb_rf_search = 'https://www.cbr-xml-daily.ru/daily_json.js'

translate_key = 'trnsl.1.1.20190405T212758Z.88c300bbd7a9189d.b35f51c6e1052bcc1bf89a46ff71533e7aac68d1'

translator_uri = "https://translate.yandex.net/api/v1.5/tr.json/translate"

geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={}&format=json"

search_api_server = "https://search-maps.yandex.ru/v1/"

search_api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

map_api_server = "http://static-maps.yandex.ru/1.x/"


class DB:  # база данных
    def __init__(self):
        conn = sqlite3.connect('server.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class NewsModel:  # class постов в базе данных
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS posts 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             start VARCHAR(100),
                             pogoda VARCHAR(1000),
                             wiki VARCHAR(100),
                             napr VARCHAR(100),
                             tran VARCHAR(100),
                             bliz VARCHAR(100),
                             from_where VARCHAR(100),
                             user_id VARCHAR(100),
                             timecode VARCHAR(100)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, level_img, level1, user_id, six, seven):
        cursor = self.connection.cursor()

        cursor.execute('''INSERT INTO posts 
                          (start, pogoda, wiki, napr, tran, bliz, from_where, user_id, timecode) 
                          VALUES (?,?,?,?,?,?,?,?,?)''', (title, content, level_img, level1, str(user_id), six, '',
                                                      seven, '1 0'))
        cursor.close()
        self.connection.commit()

    def update(self, id, what, now):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE posts SET 
                                   {} = ? 
                                   WHERE user_id = ?'''.format(what), (now, id))
        cursor.close()
        self.connection.commit()

    def get(self, news_id, what):
        cursor = self.connection.cursor()
        cursor.execute("SELECT {} FROM posts WHERE user_id = ?".format(what), ([str(news_id)]))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None, set_up=None):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        if set_up:
            rows = sorted(rows)
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM posts WHERE id = ?''', ([str(news_id)]))
        cursor.close()
        self.connection.commit()


def close_keyboard(bot, update, job_queue, chat_data):
    global reply_keyboard, markup
    reply_keyboard = [['/dice', '/timer']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    if 'job' in chat_data:
        chat_data['job'].schedule_removal()
        del chat_data['job']

    update.message.reply_text('Хорошо!', reply_markup=markup)


def start(bot, update):  # Старт
    news.insert('True', 'True', 'False', 'en-ru', 'False', 'False', update.message.chat_id)
    update.message.reply_text("Привет, я бот и я могу кое в чём тебе помочь!\nДля начала напиши город для которого ты"
                              " хотел бы получать прогноз погоды.")


def task(bot, job):  # Обработка погоды и отправка пользователю

    if news.get(job.context[0].message.chat_id, 'pogoda'):
        response = requests.post(weather.format(news.get(job.context[0].message.chat_id, 'city')))
        response = response.json()
        if response['cod'] == 200:
            descr = response['weather'][0]['description']
            temp = round(response['main']['temp'] - 273, 2)
            millibar = response['main']['pressure']
            vlazhn = response['main']['humidity']
            bot.send_message(job.context[0].message.chat_id, text='Описание - {}\nТемпература = {} цельсия\n'
                                                               'Давление(в миллибарах) - {}\nВлажность - {}%'
                             .format(descr, str(temp), str(millibar), str(vlazhn)))
            set_timer(bot, job.context[0], 24*3600, job.context[1], job.context[2])
        else:
            news.update(job.context[0].message.chat_id, 'pogoda', 'False')
            bot.send_message(job.context[0].message.chat_id, text='Кажется, такого города нет.')


def set_timer(bot, update, args, job_queue, chat_data):  # Ежедневная отправка
    global reply_keyboard, markup
    delay = int(args)+1
    job = job_queue.run_once(task, delay, context=[update, job_queue, chat_data])
    chat_data['job'] = job


def stop(bot, update):  # Конец отправки погоды
    news.update(update.message.chat_id, 'pogoda', 'False')
    update.message.reply_text('Больше не буду(\n/start для ввода города')


def timer(bot, update):
    global reply_keyboard, markup
    #  reply_keyboard = [['30 секунд', '1 минута'],
    #                  ['5 минут', 'назад']]
    #  markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Времячко",
                              reply_markup=markup)


def wiki(bot, update, mes):  # Обработка запросов по википедии
    try:
        response = requests.post(wiki_search.format(mes))
        if response:
            response = response.json()
            try:
                update.message.reply_text("Вот, что удалось найти:\n{}\nА вот ссыль: {}"
                                          .format(response[2][0], response[3][0]),
                                          reply_markup=markup)
            except Exception:
                update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа или с вашим запросом.",
                                          reply_markup=markup)
        else:
            update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа или с вашим запросом.",
                                      reply_markup=markup)
    except Exception:
        update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа или с вашим запросом.",
                                  reply_markup=markup)


def cb_rf(bot, update):  # Обработка запроса валют
    try:
        response = requests.get(cb_rf_search)
        if response:
            response = response.json()
            try:
                update.message.reply_text('Рубль - Евро: {} = 1\nРубль - Доллар: {} = 1'
                                          .format(response['Valute']['EUR']['Value'],
                                                  response['Valute']['USD']['Value']))
            except Exception:
                update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа или с вашим запросом.")
        else:
            update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа или с вашим запросом.")
    except Exception:
        update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа или с вашим запросом.")


def translater(bot, update, mes):  # Обработка запросов по переводу
    try:
        response = requests.get(
            translator_uri,
            params={
                "key": translate_key,
                "lang": news.get(update.message.chat_id, 'napr'),
                "text": mes
            })
        update.message.reply_text(
            "\n\n".join([response.json()["text"][0]]), reply_markup=markup)
    except Exception:
        update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа.",
                                  reply_markup=markup)


def geocoder(bot, update, mes):  # Отправка фото "Ближайшее..."
    try:
        geocoder_uri = geocoder_request_template = \
            "http://geocode-maps.yandex.ru/1.x/"
        response = requests.get(geocoder_uri, params={
            "format": "json",
            "geocode": news.get(update.message.chat_id, 'from_where')
        })
        if not response:
            update.message.reply_text("Ошибка выполнения запроса:")
            update.message.reply_text(geocoder_request)
            update.message.reply_text("Http статус:", response.status_code, "(", response.reason, ")")
            return
        toponym1 = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        toponym1 = ','.join(toponym1.split(' '))

        search_params = {
            "apikey": search_api_key,
            "text": mes,
            "lang": "ru_RU",
            "ll": toponym1,
        }
        response = requests.get(search_api_server, params=search_params)
        if not response:
            update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа или с вашим запросом.")
            return

        json_response = response.json()
        organization = json_response["features"][0]
        org_name = organization["properties"]["CompanyMetaData"]["name"]
        toponym2 = ','.join([str(organization['geometry']['coordinates'][0]),
                             str(organization['geometry']['coordinates'][1])])
        org_address = organization["properties"]["CompanyMetaData"]["address"]
        for_photo = org_name + '\nАдрес: ' + org_address
        #
        static_api_request = \
            "http://static-maps.yandex.ru/1.x/?l=map&pt={},ya_ru~{},pm2ntm".format(toponym1, toponym2)
        bot.sendPhoto(
            update.message.chat.id,
            static_api_request,
            caption=for_photo
        )

    except Exception:
        update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа или с вашим запросом.")


def text_m(bot, update, job_queue, chat_data):  # обработка сообщений
    global reply_keyboard, markup
    text_mes = update.message.text
    print(news.get(update.message.chat_id, 'start'))

    if news.get(update.message.chat_id, 'start') == 'True':
        news.update(update.message.chat_id, 'start', 'False4444')
        news.update(update.message.chat_id, 'city', 'text_mes')
        update.message.reply_text('Принял. Через сколько часов сделать первое оповещание(далее каждые 24 часа)?\n '
                                  'Написать нужно только число, иначе за ответ примется 12')
        return

    elif news.get(update.message.chat_id, 'start') == "False4444":
        try:
            text_mes = int(text_mes)
        except Exception:
            text_mes = 12
        set_timer(bot, update, text_mes*3600, job_queue, chat_data)
        news.update(update.message.chat_id, 'start', 'False')
        update.message.reply_text('Ok!', reply_markup=markup)

    elif news.get(update.message.chat_id, 'wiki') == 'True':
        wiki(bot, update, text_mes)
        news.update(update.message.chat_id, 'wiki', 'False')

    elif news.get(update.message.chat_id, 'tran') == 'True':
        translater(bot, update, text_mes)
        news.update(update.message.chat_id, 'tran', 'False')

    elif news.get(update.message.chat_id, 'bliz') == 'True':
        news.update(update.message.chat_id, 'bliz', 'True444')
        news.update(update.message.chat_id, 'from_where', text_mes)
        update.message.reply_text('Теперь введите то, что нужно найти(магазин, аптека и т.д.)')

    elif news.get(update.message.chat_id, 'bliz') == "True444":
        news.update(update.message.chat_id, 'bliz', 'False')
        geocoder(bot, update, text_mes)

    elif text_mes == 'Поиск Wiki':
        update.message.reply_text('Введите, что найти в Википедии', reply_markup=ReplyKeyboardRemove())
        news.update(update.message.chat_id, 'wiki', 'True')

    elif text_mes == 'Курс валют':
        cb_rf(bot, update)

    elif text_mes == 'Переводчик':
        update.message.reply_text('Ну-с, вводите то, что нужно перевести. Изначально ru-en'
                                  '\nТакже можно выбрать направление перевода.', reply_markup=markup2)
        news.update(update.message.chat_id, 'tran', 'True')

    elif text_mes == 'Ближайшее...':
        news.update(update.message.chat_id, 'bliz', 'True')
        update.message.reply_text('Введите своё местоположнение или место от которого искать(город, улица, дом)')

    elif text_mes == '30 секунд':
        update.message.reply_text('Это 0.5 минуты)')
        # set_timer(bot, update, 30, job_queue, chat_data)

    elif text_mes == '1 минута':
        update.message.reply_text('1 минута, казалось бы так мало, а что если задуматься?')
        # set_timer(bot, update, 60, job_queue, chat_data)

    elif text_mes == '5 минут':
        update.message.reply_text('Ну да, была такая песня')
        # set_timer(bot, update, 300, job_queue, chat_data)

    elif text_mes == 'один шестигранный кубик':
        update.message.reply_text(str(random.randint(1, 6)))

    elif text_mes == '2 шестигранных кубика':
        update.message.reply_text(' '.join([str(random.randint(1, 6)), str(random.randint(1, 6))]))

    elif text_mes == '20-гранный кубик':
        update.message.reply_text(str(random.randint(1, 20)))

    elif 'спасибо' in text_mes.lower():
        update.message.reply_text('Не за что)')


def help(bot, update):  # /help
    update.message.reply_text('Поиск Wiki - поиск в Википедии краткой информации по запросу пользователя.\n'
                              'Переводчик - переводы en-ru ru-en.\n'
                              'Курс валют - берётся с ЦБ РФ.\n'
                              'Ближайшее - вы вводите место откуда искать и что искать,'
                              ' а бот показвает ближайшее к месту совпадение.\n'
                              '/stop - чтобы прекратить рассылку погоды.')


def per1(bot, update):  # ревёрс переводчика
    users[update.message.chat_id]['napr'] = 'ru-en'
    update.message.reply_text("Ок, изменил")


def per2(bot, update):  # ревёрс переводчика
    users[update.message.chat_id]['napr'] = 'en-ru'
    update.message.reply_text("Ок, изменил")


def main():
    updater = Updater("812759520:AAG5XoYRenwYAj04vGQGlcgWL4uX57UfAX4")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("stop", stop))

    dp.add_handler(CommandHandler("ru-en", per1))
    dp.add_handler(CommandHandler("en-ru", per2))

    dp.add_handler(CommandHandler("set_timer", set_timer, pass_args=True, pass_job_queue=True, pass_chat_data=True))

    text_handler = MessageHandler(Filters.text, text_m, pass_job_queue=True, pass_chat_data=True)

    dp.add_handler(text_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    Artem = DB()
    news = NewsModel(Artem.get_connection())
    news.init_table()
    reply_keyboard = [['Поиск Wiki', 'Переводчик'],
                      ['Курс валют', 'Ближайшее...'],
                      ['/stop', '/help']]
    reply_keyboard2 = [['/ru-en', '/en-ru']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=False)
    main()
