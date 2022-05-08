import aiogram
import asyncio
from datetime import datetime
import config
import logging
import requests
from sqlighter import SQLighter

logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = aiogram.Bot(token=config.API_TOKEN)
dp = aiogram.dispatcher.Dispatcher(bot)


# инициализируем соединение с БД
datbas = SQLighter('db.db')
db = [None]

@dp.message_handler(commands=['start'])
async def send_welcome(message: aiogram.types.Message):
    mess = (f'Привет, <b>{message.from_user.first_name}</b>! Меня зовут Антон Чубарь. В '
    f'9 классе я всерьёз задумался о своём будущем и твёрдо решил, что пора становиться взрослее, '
    f'слазить с плеч родителей и делать деньги самостоятельно. Сейчас мне <b>21 год</b>, я успешный '
    f'миллионер, трейдер. И я могу помочь тебе добиться ТОГО ЖЕ, ЧЕГО ДОБИЛСЯ Я всего за <b>5000 рублей</b>!'
    f' Смотри курсы валют, подписывайся на ежедневные обновления валют на бирже и БУДЬ УСПЕШЕН!')
    url="https://sun9-82.userapi.com/s/v1/if1/SJv4SU-iaqJi7Tqa3FloojP7GsNEyKT8yk39CIZj0GzFkIDMn-MNpQsXMclSbgW37Sh1wV-o.jpg?size=540x1080&quality=96&type=album"
    await bot.send_photo(message.from_user.id, url, caption=mess, parse_mode='html')
    #await bot.send_message(message.from_user.id, text=mess, parse_mode='html')

@dp.message_handler(commands=['subscribe'])
async def subcribe(message: aiogram.types.Message):
    if not datbas.subscriber_exists(message.from_user.id):
        datbas.add_subscriber(message.from_user.id)
    else:
        datbas.update_subscription(message.from_user.id, True)
    await message.answer("Вы успешно подписались на рассылку!\n"
                        "Ждите актуальные курсы валют каждый день!")
                  
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: aiogram.types.Message):
	if not datbas.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
		datbas.add_subscriber(message.from_user.id, False)
		await message.answer("Вы итак не подписаны.")
	else:
		# если он уже есть, то просто обновляем ему статус подписки
		datbas.update_subscription(message.from_user.id, False)
		await message.answer("Вы успешно отписались от рассылки.")

@dp.message_handler(commands=['toha'])
async def website(message: aiogram.types.Message):
    url="https://sun9-82.userapi.com/s/v1/if1/SJv4SU-iaqJi7Tqa3FloojP7GsNEyKT8yk39CIZj0GzFkIDMn-MNpQsXMclSbgW37Sh1wV-o.jpg?size=540x1080&quality=96&type=album"
    await bot.send_photo(message.from_user.id, url)

@dp.message_handler(commands=["convert"])
async def valuta(message: aiogram.types.Message):
    conv1 = aiogram.types.KeyboardButton("USD -> RUR")
    conv2 = aiogram.types.KeyboardButton("RUR -> USD")
    markup = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(conv1, conv2)
    await bot.send_message(message.from_user.id, "Курс чего к чему Вы хотите узнать?", reply_markup=markup)

@dp.message_handler(commands=['exchange'])  
async def exchange_command(message: aiogram.types.Message):  
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
    if message.text == "USD -> RUR" or message.text == "RUR -> USD":
        db.append(message.text)
        await bot.send_message(message.from_user.id, "Введите сумму, которую хотите ковертировать")
    elif db[-1] == "USD -> RUR" and message.text.isdigit():
        req = requests.get("https://yobit.net/api/3/ticker/usd_rur")
        response = req.json()
        doll = response["usd_rur"]["sell"]
        answ = f'${message.text} = ₽{int(message.text) * doll}'
        await bot.send_message(message.from_user.id, answ)
    elif db[-1] == "RUR -> USD" and message.text.isdigit():
        req = requests.get("https://yobit.net/api/3/ticker/usd_rur")
        response = req.json()
        doll = response["usd_rur"]["sell"]
        answ = f'₽{message.text} = ${int(message.text) / doll}'
        await bot.send_message(message.from_user.id, answ)
    else:
        await bot.send_message(message.from_user.id, "Проверьте правильность ввода")

@dp.callback_query_handler(lambda call: True)  
async def iq_callback(query: aiogram.types.CallbackQuery):  
    data = query.data  
    if data.startswith('get-'):  
        await get_ex_callback(query)

async def get_ex_callback(query):  
    await bot.answer_callback_query(query.id)  
    await send_exchange_result(query.message, query.data[4:])

async def send_exchange_result(message, ex_code):  
    ex = await get_exchange(ex_code)  
    await bot.send_message(  
        message.chat.id, ex, parse_mode='HTML'  
    )

async def get_exchange(code):
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

async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        # ruble
        rur = requests.get("https://yobit.net/api/3/ticker/usd_rur")
        resp_rur = rur.json()
        sell_rur = round(resp_rur["usd_rur"]["sell"], 2)
        buy_rur = round(resp_rur["usd_rur"]["buy"], 2)
        # bitcoin
        btc = requests.get("https://yobit.net/api/3/ticker/btc_usd")
        resp_btc = btc.json()
        sell_btc = round(resp_btc["btc_usd"]["sell"], 2)
        buy_btc = round(resp_btc["btc_usd"]["buy"], 2)
        # etherium
        eth = requests.get("https://yobit.net/api/3/ticker/eth_usd")
        resp_eth = eth.json()
        sell_eth = round(resp_eth["eth_usd"]["sell"], 2)
        buy_eth = round(resp_eth["eth_usd"]["buy"], 2)
        # получаем список подписчиков бота
        subscriptions = datbas.get_subscriptions()
        # картинка для привлечения внимания
        url = "https://s0.rbk.ru/rbcplus_pics/media/img/0/78/296433791100780.png"
        # отправляем курсы валют всем, кто подписан
        for s in subscriptions:
            await bot.send_photo(
                s[1],
                url,
                caption=f'Доброго времени суток, дорогой подпсчик!\n'
                f'Сейчас {datetime.now().strftime("%d-%m-%Y %H:%M:%S")},\n'
                f'и на момент отправки сообщения на бирже следующий курс валют:\n'
                f'<b>USD:</b> Продажа {sell_rur}\t Покупка {buy_rur}\n'
                f'<b>BTC:</b> Продажа {sell_btc}\t Покупка {buy_btc}\n'
                f'<b>ETH:</b> Продажа {sell_eth}\t Покупка {buy_eth}\n',
                parse_mode='html'
            )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # По стандарту 43200 секунд == 12 часов. Для проверки 
    # можно поставить, например, 10 секунд и увидеть, что 
    # лежит в рассылке
    loop.create_task(scheduled(43200))
    aiogram.executor.start_polling(dp)
