import psycopg2
from telebot import TeleBot
import requests
import datetime
from keyboards import generate_main_menu, generate_inline_btn, generate_btn

token = "5612647929:AAF6oX53ZaildBvo4Q6ZW2WbUOK1dw8SNPQ"
bot = TeleBot(token)


data_base = psycopg2.connect(
    host='localhost',
    user='postgres',
    database='Telegram_bot',
    password='123456'
    )
cursor = data_base.cursor()
cursor.execute(""" CREATE TABLE IF NOT EXISTS users(
                user_id SERIAL PRIMARY KEY,
                user_name TEXT NOT NULL UNIQUE
        ) """)
data_base.commit()


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    bot.send_message(chat_id, f'Здравствуйте {first_name} !')
    if data_base is None:
        cursor.execute('INSERT INTO users(user_id, user_name) VALUES (%s,%s)', (chat_id, first_name))
    cursor.execute('SELECT user_name FROM users WHERE user_id=%s', (chat_id,))
    cursor.fetchall()
    data_base.commit()
    choose_catalog(message)

def choose_catalog(message):
    chat_id = message.chat.id
    user_message = bot.send_message(chat_id, "Нажмите на любую интересующую Вас кнопку ", reply_markup=generate_main_menu())
    bot.register_next_step_handler(user_message, show_products)

def show_products(message):
    chat_id = message.chat.id

    if message.text == '⛅Погода в Канаде':
        weather(message)

    elif message.text == "📖Хочу почитать!":
        bot.send_photo(
            chat_id,
            photo=open('img/img.png', 'rb'),
            caption="Идеальный карманный справочник для быстрого ознакомления с особенностями работы разработчиков на Python."
                    "Вы найдете море краткой информации о типах и операторах в Python, именах специальных методов, "
                    "встроенных функциях, исключениях и других часто используемых стандартных модулях",
            reply_markup=generate_inline_btn(url='https://drive.google.com/file/d/1Xs_YjOLgigsuKl17mOnR_488MdEKloCD/view'))

    elif message.text == "📨Сделать рассылку":
        bot.send_message(chat_id, "Вы выбрали рассылку всем пользователям. Вы уверен что хотите это сделать?", reply_markup=generate_btn())

    elif message.text == "Уверен":
        bot.send_message(chat_id, "Введите сообщение, которое хотите отправить всем пользователям.")

        cursor.execute(f'SELECT user_id FROM users WHERE user_id=%s', (chat_id,))
        data = cursor.fetchone()
        if data is None:
            user_id = ['message.chat.id']
            cursor.execute('INSERT INTO users VALUES (%s)', (user_id,))
            data_base.commit()

    elif message.text == "Отмена":
        bot.send_message(chat_id, "Диалог завершен!")
        choose_catalog(message)
        return

    bot.register_next_step_handler(message, show_products)

def weather(message):
    s_city = "Ottawa,CA"
    city_id = 0
    appid = "4e25bdc5a6894e18c9709982370e4dcb"
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': appid})
        data = res.json()
        cities = ["{} ({})".format(d['name'], d['sys']['country']) for d in data['list']]
        print("city:", cities)
        city_id = data['list'][0]['id']
        print('city_id=', city_id)
    except Exception as e:
        print("Exception (find):", e)
        pass

    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Fog": "Туман \U0001F32B"
    }

    try:
        r = requests.get("http://api.openweathermap.org/data/2.5/weather",
                            params={'id': city_id, 'units': 'metric', 'lang': 'ca', 'APPID': appid})
        data = r.json()
        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно, не пойму что там за погода!"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        bot.reply_to(message,
                     f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                     f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
                     f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                     f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность "
                     f"дня: {length_of_the_day}\n "
                     f"***Хорошего дня!***")

    except:
        bot.reply_to(message, "Проверьте название города!")

if __name__ == '__main__':
    bot.polling(none_stop=True)

