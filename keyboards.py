from telebot import types

def generate_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton(text="⛅Погода в Канаде")
    btn1 = types.KeyboardButton(text="📖Хочу почитать!")
    btn2 = types.KeyboardButton(text="📨Сделать рассылку")
    keyboard.row(btn, btn1, btn2)
    return keyboard

def generate_inline_btn(url):
    keyboard = types.InlineKeyboardMarkup()
    btn_more = types.InlineKeyboardButton(text="Подробнее", url=url)
    keyboard.row(btn_more)
    return keyboard

def generate_btn():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton(text="Уверен")
    btn1 = types.KeyboardButton(text="Отмена")
    keyboard.row(btn)
    keyboard.row(btn1)
    return keyboard

