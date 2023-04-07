import requests
import datetime
from dateparser import parse
import geocoder


from dotenv import dotenv_values
from geopy.geocoders import Nominatim
from chat_gpt_utils import get_chat_gpt_response

geolocator = Nominatim(user_agent="MyRadar Weather App")
config = dotenv_values(".env") 

myradar_api_key = config["myradar_api_key"]

def get_lat_long(location_name):
    # get lat long from weather api
    # https://www.weatherapi.com/api-explorer.aspx#forecast
    
    lat, long = None, None
    # per second 2 request is permissible
    try:
        location = geolocator.geocode(location_name)
        lat, long = location.latitude, location.longitude
    except Exception as e:
        print("error with geopy => ", e)
        print("trying geocoder api")
        try:
            location = geocoder.osm(location_name)
            lat, long = location.latlng
            
        except Exception as e:
            print("33 error with geocoder too => ", e)
    
    # print("location.latitude, location.longitude => ", lat, long)
    return lat, long


def get_forecast_data(latitude, longitude):
    if latitude and longitude:
        # Request headers
        hdr = {
            'Cache-Control': 'no-cache',
            'Subscription-Key': myradar_api_key,
        }
        forecast_url = f'''https://api.myradar.dev/forecast/{latitude},{longitude}?extend=hourly&units=us&lang=en'''
        
        r_data = requests.get(forecast_url, headers=hdr)
        print("get_forecast_data status => ", r_data.status_code)
        # print("status => ", r_data.text)
        
        if r_data.status_code == 200:
            # print(r_data.json())
            return r_data.json()
        elif r_data.status_code == 400:
            msg = r_data.json().get("message")
            print("error while get_forecast_data =>  ", msg)
            return None

    else:
        print("please provide valid latitude and longitudes")
        return None


def get_chatbot_reply(user_msg, previous_chat, location, date_time):
    latitude, longitude = get_lat_long(location)
    main_forecast_data = get_forecast_data(latitude, longitude)
    # compare here
    forecast_data = get_time_comparision(date_time, main_forecast_data)
    
    if forecast_data:    
        weather_type = forecast_data.get("summary")
        wind_mph = forecast_data.get("windSpeed")
        clouds = forecast_data.get("cloudCover")
        feelslike_f = forecast_data.get("apparentTemperature")
        uv = forecast_data.get("uvIndex")
        hourly_summary = main_forecast_data.get("hourly").get("summary")
        if date_time:
            weather_prompt = f"""Act as a weather chatbot only if user asks about weather and prepare a reply for the user using the below information:\n\tLocation: {location}\n\tWeather: {weather_type}\n\tWind speed(mph): {wind_mph}\n\tClouds: {clouds}\n\tFeels like temperature(Fahrenheit): {feelslike_f}\n\tUV rays: {uv}\n\tAbove forecast details are for: {date_time}\n\nIf user is doing Routine conversation then ignore above weather information and talk as a personal assistant with him. Strictly reply in less than 2 sentences.\nUser Query: {user_msg}\nMyRadar Chatbot: """
        else:
            weather_prompt = f"""Act as a weather chatbot only if user asks about weather and prepare a reply for the user using the below information:\n\tLocation: {location}\n\tWeather: {weather_type}\n\tWind speed(mph): {wind_mph}\n\tClouds: {clouds}\n\tFeels like temperature(Fahrenheit): {feelslike_f}\n\tUV rays: {uv}\n\tGeneral weather summary: {hourly_summary}\n\nIf user is doing Routine conversation then ignore above weather information and talk as a personal assistant with him. Strictly reply in less than 2 sentences.\nUser Query: {user_msg}\nMyRadar Chatbot: """
            
        
        print("weather_prompt => ", weather_prompt)
        
        openai_response = get_chat_gpt_response(previous_chat, weather_prompt)
        chatbot_reply = openai_response["choices"][0]["message"]["content"]

        return chatbot_reply, openai_response
    else:
        return "Some error occured. Unable to get the forecast details. Please try", {}
    

def find_datetime_location(chatbot_response):
    location = None
    date_time = None
    
    if "Location: " in chatbot_response and "Datetime: " in chatbot_response:
        lines = chatbot_response.split("\n")
        for line in lines:
            # print("****** lines => ", line)
            if line.strip().startswith("Location:"):
                location = line.replace("Location:","").strip()
            if line.strip().startswith("Datetime:"):
                date_time = line.replace("Datetime:","").strip()

    elif "Location:" in chatbot_response:
        lines = chatbot_response.split("\n")
        for line in lines:
            if line.strip().startswith("Location:"):
                location = line.replace("Location:","").strip()

    elif "Datetime:" in chatbot_response:
        lines = chatbot_response.split("\n")
        for line in lines:
            if line.strip().startswith("Datetime:"):
                date_time = line.replace("Datetime:","").strip()
        
    return location, date_time


def convert_timestamp(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    time_string = dt_object.strftime("%Y-%m-%d %H:%M:%S %p")
    am_pm = time_string.split(" ")[-1]
    
    if am_pm == "PM":
        tt = time_string.split(" ")[-2]
        hh = 24 - int(tt.split(":")[0]) + 12
        mm = int(tt.split(":")[1])
        ss = int(tt.split(":")[2])
        time_string = f"{time_string.split(' ')[0]} {hh}:{mm}:{ss}"
    else:
        time_string = " ".join(time_string.split(" ")[0:2]).strip()
    return time_string


def get_time_comparision(user_time, json_data):
    currently = json_data['currently']
    try:
        user_time = parse(user_time,)
        user_time = str(user_time).split(".")[0].strip()
        # print("usertime => ",user_time)
        hours_data = json_data['hourly']['data']
        daily_data = json_data['daily']['data']
        
        for cur_data in hours_data:
            json_time = cur_data.get("time")
            json_time = str(convert_timestamp(json_time)).strip()
            if json_time.startswith( user_time[:14] ):
                print("found time match")
                return cur_data
    except Exception as e:
        print("error => ",e)
        
    return currently
