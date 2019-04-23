from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import random
import json
import requests
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup


timer = {}
users = {}

weather = 'https://api.openweathermap.org/data/2.5/weather?q=Обнинск&appid=341ff1410c35f02ad283bd301cfd9001'
response = requests.post(weather)
print(response.json())