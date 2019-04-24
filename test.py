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
geocoder_uri = geocoder_request_template = \
        "http://geocode-maps.yandex.ru/1.x/"
search_api_server = "https://search-maps.yandex.ru/v1/"

search_api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

search_params = {
            "apikey": search_api_key,
            "text": 'аптека',
            "lang": "ru_RU",
            "ll": '36.61006,55.09681',
        }

response = requests.get("http://static-maps.yandex.ru/1.x/?l=map&pt={},~{},pm2nt".format('36.61006,55.09681', '36.51006,55.09681'))
print(response)