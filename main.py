from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import random
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup


timer = {}
users = {}



def close_keyboard(bot, update, job_queue, chat_data):
    global reply_keyboard, markup
    reply_keyboard = [['/dice', '/timer']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    if 'job' in chat_data:
        chat_data['job'].schedule_removal()
        del chat_data['job']

    update.message.reply_text('Хорошо, вернулся сейчас!', reply_markup=markup)


def start(bot, update):
    users[update.message.chat_id] = {'start': True, 'pogoda': False}
    update.message.reply_text("Привет, я бот и я могу кое в чём тебе помочь!\nДля начала напиши город для которого ты"
                              " хотел бы получать прогноз погоды.",
                              reply_markup=markup)


def task(bot, job):
    bot.send_message(job.context, text='Вернулся!')


def set_timer(bot, update, args, job_queue, chat_data):
    global reply_keyboard, markup
    reply_keyboard = [['/close']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    delay = int(args)
    job = job_queue.run_once(task, delay, context=update.message.chat_id)

    chat_data['job'] = job

    update.message.reply_text('Вернусь через {} сек!'.format(str(delay)), reply_markup=markup)


def dice(bot, update):
    global reply_keyboard, markup
    reply_keyboard = [['один шестигранный кубик', '2 шестигранных кубика'],
                      ['20-гранный кубик', 'назад']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Кубики',
                              reply_markup=markup)


def timer(bot, update):
    global reply_keyboard, markup
    reply_keyboard = [['30 секунд', '1 минута'],
                      ['5 минут', 'назад']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Времячко",
                              reply_markup=markup)


def echo(bot, update, job_queue, chat_data):
    global reply_keyboard, markup
    text_mes = update.message.text
    if text_mes == 'назад':
        reply_keyboard = [['/dice', '/timer']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text("Ok",
                                  reply_markup=markup)
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


def main():
    updater = Updater("812759520:AAG5XoYRenwYAj04vGQGlcgWL4uX57UfAX4")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("dice", dice))
    dp.add_handler(CommandHandler("timer", timer))

    dp.add_handler(CommandHandler("close", close_keyboard, pass_job_queue=True, pass_chat_data=True))

    dp.add_handler(CommandHandler("set_timer", set_timer, pass_args=True, pass_job_queue=True, pass_chat_data=True))

    text_handler = MessageHandler(Filters.text, echo, pass_job_queue=True, pass_chat_data=True)

    dp.add_handler(text_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    reply_keyboard = [['/dice', '/timer']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    main()

