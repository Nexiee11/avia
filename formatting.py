from database import DB 
import constants
import requests
db = DB('telegram_bot_db.db')
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
    return response 