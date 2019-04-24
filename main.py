from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import random
import json
import requests
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup


timer = {}
users = {}

weather = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=341ff1410c35f02ad283bd301cfd9001'

wiki_search = 'https://ru.wikipedia.org/w/api.php?action=opensearch&search={}&prop=info&format=json&inprop=url'

cb_rf_search = 'https://www.cbr-xml-daily.ru/daily_json.js'

translate_key = 'trnsl.1.1.20190405T212758Z.88c300bbd7a9189d.b35f51c6e1052bcc1bf89a46ff71533e7aac68d1'

translator_uri = "https://translate.yandex.net/api/v1.5/tr.json/translate"



def close_keyboard(bot, update, job_queue, chat_data):
    global reply_keyboard, markup
    reply_keyboard = [['/dice', '/timer']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    if 'job' in chat_data:
        chat_data['job'].schedule_removal()
        del chat_data['job']

    update.message.reply_text('Хорошо!', reply_markup=markup)


def start(bot, update):
    users[update.message.chat_id] = {'start': True, 'pogoda': True, 'wiki': False, 'napr': 'en-ru', 'tran': False}
    update.message.reply_text("Привет, я бот и я могу кое в чём тебе помочь!\nДля начала напиши город для которого ты"
                              " хотел бы получать прогноз погоды.")


def task(bot, job):
    if users[job.context[0].message.chat_id]['pogoda']:
        response = requests.post(weather.format(users[job.context[0].message.chat_id]['city']))
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
            users[job.context[0].message.chat_id]['pogoda'] = False
            bot.send_message(job.context[0].message.chat_id, text='Кажется, такого города нет.')


def set_timer(bot, update, args, job_queue, chat_data):
    global reply_keyboard, markup
    delay = int(args)+1
    job = job_queue.run_once(task, delay, context=[update, job_queue, chat_data])
    chat_data['job'] = job


def stop(bot, update):
    users[update.message.chat_id]['pogoda'] = False
    update.message.reply_text('Больше не буду(\n/start для ввода города')


def timer(bot, update):
    global reply_keyboard, markup
    #  reply_keyboard = [['30 секунд', '1 минута'],
    #                  ['5 минут', 'назад']]
    #  markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Времячко",
                              reply_markup=markup)


def wiki(bot, update, mes):
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


def cb_rf(bot, update):
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


def translater(bot, update, mes):
    try:
        response = requests.get(
            translator_uri,
            params={
                "key": translate_key,
                "lang": users[update.message.chat_id]['napr'],
                "text": mes
            })
        update.message.reply_text(
            "\n\n".join([response.json()["text"][0]]), reply_markup=markup)
    except Exception:
        update.message.reply_text("Что-то пошло не так. Возможно с сервером лажа.",
                                  reply_markup=markup)


def text_m(bot, update, job_queue, chat_data):
    global reply_keyboard, markup
    text_mes = update.message.text

    if users[update.message.chat_id]['start'] == True:
        users[update.message.chat_id]['start'] = 'False4444'
        users[update.message.chat_id]['city'] = text_mes
        update.message.reply_text('Принял. Через сколько часов сделать первое оповещание(далее каждые 24 часа)?\n '
                                  'Написать нужно только число, иначе за ответ примется 12')
        return

    elif users[update.message.chat_id]['start'] == "False4444":
        try:
            text_mes = int(text_mes)
        except Exception:
            text_mes = 12
        set_timer(bot, update, text_mes*3600, job_queue, chat_data)
        users[update.message.chat_id]['start'] = False
        update.message.reply_text('Ok!', reply_markup=markup)

    elif users[update.message.chat_id]['wiki']:
        wiki(bot, update, text_mes)
        users[update.message.chat_id]['wiki'] = False

    elif users[update.message.chat_id]['tran']:
        translater(bot, update, text_mes)
        users[update.message.chat_id]['tran'] = True

    elif text_mes == 'Поиск Wiki':
        update.message.reply_text('Введите, что найти в Википедии', reply_markup=ReplyKeyboardRemove())
        users[update.message.chat_id]['wiki'] = True

    elif text_mes == 'Курс валют':
        cb_rf(bot, update)
    elif text_mes == 'Переводчик':
        update.message.reply_text('Ну-с, вводите то, что нужно перевести. Изначально ru-en'
                                  '\nТакже можно выбрать направление перевода.', reply_markup=markup2)
        users[update.message.chat_id]['tran'] = True

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


def help(bot, update):
    update.message.reply_text('Поиск Wiki - поиск в Википедии краткой информации по запросу пользователя.\n'
                              'Переводчик - переводы en-ru ru-en.\n'
                              'Курс валют - берётся с ЦБ РФ.\n'
                              'Ближайшее - вы вводите место откуда искать и что искать,'
                              ' а бот показвает ближайшее к месту совпадение.\n'
                              '/stop - чтобы прекратить рассылку погоды.')


def per1(bot, update):
    users[update.message.chat_id]['napr'] = 'ru-en'
    update.message.reply_text("Ок, изменил")


def per2(bot, update):
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
    reply_keyboard = [['Поиск Wiki', 'Переводчик'],
                      ['Курс валют', 'Ближайшее...'],
                      ['/stop', '/help']]
    reply_keyboard2 = [['/ru-en', '/en-ru']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=False)
    main()

