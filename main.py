from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import random
import json
import requests
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup


timer = {}
users = {}

weather = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=341ff1410c35f02ad283bd301cfd9001'


def close_keyboard(bot, update, job_queue, chat_data):
    global reply_keyboard, markup
    reply_keyboard = [['/dice', '/timer']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    if 'job' in chat_data:
        chat_data['job'].schedule_removal()
        del chat_data['job']

    update.message.reply_text('Хорошо, вернулся сейчас!', reply_markup=markup)


def start(bot, update):
    users[update.message.chat_id] = {'start': True, 'pogoda': True}
    update.message.reply_text("Привет, я бот и я могу кое в чём тебе помочь!\nДля начала напиши город для которого ты"
                              " хотел бы получать прогноз погоды.")


def task(bot, job):
    if users[job.context]['pogoda']:
        response = requests.post(weather.format(users[job.context]['city']))
        response = requests.post(response).json()
        if response['cod'] == 200:
            descr = response['weather'][0]['description']
            temp = response['main']['temp'] - 273
            millibar = response['main']['pressure']
            vlazhn = response['main']['humidity']
            bot.send_message(job.context, text='Описание - {}\nТемпература = {}\n'
                                               'Давление(в миллибарах) - {}\nВлажность - {}'
                             .format(descr, str(temp), str(millibar), str(vlazhn)))
        else:
            users[job.context]['pogoda'] = False
            bot.send_message(job.context, text='Кажется, такого города нет.')


def set_timer(bot, update, args, job_queue, chat_data):
    global reply_keyboard, markup
    reply_keyboard = [['/close']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    delay = int(args)
    job = job_queue.run_once(task, delay, context=update.message.chat_id)

    chat_data['job'] = job


def stop(bot, update):
    users[update.message.chat_id]['pogoda'] = False
    update.message.reply_text('Больше не буду(')


def timer(bot, update):
    global reply_keyboard, markup
    reply_keyboard = [['30 секунд', '1 минута'],
                      ['5 минут', 'назад']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Времячко",
                              reply_markup=markup)


def text_m(bot, update, job_queue, chat_data):
    global reply_keyboard, markup
    text_mes = update.message.text
    if users[update.message.chat_id]['start']:
        users[update.message.chat_id]['start'] = 'False'
        users[update.message.chat_id]['city'] = text_mes
        update.message.reply_text('Принял. Через сколько часов сделать первое оповещание(далее каждые 24 часа).\n '
                                  'Написать нужно только число, иначе за ответ примется 12')
        return
    elif users[update.message.chat_id]['start'] == "False":
        try:
            text_mes = int(text_mes)
        except Exception:
            text_mes = 12
        set_timer(bot, update, text_mes*60, job_queue, chat_data)
        users[update.message.chat_id]['start'] = False
        update.message.reply_text('Ok!', reply_markup=markup)
    elif text_mes == '30 секунд':
        set_timer(bot, update, 30, job_queue, chat_data)
    elif text_mes == '1 минута':
        set_timer(bot, update, 60, job_queue, chat_data)
    elif text_mes == '5 минут':
        set_timer(bot, update, 300, job_queue, chat_data)
    elif text_mes == 'один шестигранный кубик':
        update.message.reply_text(str(random.randint(1, 6)))
    elif text_mes == '2 шестигранных кубика':
        update.message.reply_text(' '.join([str(random.randint(1, 6)), str(random.randint(1, 6))]))
    elif text_mes == '20-гранный кубик':
        update.message.reply_text(str(random.randint(1, 20)))


def help(bot, update):
    update.message.reply_text('Поиск Wiki - поиск в Википедии краткой информации по запросу пользователя.\n'
                              'Переводчик - переводы en-ru ru-en.\n'
                              'Курс валют - берётся с ЦБ РФ.\n'
                              'Ближайшее - вы вводите место откуда искать и что искать, а бот показвает ближайшее к месту совпадение.\n'
                              '/stop - чтобы прекратить рассылку погоды.')


def main():
    updater = Updater("812759520:AAG5XoYRenwYAj04vGQGlcgWL4uX57UfAX4")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))


    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("timer", timer))

    dp.add_handler(CommandHandler("close", close_keyboard, pass_job_queue=True, pass_chat_data=True))

    dp.add_handler(CommandHandler("set_timer", set_timer, pass_args=True, pass_job_queue=True, pass_chat_data=True))

    text_handler = MessageHandler(Filters.text, text_m, pass_job_queue=True, pass_chat_data=True)

    dp.add_handler(text_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    reply_keyboard = [['Поиск Wiki', 'Переводчик'],
                      ['Курс валют', 'Ближайшее...'],
                      ['/stop', '/help']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    main()

