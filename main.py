# импорт нужных модулей и библиотек
import constants
import telebot
from telebot import types
from FlightRadar24 import FlightRadar24API
from datetime import datetime, timedelta
from pytz import timezone
from database import DB
import requests
import geopy.distance
import schedule
import time
import threading
from telegram_bot_pagination import InlineKeyboardPaginator
import formatting
import json
import random

selected = None
selected_date = None
# объявление экземпляров классов
fr_api = FlightRadar24API()
TOKEN = constants.TOKEN
bot = telebot.TeleBot(TOKEN)
db = DB("/Users/fedorfatekhov/Desktop/telegram_bot/telegram_bot_db.db")
with open("cities.json", "r") as f:
    cities = json.load(f)
    f.close()


@bot.message_handler(commands=["start"])
def start(message):
    """Send welcome message to user"""
    s = "I am a Flight Track Bot and I will help all aviation enthusiasts around the world\n"
    bot.send_message(
        message.chat.id,
        f"Hi,<b>{message.from_user.first_name}</b>\n\n{s}",
        parse_mode="HTML",
    )


bot.set_my_commands(
    [
        telebot.types.BotCommand("/start", "Start bot"),
        telebot.types.BotCommand("/flight", "Find flight by registration number"),
        telebot.types.BotCommand(
            "/ticket", "Find cheapest ticket from your home airport"
        ),
        telebot.types.BotCommand("/registration", "Set your home airport"),
        telebot.types.BotCommand("/change", "Change your home airport"),
        telebot.types.BotCommand("/gif", "Get an aviation gif"),
        telebot.types.BotCommand("/stats", "Get your last searched flights"),
    ]
)


@bot.message_handler(commands=["help"])
def help_handler(message):
    bot.send_message(message.from_user.id, constants.HELP)


# обработчки для команды регистарции
@bot.message_handler(commands=["registration"])
def reg_person(message):
    """Check user in DB if user is new add him to DB"""
    if not db.check_user_in_db(message.chat.id):
        bot.send_message(message.chat.id, "Enter your home AIRPORT")
        bot.register_next_step_handler(message, get_airport)
    else:
        bot.send_message(
            message.chat.id,
            "You are already registered! Enjoy our bot.\nFor help type: /help",
        )


def get_airport(message):
    """Get home airport from user and add it to DB"""
    airport = f"<b>{message.text}</b>"
    bot.send_message(
        message.chat.id,
        f"Thank you for registering. Your home airport is now {airport}",
        parse_mode="HTML",
    )
    db.add_user(
        message.from_user.id, message.text
    )  # записываем введенный аэропорт в БД, с помомщью запроса


@bot.message_handler(commands=["change"])
def change_airport(message):
    bot.send_message(message.chat.id, "Enter your new home airport")
    print(db.get_user_id(message.from_user.id))
    bot.register_next_step_handler(message, get_new_airport)


@bot.message_handler(commands=["gif"])
def gif_sender(message):
    """Get url of a gif and send it to user"""
    url = get_gif_url()
    bot.send_document(message.chat.id, url)


def get_new_airport(message):
    new_port = message.text
    db.change_airport(
        message.from_user.id, new_port
    )  # обновляем таблицу в БД с помощью INSERT
    bot.send_message(message.chat.id, f"All set! Your new home airport is {new_port}")


def get_bounds(message):
    """Find flight by geo bounds"""
    bounds = fr_api.get_bounds_by_point(
        message.location.latitude, message.location.longitude, 250000
    )
    flight = fr_api.get_flights(bounds=bounds)[0]
    return flight


def get_url(message, by):
    if by == "location":
        flight = get_bounds(message)
    else:
        flight = fr_api.get_flights(registration=message.text)[0]

    flight_details = fr_api.get_flight_details(flight)
    flight.set_flight_details(flight_details)
    url = flight.aircraft_images["medium"][0]["src"]
    return url


def get_info(message, by):
    if by == "location":
        flight = get_bounds(message)
    else:
        flight = fr_api.get_flights(registration=message.text)[0]

    flight_details = fr_api.get_flight_details(flight)
    flight.set_flight_details(flight_details)
    info = [
        flight.registration,
        flight.aircraft_model,
        flight.airline_name,
        flight.origin_airport_name,
        flight.destination_airport_name,
        flight.ground_speed,
        flight.altitude,
        flight.heading,
        flight.time_details,
        flight.destination_airport_iata,
        flight.origin_airport_iata,
    ]
    return info


