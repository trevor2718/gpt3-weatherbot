import openai
from dotenv import dotenv_values
from flask import session
import tiktoken
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from user_agent import generate_user_agent
from math import radians, cos, sin, asin, sqrt
import os
import json

config = dotenv_values(".env") 

openai.api_key = config["openai_key"]

user_agent = generate_user_agent()


def trim_prompt_length(prompt, token_len):
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

    if len(encoding.encode(prompt)) > token_len:
        print(f"Prompt is too long, Need to trim, Using first {token_len} tokens")
        encoded_prompt = encoding.encode(prompt)[:token_len]
        prompt = encoding.decode( encoded_prompt )
        print("last sentence from the prompt => ", prompt[-100:])
    return prompt


def get_chat_gpt_response(prompt):
    
    max_input_token = 3072
    prompt = trim_prompt_length(prompt, max_input_token)
    
    msg_list = [
          {
            "role": "user",
            "content": prompt
        }
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=msg_list,
        temperature=0.0,
        top_p=1.0,
        n=3,
        stream= False,
        max_tokens= 192,
        presence_penalty= 0,
        frequency_penalty= 0
    )

    # print(completion)
    # res_str = completion["choices"][0]["message"]["content"]
    return completion


def get_chat_gpt_parameterized_response(prompt, temperature=0.0, top_p=1.0, n=1, stream=False, max_tokens=1024, presence_penalty=0, frequency_penalty=0):
    
    max_input_token = 2560
    prompt = trim_prompt_length(prompt, max_input_token)
    
    msg_list = [
          {
            "role": "user",
            "content": prompt
        }
    ]
       
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=msg_list,
        temperature=temperature,
        top_p=top_p,
        n=n,
        stream=stream,
        max_tokens=max_tokens,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty
    )

    return completion


def get_location_from_chat_gpt(user_msg):
    
    prompt = f'''Act as a NER model and find only location and datetime from the given sentence. Do not form a sentence. Strictly follow the instruction below. If none found then provide NO_DATA_FOUND.\neg.\nInput: Is it going to rain in Texas tomorrow?\nOutput: Location: Texas\nDatetime: Tomorrow\nInput: Where is Cincinnati?\nOutput: Location: Cincinnati\nDatetime: None\nInput: Who is the president?\nOutput: NO_DATA_FOUND.\nInput: {user_msg.strip()}\nOutput: '''

    max_input_token = 2560
    prompt = trim_prompt_length(prompt, max_input_token)
    
    msg_list = [
        {
            "role": "user",
            "content": prompt
        }     
    ]
    # print("context msg list => ", msg_list)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=msg_list )

    # print(completion)
    # res_str = completion["choices"][0]["message"]["content"]
    return completion


def get_distance_info(user_msg):
    prompt = f'''This is an intent detection task. Your job is to identify if the user is asking about cyclones or hurricanes occurring near a specific location within a certain distance. If the user does not provide a distance, but mentions a term implying proximity like 'near', 'around', 'close', etc., assume a default distance of 10 km.

Make sure to only identify the location and distance (if provided), and the user's intent to know about cyclones/hurricanes. If there's no intent or the intent does not involve asking about cyclones/hurricanes near a location, return 'not_found'. If the user's intent is detected correctly, return the location and distance in the format `["location, distance"]`. If the distance is not provided, use the default distance of 10 km.

Here are some examples:

Input: How many cyclones occurred in Miami?
Output: not_found

Input: How many cyclones occurred near 5km of Miami?
Output: ["Miami, 5km"]

Input: Which was the strongest hurricane ever occurred in Texas?
Output: not_found

Input: How many hurricanes occurred nearly 10 miles from London?
Output: ["London, 10 miles"]

Input: How many hurricanes occurred nearly 10 miles from London? and give the names
Output: ["London, 10 miles"]

Input: How many hurricanes occurred nearly 10 miles from London in the year of 2022?
Output: ["London, 10 miles"]

Input: How many hurricanes occurred nearly 10 km from London in the year of 2022?
Output: ["London, 10 km"]

Input: How many hurricanes occurred between 2010 and 2020 within 10 miles of London?
Output: ["London, 10 miles"]

Input: How many hurricanes occurred between 2010 and 2020 within 10 miles of London? And which?
Output: ["London, 10 miles"]


Strictly do not generates output like `["Florida, 100 km"], not_found` generates any of one and never return 'not_found' in the list.
Differentiate distance and location with `,` strictly in the output.
     Input: {user_msg.strip()}\nOutput: '''
    max_input_token = 2560
    prompt = trim_prompt_length(prompt, max_input_token)
    
    msg_list = [
        {
            "role": "user",
            "content": prompt
        }     
    ]
    # print("context msg list => ", msg_list)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=msg_list )

    # print(completion)
    res_str = completion["choices"][0]["message"]["content"]
    
    print(res_str)
    # print(completion)
    return res_str


def remove_trailing_zero(num):
    if num.is_integer():
        return int(num)
    else:
        return num


def generate_points_within_radius(lat, long, radius_km):
        R = 6371.01  # radius of Earth in km

        lat_range = range(int(lat*10)-10, int(lat*10)+111)
        points = []
        for lat_offset in lat_range:
            long_range = range(int(long*10)-10, int(long*10)+111)
            for long_offset in long_range:
                lat_new = round(lat_offset / 10, 1)
                long_new = round(long_offset / 10, 1)
                dlat = radians(lat_new - lat)
                dlong = radians(long_new - long)
                a = sin(dlat / 2) ** 2 + cos(radians(lat)) * cos(radians(lat_new)) * sin(dlong / 2) ** 2
                c = 2 * asin(sqrt(a))
                distance = R * c
                if distance <= radius_km:
                    points.append((lat_new, long_new))
        return points


def find_matching_points(input_str):
    print(type(input_str))
    input_str = json.loads(input_str)
    input_str_ = input_str[0]
    input_list = input_str_.split(", ")
    location_name = input_list[0]
    radius = input_list[1]
    
    hurdat_csv = './hurdat_data/final_csv_data.csv'
    
    if not os.path.exists(hurdat_csv):
        return False
    
    df = pd.read_csv(hurdat_csv)

    if "km" in radius:
        radius_km = int(radius.replace("km", ""))
    elif "miles" in radius:
        radius_km = int(radius.replace("miles", "")) * 1.60934
    else:
        raise ValueError("Radius must be specified in kilometers or miles")

    geolocator = Nominatim(user_agent=user_agent)
    location = geolocator.geocode(location_name)
    latitude = location.latitude
    longitude = location.longitude


    nearby_points = generate_points_within_radius(latitude, longitude, radius_km)
    nearby_points_updated = [(remove_trailing_zero(lat), remove_trailing_zero(lon)) for lat, lon in nearby_points]


    # Update latitude and longitude columns in the DataFrame
    df['latitude'] = df['latitude'].apply(remove_trailing_zero)
    df['longitude'] = df['longitude'].apply(remove_trailing_zero)
    if len (input_str) == 1:
        matching_points = df[df.apply(lambda row: (row['latitude'], row['longitude']) in nearby_points_updated, axis=1)]
        print('this is matching points',matching_points.head())
        return matching_points
    else:
        return "No cyclone occured"
    
