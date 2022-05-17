# def Dicts( dictionary):
#     if dictionary == "RU":
#         a = Russian()
#         return a
#     elif dictionary == "UK":
#         a = Ukrainian()
#         return a
#     elif dictionary == "EN":
#         a = English()
#         return a

def welmes(s) -> str:
    welcome_mess = (f'Привет, <b>{s}</b>! Меня зовут Антон Чубарь. В '
    f'9 классе я всерьёз задумался о своём будущем и твёрдо решил, что пора становиться взрослее, '
    f'слазить с плеч родителей и делать деньги самостоятельно. Сейчас мне <b>21 год</b>, я успешный '
    f'миллионер, трейдер. И я могу помочь тебе добиться ТОГО ЖЕ, ЧЕГО ДОБИЛСЯ Я всего за <b>5000 рублей</b>!'
    f' Смотри курсы валют, подписывайся на ежедневные обновления валют на бирже и БУДЬ УСПЕШЕН!')
    return welcome_mess

def anekdot() -> tuple:
    anek = '''Таксист и пьяный пассажир.
    -Куда вам?
    -Не хочу к удавам...
    -Куда вам надо?
    -А, ну если надо к удавам, поехали к удавам.
    '''
    url = "https://sun1-98.userapi.com/s/v1/if2/_PzAOxXAb20uyAyC5tta6wGU1Bf4WoEJM9nuHy8D3C21Gp-GXCBH3kDLZF-G726SgTESSaSwtFDrgwqujxXVMCWF.jpg?size=1284x1179&quality=95&type=album"
    return anek, url
