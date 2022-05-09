import aiogram
from datetime import datetime
import logging
import requests
import re
import time

import text
from sqlighter import SQLighter
from config import API_TOKEN
from os import environ

logging.basicConfig(level=logging.INFO)

# инициализируем бота
# API_TOKEN = environ.get("API_KEY")
bot = aiogram.Bot(token=API_TOKEN)
dp = aiogram.dispatcher.Dispatcher(bot)


# инициализируем соединение с БД
datbas = SQLighter('db.db')
db = [None]

@dp.message_handler(commands=['start'])
async def send_welcome(message: aiogram.types.Message):
    '''Обработчик команды /start. Приветствие пользователя'''
    mess = text.welmes(message.from_user.full_name)
    url="https://sun9-82.userapi.com/s/v1/if1/SJv4SU-iaqJi7Tqa3FloojP7GsNEyKT8yk39CIZj0GzFkIDMn-MNpQsXMclSbgW37Sh1wV-o.jpg?size=540x1080&quality=96&type=album"
    await bot.send_photo(message.from_user.id, url, caption=mess, parse_mode='html')

@dp.message_handler(commands=['toha'])
async def website(message: aiogram.types.Message):
    '''Обработчик команды /toha. Выводит фото успешного человека'''
    url="https://sun9-82.userapi.com/s/v1/if1/SJv4SU-iaqJi7Tqa3FloojP7GsNEyKT8yk39CIZj0GzFkIDMn-MNpQsXMclSbgW37Sh1wV-o.jpg?size=540x1080&quality=96&type=album"
    await bot.send_photo(message.from_user.id, url, caption="Look at this perfect man")

@dp.message_handler(commands=["convert"])
async def valuta(message: aiogram.types.Message):
    '''Обработчик команды /convert. Запускает сценарий конвертации валюты'''
    conv1 = aiogram.types.KeyboardButton("USD -> RUR")
    conv2 = aiogram.types.KeyboardButton("RUR -> USD")
    markup = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(conv1, conv2)
    await bot.send_message(message.from_user.id, "Курс чего к чему Вы хотите узнать?", reply_markup=markup)

@dp.message_handler(commands=['exchange'])  
async def exchange_command(message: aiogram.types.Message):
    '''Обработчик команды /exchange. Показывает Inline-кнопки и обрабатывает
        нажатия на них'''  
    keyboard = aiogram.types.InlineKeyboardMarkup()  
    keyboard.row(  
        aiogram.types.InlineKeyboardButton('USD', callback_data='get-USD')  
    )  
    keyboard.row(  
        aiogram.types.InlineKeyboardButton('BTC', callback_data='get-BTC'),  
        aiogram.types.InlineKeyboardButton('ETH', callback_data='get-ETH')  
    )  

    await bot.send_message(  
        message.from_user.id,   
        'Click on the currency of choice:',  
        reply_markup=keyboard  
    )

@dp.message_handler(content_types=['text'])
async def convert(message: aiogram.types.Message):
    '''Оработчик текстовых сообщений. Используется конвертером.
        Если прошлое сообщение от пользователя было командами конвертера,
        то запускается сценарий конвертации. Иначе выводится сообщение об
        ошибке ввода'''
    mes = re.sub("[^0-9]", "", message.text)
    if message.text == "USD -> RUR" or message.text == "RUR -> USD":
        db.append(message.text)
        await bot.send_message(message.from_user.id, "Введите сумму, которую хотите ковертировать")
    elif db[-1] == "USD -> RUR" and mes.isdigit():
        req = requests.get("https://yobit.net/api/3/ticker/usd_rur")
        response = req.json()
        doll = response["usd_rur"]["sell"]
        answ = f'${message.text} = ₽{float(message.text) * doll}'
        await bot.send_message(message.from_user.id, answ)
    elif db[-1] == "RUR -> USD" and mes.isdigit():
        req = requests.get("https://yobit.net/api/3/ticker/usd_rur")
        response = req.json()
        doll = response["usd_rur"]["sell"]
        answ = f'₽{message.text} = ${float(message.text) / doll}'
        await bot.send_message(message.from_user.id, answ)
    elif message.text == "РАССМЕШИ МЕНЯ":
        url = "https://sun1-98.userapi.com/s/v1/ig2/Qda4VVsQk0Zf0hrSLPGrDSSkVMeqSk-I8awf6obn_4cwOZl_aHlYrcOS-MwJqhW--oKNXS-QvKFPQX-tyTY8ln6z.jpg?size=1279x1424&quality=96&type=album"
        await bot.send_photo(message.from_user.id, url, caption="Вы готовы, дети?")
        time.sleep(2)
        mess = text.anekdot()
        keyboard = aiogram.types.InlineKeyboardMarkup()
        button = aiogram.types.InlineKeyboardButton('Больше такого тут 👉🏻', url='https://vk.com/jumoreski')
        keyboard.add(button)
        await bot.send_photo(message.from_user.id, mess[1], caption=mess[0], reply_markup=keyboard)       
    else:
        await bot.send_message(message.from_user.id, "Хотите шутку? Напишите в чат РАССМЕШИ МЕНЯ")

@dp.callback_query_handler(lambda call: True)  
async def iq_callback(query: aiogram.types.CallbackQuery):
    '''Обработчик call-back'ов. Если callback начинается с get-, то
        запускается сценарий отображения курса валюты'''  
    data = query.data  
    if data.startswith('get-'):  
        await get_ex_callback(query)

async def get_ex_callback(query):
    '''Промежуточная функция сценария отображения курса валюты'''  
    await bot.answer_callback_query(query.id)  
    await send_exchange_result(query.message, query.data[4:])

async def send_exchange_result(message, ex_code):
    '''Вызывает функцию получения курса нужной валюты
        и отправляет её пользователю'''  
    ex = await get_exchange(ex_code)  
    await bot.send_message(  
        message.chat.id, ex, parse_mode='HTML'  
    )

async def get_exchange(code):
    '''На вход получает одну из трёх строк с названием валюты.
        Возвращает строку с текущим временем и актуальным курсом'''
    if code == "USD":
        req = requests.get("https://yobit.net/api/3/ticker/usd_rur")
        response = req.json()
        sell_price = response["usd_rur"]["sell"]
        answ = f'На момент {datetime.now().strftime("%d-%m-%Y %H:%M:%S")} Доллар торгуется по {sell_price} рублей'
        return answ
    elif code == "BTC":
        req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
        response = req.json()
        sell_price = response["btc_usd"]["sell"]
        answ = (f'На момент {datetime.now().strftime("%d-%m-%Y %H:%M:%S")} биткоин торгуется по {sell_price}$')
        return answ
    elif code == "ETH":
        req = requests.get("https://yobit.net/api/3/ticker/eth_usd")
        response = req.json()
        sell_price = response["eth_usd"]["sell"]
        answ = (f'На момент {datetime.now().strftime("%d-%m-%Y %H:%M:%S")} эфир торгуется по {sell_price}$')
        return answ


if __name__ == "__main__":
    aiogram.executor.start_polling(dp)
