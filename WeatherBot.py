import telebot
import requests
import traceback
from telebot import types

open_weather_token = "6b5ba33aa6df3f67fb18024f6f3ad1eb"
bot = telebot.TeleBot('7707024539:AAFszGFgFe6WZsduVFT0UkcTqPvg0u3a-ng')
apikey = '66c5e677-82c2-4b32-aa11-09327f4c3635'

keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
kb = types.KeyboardButton(text="Помощь")
kb2 = types.KeyboardButton(text="Погода", request_location=True)
keyboard.add(kb, kb2)
keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.add(kb, kb2)

gl_var = 0

@bot.message_handler(commands=['start'])
def start(message):
    global gl_var
    mess = f'Привет👋, {message.from_user.first_name}! Я могу тебе рассказать какая погода в любом городе или поселке! (нужна помощь напиши: "/help")'
    if gl_var == 0:
        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=keyboard)
        gl_var = 1
    else:
        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=keyboard1)
        gl_var = 0

@bot.message_handler(commands=['help'])
def help(message):
    mess = f"""Чтобы узнать погоду любого населенного пункта следуйте данной инструкции:
Для ручного ввода напишите команду "/weather" или "Погода", далее название города или поселка.
Для автоматического ввода через геолокацию нажмите на кнопку "Погода"."""
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler(commands=['weather'])
def after_text(message):
    msg = bot.send_message(message.from_user.id, 'Введите название населенного пункта: ')
    bot.register_next_step_handler(msg, after_text_2)

def after_text_2(message):
    try:
        if  message.text == '#':
            return
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]

        mess = f"Погода в городе: {city}\nТемпература: {cur_weather}C°\nВлажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
        bot.send_message(message.chat.id, mess, parse_mode='html')
    except Exception as e:
        print('gsds', traceback.format_exc())
        if data['cod'] == '404':
            bot.send_message(message.chat.id, "🚫 Проверьте название 🚫", parse_mode='html')
            after_text(message)

@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        coord = str(message.location.longitude) + ',' + str(message.location.latitude)
        s = requests.get('https://geocode-maps.yandex.ru/1.x/?apikey=' + apikey + '&format=json&geocode=' + coord)

        if len(s.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['Components'][4]['name']) > 0:
            message.text = s.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['Components'][4]['name']
            after_text_2(message)
        else:
            bot.send_message(message.chat.id, 'Не удалось получить Ваш адрес')

@bot.message_handler()
def user_text(message):
    get_message_bot = message.text.lower()
    if get_message_bot == "помощь":
        mess = f"""Чтобы узнать погоду любого населенного пункта следуйте данной инструкции:
Для ручного ввода напишите команду "/weather" или "Погода", далее название города или поселка.
Для втоматического ввода через геолокацию нажмите на кнопку "Погода"."""
        bot.send_message(message.chat.id, mess, parse_mode='html')
    elif get_message_bot == "погода":
        msg = bot.send_message(message.from_user.id, 'Введите название населенного пункта: ')
        bot.register_next_step_handler(msg, after_text_2)
    else:
        bot.send_message(message.chat.id, "Я не понял повторите еще раз!😢", parse_mode='html')

bot.polling(none_stop=True, interval=0)