import requests
import datetime
from dateparser import parse
import geocoder
import io
from contextlib import redirect_stdout
import pandas as pd

from dotenv import dotenv_values
from geopy.geocoders import Nominatim
from chat_gpt_utils import get_chat_gpt_response
from misc_utils import get_latest_csv_file
from load_hurdat_data import download_latest_data
from convert_dataset import convert_to_df

geolocator = Nominatim(user_agent="MyRadar Weather App")
config = dotenv_values(".env") 

myradar_api_key = config["myradar_api_key"]

latest_csv_file = get_latest_csv_file()

if not latest_csv_file:
    print("csv file data not found. initiating download")
    file_path = download_latest_data()
    if file_path:
        print("downloaded csv data ")
        df_path = convert_to_df(file_path)
        if df_path:
            print("Text data succesfully converted.")
            latest_csv_file = get_latest_csv_file()
        else:
            print("unable to convert text data to csv data")
            exit()
    else:
        print("unable to download csv data ")
        exit()
    
df = pd.read_csv(latest_csv_file)


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


# takes user's query and outputs the prompt
def create_hudat_prompt(user_query):
    print("using data from => ", latest_csv_file)
    column_names = "index, basin, atcf_cyclone_number_for_that_year, name, year, month, day, hours_in_utc, minutes_in_utc, record_identifier, record_identifier_desc, status_of_system, status_of_system_desc, latitude, longitude, maximum_sustained_wind_in_knots, minimum_pressure_in_millibars"
    prompt = f"""
Below are the HURDAT2 CSV database columns loaded into dataframe.
Dataframe Columns:
    {column_names}
Instructions:
    - Assume that the data is there in the pandas dataframe and dataframe is defined as `df`.
    - Only provide python code for the given query.
    - Do not form any textual sentence.
    - Use print statements to answer user query in single sentence.
    - Respond with the python code only.
    - Do not explain the code.
    - Strictly reply 'print("cant_find")' if User Query is not related to HURDAT2.
Using above Dataframe Columns and follow instructions strictly to generate only python code.
User Query: {user_query}
"""
    return prompt


# if first response 
def fix_code_prompt(python_code, error):
    prompt = f"""Act as a Python interpreter and solve the following. Respond with the python code only.
Instructions:
    - Assume that the data is there in the pandas dataframe and dataframe is defined as `df`.
    - Only provide python code for the given query.
    - Do not form any textual sentence.
    - Use print statements to answer user query in single sentence.
    - Respond with the python code only.
    - Do not explain the code.
    - Current year is {datetime.now().year}
    - Strictly reply 'print("cant_find")' if User Query is not related to HURDAT2.
Python Code: {python_code}\n
Error: {error}
New Python Code: 
"""
    return prompt
    

def evaluate_code(python_code):
    error = ""
    try:
        print("generated python code => ", python_code)
        
        # Redirect the output to a string buffer
        output = io.StringIO()
        with redirect_stdout(output):
            eval(python_code)

        # Get the output as a string
        python_result = output.getvalue()
        print("python_result => ", python_result)
    
    except Exception as e:
        python_result = "Python: SyntaxError"
        print("Python: SyntaxError => ", e)
        error = e
        
    return python_result, error


def get_hurdat_response(user_msg):
    try:
        prompt = create_hudat_prompt(user_msg)
        response = get_chat_gpt_response("", prompt)
        python_code = response["choices"][0]["message"]["content"]
        python_result, error = evaluate_code(python_code)


        if python_result == "Python: SyntaxError":
            print("got python error, trying again to fix the issue")
            new_prompt = fix_code_prompt(python_code, error)
            response = get_chat_gpt_response("", new_prompt)
            python_code = response["choices"][0]["message"]["content"]
            python_result, error = evaluate_code(python_code)
            
        return python_result
    except Exception as e:
        print("error in get hurdat_response => ", e)
        return None
    
    
def is_valid_hurdat_response(hurdat_response):
    if not hurdat_response:
        return False 
    
    if hurdat_response and ( hurdat_response.strip() == "[]" or  hurdat_response.strip() == ""):
        print("empty array or empty response using hurdat prompt")
        return False
    
    if hurdat_response.strip().lower() == "nan":
        return False
    
    if not hurdat_response:
        return False
    
    if hurdat_response == "Python: SyntaxError":
        print("Python: SyntaxError == using hurdat prompt")
        return False

    if str(hurdat_response).strip() == "cant_find":
        print("HURDAT answer not available in database")
        return False
    
    return True