# from FlightRadar24 import FlightRadar24API
# fr_api = FlightRadar24API()
# import json
# from datetime import datetime,timedelta
# import geopy.distance
# import constants
# from database import DB

# coords_1 = (52.2296756, 21.0122287)
# coords_2 = (52.406374, 16.9251681)
# a1 = fr_api.get_airport('JFK')
# a2 = fr_api.get_airport('SVO')


# # # print(a1.latitude,a1.longitude)
# print(f'{geopy.distance.geodesic((a1.latitude,a1.longitude), (a2.latitude,a2.longitude)).km:.0f}')
# # bounds = fr_api.get_bounds_by_point(55.702898257823115, 37.35183186771398,  1000000)
# # flight = fr_api.get_flights(bounds = bounds)[0]
# # flight_details = fr_api.get_flight_details(flight)
# # flight.set_flight_details(flight_details)
# # # print(flight.registration,flight.aircraft_model,flight.airline_name,flight.origin_airport_name,flight.destination_airport_name)
# # print(fr_api.get_airport(flight.origin_airport_iata).latitude)


# # most = [fr_api.get_most_tracked()['data'][i]['to_iata'] for i in range(6)]
# # filtered_most = list(filter(lambda x: x is not None,most))[0]
# # print(filtered_most)
# # home_airport = 'JFK'




# import requests

# # url = "https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com/v1/prices/cheap"

# # querystring = {"origin":"MOW","page":"None","currency":"USD","depart_date":"2024-03-20","destination":"HND"}

# # headers = {
# # 	"X-Access-Token": "ce9f018ac8cb9b2c6575130aef080d96",
# # 	"X-RapidAPI-Key": "51cac9d41fmsh2b69d7fac76868ep12147bjsne60d91a60d8a",
# # 	"X-RapidAPI-Host": "travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com"
# # }

# # airlines = fr_api.get_airlines()
# # airports = fr_api.get_airports()
# # airport = fr_api.get_airport('MOW')
# # print(airport.city)
# # response = requests.get(url, headers=headers, params=querystring).json()
# # print(response)
# # key = list(response['data'].keys())[0]
# # ticket_info = response['data'][key]
# # ticket_info_keys = list(ticket_info.keys())

# # airline = [x['Name'] for x in airlines if x['Code'] == response['data'][key][ticket_info_keys[0]]['airline']][0]

# # departure = response['data'][key][ticket_info_keys[0]]['departure_at']
# # departure = datetime.fromisoformat(departure) + timedelta(hours=3)
# # departure = departure.strftime("%Y-%m-%d %H:%M:%S")
# # price = str(response['data'][key][ticket_info_keys[0]]['price']) + ' $'
# # print(airline,departure,price.split(' ')[0])

# # url = "https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com/v1/city-directions"

# # querystring = {"currency":"USD","origin":"MOW"}

# # headers = {
# # 	"X-Access-Token": "ce9f018ac8cb9b2c6575130aef080d96",
# # 	"X-RapidAPI-Key": "51cac9d41fmsh2b69d7fac76868ep12147bjsne60d91a60d8a",
# # 	"X-RapidAPI-Host": "travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com"
# # }

# # response = list((requests.get(url, headers=headers, params=querystring).json()['data'].values()))
# # airlines = fr_api.get_airlines()

# # # key = list(response['data'].keys())[0]
# # # ticket_info = response['data'][key]
# # # ticket_info_keys = list(ticket_info.keys())



# # top_10 = sorted(response,key=lambda x: (x['price'],x['departure_at']))[:10]
# # # departure = response['data'][key][ticket_info_keys[0]]['departure_at']
# # # departure = datetime.fromisoformat(departure) + timedelta(hours=3)
# # # departure = departure.strftime("%Y-%m-%d %H:%M:%S")
# # # price = str(response['data'][key][ticket_info_keys[0]]['price']) + ' $'

# # # for i,x in enumerate(top_10,1):
# # #     airline = [y['Name'] for y in airlines if y['Code'] == x['airline']][0]
# # #     departure = x['departure_at']
# # #     departure = datetime.fromisoformat(departure) + timedelta(hours=3)
# # #     departure = departure.strftime("%Y-%m-%d %H:%M:%S")
# # #     print(f"{i}. {x['origin']} -> {x['destination']} with {airline} at {departure} for {x['price']} $")

# # def get_10_flights(user_id):
# #     home_airport = db.get_home_airport(user_id)
# #     url = "https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com/v1/city-directions"
# #     querystring = {"currency":"USD","origin":f'{home_airport}'}
# #     headers = {
# #         "X-Access-Token": f'{constants.X_Access_Token}',
# #         "X-RapidAPI-Key": f'{constants.X_RapidAPI_Key}',
# #         "X-RapidAPI-Host": f'{constants.X_RapidAPI_Host}'
# #     }

# #     response = list((requests.get(url, headers=headers, params=querystring).json()['data'].values()))
# #     airlines = fr_api.get_airlines()
# #     top_10 = sorted(response,key=lambda x: (x['price'],x['departure_at']))[:10]
# #     s = '<b> Top 10 flights from your home airport for today</b>\n'
# #     for i,x in enumerate(top_10,1):
# #         airline = [y['Name'] for y in airlines if y['Code'] == x['airline']][0]
# #         departure = x['departure_at']
# #         departure = datetime.fromisoformat(departure) + timedelta(hours=3)
# #         departure = departure.strftime("%Y-%m-%d %H:%M:%S")
# #         s += (f"{i}. {x['origin']} -> {x['destination']} with {airline} at {departure} for {x['price']} $\n")
# #     return s

# # db = DB('/Users/fedorfatekhov/Desktop/telegram_bot/telegram_bot_db.db')
# # users = db.get_all_users()
# # for x in users: 
# #     print(get_10_flights(x[0]))




        
# for x in a: 
#     print(x)

# print()