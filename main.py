#импорт нужных модулей и библиотек
import constants
import telebot
from telebot import types
from FlightRadar24 import FlightRadar24API
from datetime import datetime,timedelta
from pytz import timezone
from database import DB
import requests
import geopy.distance
import schedule
import time
import threading
#объявление экземпляров классов
fr_api = FlightRadar24API()
TOKEN = constants.TOKEN
bot = telebot.TeleBot(TOKEN)
db = DB('/Users/fedorfatekhov/Desktop/telegram_bot/telegram_bot_db.db')

#обработчик команды старт + отправка сообщения
@bot.message_handler(commands = ['start'])
def start(message): 
    s = 'I am a Flight Track Bot and I will help all aviation enthusiasts around the world\n'
    bot.send_message(message.chat.id,f'Hi,<b>{message.from_user.first_name}</b>\n\n{s}',parse_mode='HTML')
    
#создаем инлайн кнопки для бота + обработчик команды help
@bot.message_handler(commands=['help'])
def help_handler(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
    markup.add('Get flight info') #добавляем кнопку в маркап
    markup.add('Get planes near you')
    markup.add('See my stats')
    markup.add('Get an Airplane GIF')
    bot.send_message(message.from_user.id, constants.HELP, reply_markup=markup)
    
#обработчки для команды регистарции    
@bot.message_handler(commands=['register'])
def reg_person(message):
    if not db.check_user_in_db(message.chat.id):
        bot.send_message(message.chat.id,'Enter your home AIRPORT') 
        bot.register_next_step_handler(message,get_airport)
    else: 
        bot.send_message(message.chat.id,'You are already registered! Enjoy our bot.\n For help type: /help')
        
#функция которая получает нужный аэропорт(попадаем в нее с помощью next step handler)    
def get_airport(message):
    airport = f'<b>{message.text}</b>'
    bot.send_message(message.chat.id,f'Thank you for registering. Your home airport is {airport}',parse_mode='HTML')
    db.add_user(message.from_user.id,message.text) # записываем введенный аэропорт в БД, с помомщью запроса
    
#функция хэндлер для команды сменить аэропорт
@bot.message_handler(commands=['change_airport'])
def change_airport(message):
    bot.send_message(message.chat.id,'Enter your new home airport')
    print(db.get_user_id(message.from_user.id))
    bot.register_next_step_handler(message,get_new_airport)
    
#функция аналогичная предыдущей, но для обновления 
def get_new_airport(message): 
    new_port = message.text 
    db.change_airport(message.from_user.id,new_port) # обновляем таблицу в БД с помощью INSERT
    bot.send_message(message.chat.id,f'All set! Your new home airport is {new_port}')
     
    
#полчуаем фото самолета по локации
def get_url_by_location(message):
    #через запрос к API FlightRadar24 границы поиска + указываем полученные из отправленной лоакции широту и долготу
    bounds = fr_api.get_bounds_by_point(message.location.latitude, message.location.longitude, 250000)
    flight = fr_api.get_flights(bounds = bounds)[0]
    flight_details = fr_api.get_flight_details(flight)
    flight.set_flight_details(flight_details)
    print(message.location.latitude, message.location.longitude)
    try:
        url = flight.aircraft_images['medium'][0]['src']
        return url
    except:
        return 'https://unsplash.com/photos/a-large-airplane-flying-through-a-blue-sky-72Q4qUGGAbU'

def get_info_by_location(message):
    bounds = fr_api.get_bounds_by_point(message.location.latitude, message.location.longitude, 250000)
    flight = fr_api.get_flights(bounds = bounds)[0]
    flight_details = fr_api.get_flight_details(flight)
    flight.set_flight_details(flight_details)
    info = [flight.registration,flight.aircraft_model,flight.airline_name,flight.origin_airport_name,flight.destination_airport_name,flight.ground_speed,flight.altitude,flight.heading,flight.time_details,flight.destination_airport_iata,flight.origin_airport_iata]
    return info

def get_url_by_registration(message):
    flight = fr_api.get_flights(registration=message.text)[0]
    flight_details = fr_api.get_flight_details(flight)
    flight.set_flight_details(flight_details)
    url = flight.aircraft_images['medium'][0]['src']
    
    return url
def ticket_price_handler(message):
    print(type(message.text))
    home_airport = db.get_home_airport(message.from_user.id)
    url = constants.API_URL
    dest_and_time = message.text.split(' ')
    print(message.text)
    querystring = {"origin":f'{home_airport}',"page":"None","currency":"USD","depart_date":f'{dest_and_time[1]}',"destination":f'{dest_and_time[0]}'}

    headers = {
        "X-Access-Token": f'{constants.X_Access_Token}',
        "X-RapidAPI-Key": f'{constants.X_RapidAPI_Key}',
        "X-RapidAPI-Host": f'{constants.X_RapidAPI_Host}'
    }

    response = requests.get(url, headers=headers, params=querystring).json()
    
    airlines = fr_api.get_airlines()
    print(response['data'])
    key = list(response['data'].keys())[0]
    ticket_info = response['data'][key]
    ticket_info_keys = list(ticket_info.keys())

    airline = [x['Name'] for x in airlines if x['Code'] == response['data'][key][ticket_info_keys[0]]['airline']][0]

    departure = response['data'][key][ticket_info_keys[0]]['departure_at']
    departure = datetime.fromisoformat(departure) + timedelta(hours=3)
    departure = departure.strftime("%Y-%m-%d %H:%M:%S")
    
    price = str(response['data'][key][ticket_info_keys[0]]['price']) + ' $'
    
    s = '<b>Info about your flight</b>\n'
    s += f'Destination: {home_airport} -> {dest_and_time[0]}\n'
    s += f'Airline: {airline}\n'
    s += f'Departure date: {departure}\n'
    s += f'Price: {price}\n'
    
    db.add_flight(message.from_user.id,home_airport,dest_and_time[0],int(price.split(' ')[0]),departure)
    bot.send_message(message.chat.id,s,parse_mode='HTML')
    
@bot.message_handler(commands=['get_my_flight'])
def get_ticket_price(message):
    bot.send_message(message.chat.id,'<b>Enter your destination and departure date</b>\nExample:\nVKO 2024-03-15\nVKO 2024-03',parse_mode='HTML')
    bot.register_next_step_handler(message,ticket_price_handler)
    
def format_searches(row):
    ...
def get_10_flights(user_id):
    home_airport = db.get_home_airport(user_id)
    url = "https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com/v1/city-directions"
    querystring = {"currency":"USD","origin":f'{home_airport}'}
    headers = {
        "X-Access-Token": f'{constants.X_Access_Token}',
        "X-RapidAPI-Key": f'{constants.X_RapidAPI_Key}',
        "X-RapidAPI-Host": f'{constants.X_RapidAPI_Host}'
    }

    response = list((requests.get(url, headers=headers, params=querystring).json()['data'].values()))
    airlines = fr_api.get_airlines()
    top_10 = sorted(response,key=lambda x: (x['price'],x['departure_at']))[:10]
    s = '<b> Top 10 flights from your home airport for today</b>\n'
    for i,x in enumerate(top_10,1):
        airline = [y['Name'] for y in airlines if y['Code'] == x['airline']][0]
        departure = x['departure_at']
        departure = datetime.fromisoformat(departure) + timedelta(hours=3)
        departure = departure.strftime("%Y-%m-%d %H:%M:%S")
        s += (f"{i}. {x['origin']} -> {x['destination']} with {airline} at {departure} for {x['price']} $\n\n")
    return s

# @bot.message_handler(commands=['send'])
# def admin_send_flights(message):
#     admin = db.check_admin()
#     print(message.chat.id)
#     if str(message.chat.id) == str(admin):
#         bot.send_message(message.chat.id,'Starting...') 
#         all_id = db.get_all_users()
#         print(all_id)
#         for i in all_id:
#             bot.send_message(int(i[0]),get_10_flights(i[0]),parse_mode='HTML')
#     else:
#         bot.send_message(message.chat.id,'Access denied') 

def admin_send_flights123():
    ids = db.get_all_users()[1][0]
    bot.send_message(ids,get_10_flights(ids),parse_mode='HTML')
    
    

@bot.message_handler(content_types=['text'])
def get_users_flights(message):
    if message.text == 'See my stats':
        home_airport = db.get_home_airport(message.from_user.id)
        s = f'<b>Your most recent flight searches</b>\n\n<u>Your home airport is currently</u>: {home_airport}\n\n'
        
        stats = db.show_user_flights(message.from_user.id)
        print(stats[0])
        for i,x in enumerate(stats,start=1):
            s += f'{i}. From {x[0]} to {x[1]} for: {x[2]}$ at {x[3]}\n\n'
        bot.send_message(message.chat.id,s,parse_mode='HTML')
    
def get_info_by_registration(message):
    flight = fr_api.get_flights(registration=message.text)[0]
    flight_details = fr_api.get_flight_details(flight)
    flight.set_flight_details(flight_details)
    info = [flight.registration,flight.aircraft_model,flight.airline_name,flight.origin_airport_name,flight.destination_airport_name,flight.ground_speed,flight.altitude,flight.heading,flight.time_details,flight.destination_airport_iata,flight.origin_airport_iata]
    return info


def format_time(timestamp): 
    datetime_obj = datetime.utcfromtimestamp(timestamp)

    formatted_time = (datetime_obj +timedelta(hours=3)).strftime('%H:%M:%S')
    return formatted_time

def get_distance(coord1,coord2):
    return geopy.distance.geodesic(coord1, coord2).km

def format_info(message,by): 
    if by == 'location':
        info = get_info_by_location(message)
    else:
        info = get_info_by_registration(message)

    s = "<b>Info</b>\n\n"
    s += "<b>Basic info</b>\n"
    try: 
        s += f'Registration: {info[0]}\n\n'
    except: 
        s += 'N/A'
    try: 
        s += f'Aircraft model: {info[1]}\n\n'
    except: 
        s += 'N/A'
    try: 
        s += f'Airline name: {info[2]}\n\n'
    except: 
        s += 'N/A'
    
    try: 
        s += f'Origin Airport: {info[3]}\n\n'
    except: 
        s += 'N/A'
    
    try: 
        s += f'Destination Airport: {info[4]}\n\n'
    except: 
        s += 'N/A'
    s += "<b>Physics info</b>\n"
    try: 
        s += f'Ground speed: {info[5]}\n\n'
    except: 
        s += 'N/A'
        
    try: 
        s += f'Altitude: {info[6]}\n\n'
    except: 
        s += 'N/A'
    
    try: 
        s += f'Heading : {info[7]}\n\n'
    except: 
        s += 'N/A'
        
    try: 
        s += f'Scheduled time of departure: {format_time(info[8]["scheduled"]["departure"])}\n\n'
    except: 
        s += 'N/A'
    try: 
         s += f'Scheduled time of arrival: {format_time(info[8]["scheduled"]["arrival"])}\n\n'
    except: 
        s += 'N/A'
    try:
        ap_from = (fr_api.get_airport(info[9]).latitude,fr_api.get_airport(info[9]).longitude)
        ap_to = (fr_api.get_airport(info[10]).latitude,fr_api.get_airport(info[10]).longitude)
        s += f'Distance is {get_distance(ap_from,ap_to):.0f} km'
    except:
        s += 'N/A'
    return s
        

@bot.message_handler(content_types=['location'])
def handle_location_message(message):
    url = get_url_by_location(message)
    sent_photo = bot.send_photo(message.chat.id,url)
    sent_photo_id = sent_photo.message_id
    bot.send_message(message.chat.id, format_info(message,'location'), reply_to_message_id=sent_photo_id,parse_mode='HTML')

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
def get_flight(message):
    url = get_url_by_registration(message)
    sent_photo = bot.send_photo(message.chat.id,url)
    sent_photo_id = sent_photo.message_id
    bot.send_message(message.chat.id, format_info(message,'registration'), reply_to_message_id=sent_photo_id,parse_mode='HTML')
    
@bot.message_handler(content_types=['text'])
def info_by_registration(messsage): 
    if messsage.text == 'Get flight info':
        bot.register_next_step_handler(messsage,get_flight)
        

schedule.every(10).seconds.do(admin_send_flights123)

def biba():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=biba)
scheduler_thread.start()
bot.polling()