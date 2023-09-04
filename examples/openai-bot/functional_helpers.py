# import libraries
import os
import json
import requests

rapid_api_key = os.getenv(rapid_api_key)



# making an airport searching function
def searchAirport(from_city, to_city, dod, adult_pax):
    url = "https://flight-fare-search.p.rapidapi.com/v2/flights/"

    querystring = {"from": from_city, "to": to_city, "date": dod, "adult": adult_pax, "type": "economy",
                   "currency": "USD"}

    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": "flight-fare-search.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()


# making a weather status function
def weather_status(place, dt):
    url = "https://weatherapi-com.p.rapidapi.com/forecast.json"

    querystring = {"q":place,"dt" : dt, "lang":"eng"}

    headers = {
        "X-RapidAPI-Key": "5a9578e219msh7b5adda8b82de3fp1b16e3jsn6e6ff7c4440e",
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    weather_report = response.json()
    return f"""Date_of_forecast : {weather_report['forecast']['forecastday'][0]['date']}, 
                MaxTemp : {weather_report['forecast']['forecastday'][0]['day']['maxtemp_c']},
                Text : {weather_report['forecast']['forecastday'][0]['day']['condition']['text']},
                Chance_of_rain : {weather_report['forecast']['forecastday'][0]['day']['daily_chance_of_rain']}
                """