def ticket_price_handler(message):
    home_airport = db.get_home_airport(message.from_user.id)
    url = constants.API_URL
    dest_and_time = message.text.split(" ")
    querystring = {
        "origin": f"{home_airport}",
        "page": "None",
        "currency": "USD",
        "depart_date": f"{selected_date}",
        "destination": f"{selected}",
    }

    headers = {
        "X-Access-Token": f"{constants.X_Access_Token}",
        "X-RapidAPI-Key": f"{constants.X_RapidAPI_Key}",
        "X-RapidAPI-Host": f"{constants.X_RapidAPI_Host}",
    }

    response = requests.get(url, headers=headers, params=querystring).json()

    airlines = fr_api.get_airlines()
    key = list(response["data"].keys())[0]
    ticket_info = response["data"][key]
    ticket_info_keys = list(ticket_info.keys())

    airline = [
        x["Name"]
        for x in airlines
        if x["Code"] == response["data"][key][ticket_info_keys[0]]["airline"]
    ][0]

    departure = response["data"][key][ticket_info_keys[0]]["departure_at"]
    departure = datetime.fromisoformat(departure) + timedelta(hours=3)
    departure = departure.strftime("%Y-%m-%d %H:%M:%S")

    price = str(response["data"][key][ticket_info_keys[0]]["price"]) + " $"

    s = "<b>Info about your flight</b>\n"
    s += f"Destination: {home_airport} -> {selected}\n"
    s += f"Airline: {airline}\n"
    s += f"Departure date: {departure}\n"
    s += f"Price: {price}\n"

    db.add_flight(
        message.from_user.id,
        home_airport,
        selected,
        int(price.split(" ")[0]),
        departure,
        airline,
        datetime.now(),
    )
    bot.send_message(message.chat.id, s, parse_mode="HTML")


def show_airports(message):
    values = [x for x, y in cities.items() if y == message.text]
    keyboard = types.InlineKeyboardMarkup()
    for value in values:
        button = types.InlineKeyboardButton(text=value, callback_data=value)
        keyboard.add(button)
    bot.send_message(message.chat.id, "Choose from this options", reply_markup=keyboard)


def get_date(message):
    global selected_date
    text = message.text.split()
    selected_date = f'2024-{"-".join(x for x in text)}'
    ticket_price_handler(message)


def choose_date(message):
    bot.send_message(
        message.chat.id,
        f"Selected option: {selected}\nNow choose a date\nFormat: MM DD",
    )
    bot.register_next_step_handler(message, get_date)


@bot.message_handler(commands=["ticket"])
def get_ticket_price(message):
    bot.send_message(
        message.chat.id, "<b>Enter your city destination</b>", parse_mode="HTML"
    )
    bot.register_next_step_handler(message, show_airports)


@bot.callback_query_handler(func=lambda call: True)
def button_click(call):
    global selected
    selected = call.data
    choose_date(call.message)


def get_10_flights(user_id):
    response = formatting.get_10_flights(user_id)
    airlines = fr_api.get_airlines()
    top_10 = sorted(response, key=lambda x: (x["price"], x["departure_at"]))[:10]
    s = "<b> Top 10 flights from your home airport for today</b>\n"
    for i, x in enumerate(top_10, 1):
        airline = [y["Name"] for y in airlines if y["Code"] == x["airline"]][0]
        departure = x["departure_at"]
        departure = datetime.fromisoformat(departure) + timedelta(hours=3)
        departure = departure.strftime("%Y-%m-%d %H:%M:%S")
        s += f"{i}. {x['origin']} -> {x['destination']} with {airline} at {departure} for {x['price']} $\n\n"
    return s


def admin_send_flights123():
    ids = db.get_all_users()[1][0]
    bot.send_message(ids, get_10_flights(ids), parse_mode="HTML")


@bot.message_handler(commands=["flight"])
def info_by_registration(message):
    bot.send_message(message.chat.id, "Please send me registration")
    bot.register_next_step_handler(message, get_flight)


