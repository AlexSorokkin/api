from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import random
import json
import requests
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup


timer = {}
users = {}

weather = 'https://api.openweathermap.org/data/2.5/weather?q=Обнинск&appid=341ff1410c35f02ad283bd301cfd9001'
wiki_search = 'https://ru.wikipedia.org/w/api.php?action=opensearch&search={}&prop=info&format=json&inprop=url'
cb_rf_search = 'https://www.cbr-xml-daily.ru/daily_json.js'
response = requests.get(cb_rf_search).json()

print(response['Valute']['USD']['Value'])
