# import libraries
import os
import json
import openai
import requests
from typing import List
from functional_helpers import *
from dotenv import load_dotenv
from textbase import bot, Message
from textbase.models import OpenAI

# Load your OpenAI API key

OpenAI.api_key = os.getenv(OPENAI_API_KEY)
rapid_api_key = os.getenv(rapid_api_key)


# Prompt for GPT-3.5 Turbo
SYSTEM_PROMPT = """You are chatting with an AI Travel Agent. You job is to provide a plan a tour on the destination.You can ask relevant question. 
The AI should follow the instruction as per the function call information provided. Feel free to start the conversation with any travel related question or topic, and let's have a pleasant chat!
"""
# making function call parameters
functions_to_call = [
    {
        "name": "weather_status",
        "description": "Get both current and forecast weather of a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA.",
                },
                "date_to_predict": {"type": "string",
                                    "description": "The required forecast date from current date, "
                                                   "e.g : if current date is 2023-09-04 then after 5 days means 5 days"
                                                   " after current day which is 2023-09-09"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location", "date_to_predict"],
        }
    },
    {
        "name": "get_flight_info",
        "description": "Get flight information between two locations",
        "parameters": {
            "type": "object",
            "properties": {
                "loc_origin": {
                    "type": "string",
                    "description": "The departure airport, e.g. DUS. This is important",
                },
                "loc_destination": {
                    "type": "string",
                    "description": "The destination airport, e.g. BLR. This is important",
                },

                "journey_date": {
                    "type": "string",
                    "format": "YYYY-MM-DD, e.g 2023-12-31",
                    "description": "The date of journey from departure airport to destination airport"
                },
                "adult_pax": {
                    "type": "string",
                    "description": "No. of adult passenger"
                }
            },
            "required": ["loc_origin", "loc_destination", "destination", "journey_date", "adult_pax"],
        },
    },

]


@bot()
def on_message(message_history: List[Message], state: dict = None):
    # Generate GPT-3.5 Turbo response
    bot_response = OpenAI.generate(
        system_prompt=SYSTEM_PROMPT,
        message_history=message_history,  # Assuming history is the list of user messages
        model="gpt-3.5-turbo-0613",
        function_descriptions_multiple=functions_to_call,
    )
    print("*" * 80)
    print(bot_response)
    print("*" * 80)
    if bot_response.get("function_call"):
        function_name = bot_response["function_call"]["name"]
        function_args = json.loads(bot_response["function_call"]["arguments"])

        if function_name == 'get_flight_info':
            print("check 2")
            function_response = searchAirport(function_args['loc_origin'], function_args['loc_destination'],
                                              function_args['journey_date'], function_args['adult_pax'])
            print("*|" * 40)
            print(function_response)
            print("*|" * 40)
            top_choice = function_response['results'][0]
            # print("*|" * 40)
            # print(top_choice)
            # print("*|" * 40)
            req_date, req_time = top_choice['arrivalAirport']['time'].split('T')
            weather_report = weather_status(top_choice['arrivalAirport']['city'], req_date)
            # weather_details = f"""Date : {weather_report['forecast']['forecastday'][0]['date']},
            #             MaxTemp : {weather_report['forecast']['forecastday'][0]['day']['maxtemp_c']},
            #             Text : {weather_report['forecast']['forecastday'][0]['day']['condition']['text']},
            #             Chance_of_rain : {weather_report['forecast']['forecastday'][0]['day']['daily_chance_of_rain']}
            #             """

            # print("check 3")
            flight_details = f"""from_city : {function_args['loc_origin']}, to_city : {function_args['loc_destination']},
            flight_name : {top_choice["flight_name"]},flight_code: {top_choice['flight_code']},
            departureAirportTime : {top_choice['departureAirport']['time']},
            arrivalAirportTime : {top_choice['arrivalAirport']['time']},
            duration : {top_choice['duration']['text']}, total_cost: {top_choice['totals']['total']},
            Weather details : {weather_report}"""
            # print("check 4")
            # print(flight_details)
            # print("*|" * 40)
            function_response = flight_details
        elif function_name == 'weather_status':
            if len(function_args['date_to_predict']) == 1:
                req_date = str(datetime.now().date() + timedelta(days=function_args['date_to_predict']))
            else:
                req_date = str(function_args['date_to_predict'])
            weather_report = weather_status(function_args['location'], req_date)
            # weather_details = f"""Date_of_forecast : {function_args['date_to_predict']},
            # MaxTemp : {weather_report['forecast']['forecastday'][0]['day']['maxtemp_c']},
            # Text : {weather_report['forecast']['forecastday'][0]['day']['condition']['text']},
            # Chance_of_rain : {weather_report['forecast']['forecastday'][0]['day']['daily_chance_of_rain']}
            # """
            function_response = weather_report
        else:
            function_response = "No required function available for now! Please ask something else:"
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Weather or Flight details depending on the function response : "},
                bot_response,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
            ],
        )
        print("check 5")

        bot_response = second_response["choices"][0]["message"]["content"]
        print("#" * 80)
        print(bot_response)
        print("#" * 80)
    else:
        bot_response = bot_response.content

    response = {
        "data": {
            "messages": [
                {
                    "data_type": "STRING",
                    "value": bot_response
                }
            ],
            "state": state
        },
        "errors": [
            {
                "message": ""
            }
        ]
    }
    print("check 6")
    # print(f"bot_response : {bot_response}")
    return {
        "status_code": 200,
        "response": response
    }