@bot.message_handler(commands=["stats"])
def get_users_flights(message):
    home_airport = db.get_home_airport(message.from_user.id)
    s = f"<b>Your most recent flight searches</b>\n\n<u>Your home airport is currently</u>: {home_airport}\n\n"

    stats = db.show_user_flights(message.from_user.id)
    print(stats[0])
    for i, x in enumerate(stats, start=1):
        s += f"{i}. From {x[0]} to {x[1]} for: {x[2]}$ at {x[3]} with {x[4]}\n\n"
    bot.send_message(message.chat.id, s, parse_mode="HTML")


def get_gif_url():
    url = "https://api.giphy.com/v1/gifs/search"

    param = {"api_key": constants.GIPHY_API, "q": "airplane", "limit": 5, "rating": "g"}

    result = requests.get(url, params=param).json()
    result = [result["data"][i]["images"]["original"]["url"] for i in range(5)]
    return random.choice(result)


def format_time(timestamp):
    datetime_obj = datetime.utcfromtimestamp(timestamp)

    formatted_time = (datetime_obj + timedelta(hours=3)).strftime("%H:%M:%S")
    return formatted_time


def format_info(message, by):
    info = get_info(message, by)
    flight = fr_api.get_flights(registration=info[0])[0]
    s = "<b>Info</b>\n\n"
    s += "<b>Basic info</b>\n"
    try:
        s += f"Registration: {info[0]}\n\n"
    except:
        s += "N/A"
    try:
        s += f"Aircraft model: {info[1]}\n\n"
    except:
        s += "N/A"
    try:
        s += f"Airline name: {info[2]}\n\n"
    except:
        s += "N/A"

    try:
        s += f"Origin Airport: {info[3]}\n\n"
    except:
        s += "N/A"

    try:
        s += f"Destination Airport: {info[4]}\n\n"
    except:
        s += "N/A"
    s += "<b>Physics info</b>\n"
    try:
        s += f"Ground speed: {info[5]}\n\n"
    except:
        s += "N/A"

    try:
        s += f"Altitude: {info[6]}\n\n"
    except:
        s += "N/A"

    try:
        s += f"Heading : {info[7]}\n\n"
    except:
        s += "N/A"

    try:
        s += f'Scheduled time of departure: {format_time(info[8]["scheduled"]["departure"])}\n\n'
    except:
        s += "N/A"
    try:
        s += f'Scheduled time of arrival: {format_time(info[8]["scheduled"]["arrival"])}\n\n'
    except:
        s += "N/A"
    try:
        s += f"Distance left: {flight.get_distance_from(fr_api.get_airport(info[-2])):.0f} km\n\n"
    except:
        s += "N/A"
    try:
        s += f"Arrival airport website is: {fr_api.get_airport(info[-2],details=True).website}"
    except:
        s += "N/A"

    return s


@bot.message_handler(content_types=["location"])
def handle_location_message(message):
    try:
        url = get_url(message, "location")
        sent_photo = bot.send_photo(message.chat.id, url)
        sent_photo_id = sent_photo.message_id
        bot.send_message(
            message.chat.id,
            format_info(message, "location"),
            reply_to_message_id=sent_photo_id,
            parse_mode="HTML",
        )
    except:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(
            message.chat.id,
            "It seems that now there is no flights above you\nPlease,check later!",
        )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


def get_flight(message):
    url = get_url(message, "registration")
    sent_photo = bot.send_photo(message.chat.id, url)
    sent_photo_id = sent_photo.message_id
    bot.send_message(
        message.chat.id,
        format_info(message, "registration"),
        reply_to_message_id=sent_photo_id,
        parse_mode="HTML",
    )


@bot.message_handler(commands=["flight"])
def info_by_registration(message):
    bot.send_message(message.chat.id, "Please send me registration")
    bot.register_next_step_handler(message, get_flight)


@bot.message_handler(commands=["weather"])
def get_weather(message):
    airport = db.get_home_airport(message.chat.id)
    weather = fr_api.get_airport(airport, details=True).weather["temp"]["celsius"]
    bot.send_message(message.chat.id, f"Temp at your home airport is: {weather} °C")


# schedule.every(10).seconds.do(admin_send_flights123)

# def biba():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# scheduler_thread = threading.Thread(target=biba)
# scheduler_thread.start()
bot.polling()
