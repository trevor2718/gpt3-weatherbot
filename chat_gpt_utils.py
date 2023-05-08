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
    prompt = f'''Act as a NER model and find only the distance, location and intent of the user msg do not form a sentence strictly follow the instructions. If the user has asked about the nearby location info then and only then provide a valid response else provide `not_found`. If distance is not provided and given approx distance then use 10km as a default nearby/around distance.
Input: How many cyclones occurred in Miami?
Output: not_found

Input: How many cyclones occurred near 5km of Miami?
Output: ["Miami, 5km"]

Input: Which was the strongest hurricane ever occurred in Texas?
Output: not_found

Input: How many hurricanes occurred nearly 10 miles from London?
Output: ["London, 10 miles"]

Input: How many hurricanes occurred nearly 10 miles from London and which?
Output: ["London, 10 miles", "name"]

Input: How many hurricanes occurred nearly 10 miles from London? list all.
Output: ["London, 10 miles", "name"]

Input: How many hurricanes occurred nearly 10 miles from London? and give the names
Output: ["London, 10 miles", "name"]

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

    # Compare and find matching points
    matching_points = df[df.apply(lambda row: (row['latitude'], row['longitude']) in nearby_points_updated, axis=1)]
    unique_cyclones_matching_points = matching_points.groupby(['year', 'atcf_cyclone_number_for_that_year'])['name'].first().reset_index()
    unique_cyclones_matching_points_name = matching_points.groupby(['year', 'atcf_cyclone_number_for_that_year', 'name'])['name'].count().reset_index(name='count')

    print("Unique Cyclone Occurrences for Matching Points:")
    print(len(unique_cyclones_matching_points))
    name_of_cyclone=unique_cyclones_matching_points_name['name'].tolist()
    year_of_cyclone=unique_cyclones_matching_points_name['year'].tolist()
    print(name_of_cyclone)
    print(year_of_cyclone)
    formated_list=[]
    for i , j in zip(name_of_cyclone,year_of_cyclone):
        formated_list.append(f'cyclone {i} in the year of {str(j)}')
    if len (input_str) == 1:
        return (len(unique_cyclones_matching_points))
    else:
        if year_of_cyclone!=[]:
            return formated_list
        else:
            return "No cyclone occured"
