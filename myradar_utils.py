import requests
import datetime
from dateparser import parse
import geocoder
import io
from contextlib import redirect_stdout
import pandas as pd
# import numpy as np

from dotenv import dotenv_values
from geopy.geocoders import Nominatim
from chat_gpt_utils import get_chat_gpt_response, get_chat_gpt_parameterized_response
from misc_utils import get_latest_csv_file
from load_hurdat_data import download_latest_data
from convert_dataset import convert_to_df

geolocator = Nominatim(user_agent="MyRadar Weather App")
config = dotenv_values(".env") 

myradar_api_key = config["myradar_api_key"]
download_dir = "hurdat_data"

latest_csv_file = get_latest_csv_file()

if not latest_csv_file:
    print("csv file data not found. initiating download")
    file_path = download_latest_data()
    if file_path:
        print("downloaded csv data ")
        df_path = convert_to_df(file_path)
        if df_path:
            print("Text data succesfully converted.")
            print("Merging the CSV file now.")
            # latest_csv_file = get_latest_csv_file()
            
            df_without_loc = pd.read_csv(df_path)
            df_with_loc = pd.read_csv(f"./csv_with_53971.csv")
            
            new_loc = df_with_loc[ ["Unnamed: 0", "location_name", "location_country", "location_region" ] ]
            with_loc_csv = pd.merge(df_without_loc, new_loc, on ='Unnamed: 0')
            
            latest_csv_file = f"{download_dir}/final_csv_data.csv"
            with_loc_csv.to_csv(latest_csv_file, index=False)
            print("Merged the csv files.")

            
        else:
            print("unable to convert text data to csv data")
            exit()
    else:
        print("Unable to download csv data. Program will exit.")
        exit()

print("latest file is => ", latest_csv_file)
df = pd.read_csv(latest_csv_file)
print(df.tail())
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


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
        
        openai_response = get_chat_gpt_response(weather_prompt)
        chatbot_reply = openai_response["choices"][0]["message"]["content"]

        return chatbot_reply, openai_response
    else:
        return "Some error occured. Unable to get the forecast details. Please try later", {}
    

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
def create_hurdat_prompt(user_query):
    print("using data from => ", latest_csv_file)
    column_names = "index, atcf_id, basin, atcf_cyclone_number_for_that_year, name, year, month, day, hours_in_utc, minutes_in_utc, record_identifier, record_identifier_desc, status_of_system, status_of_system_desc, latitude, longitude, maximum_sustained_wind_in_knots, minimum_pressure_in_millibars,location_name,location_country,location_region"
    
    prompt = f"""
Below are the HURDAT2 CSV database columns loaded into dataframe.
Dataframe Columns:
{column_names}
Sample Dataframe data:
{column_names}
53346,AL172021,AL,17,ROSE,2021,9,22,0,0,,,TS,Tropical cyclone of tropical storm intensity (34-63 knots),22.7,-37.7,35.0,1008.0,North Atlantic Ocean,,
53347,AL172021,AL,17,ROSE,2021,9,22,0,60,,,TD,Tropical cyclone of tropical depression intensity (< 34 knots),23.1,-38.1,30.0,1009.0,North Atlantic Ocean,,
53536,AL022022,AL,02,2022,BONNIE,2022,7,2,0,30,L,Landfall (center of system crossing a coastline),TS,Tropical cyclone of tropical storm intensity (34-63 knots),11.0,-83.8,50.0,996.0,Bluefields,Nicaragua,Rio San Juan
53537,AL022022,AL,02,2022,BONNIE,2022,7,2,0,60,,,TS,Tropical cyclone of tropical storm intensity (34-63 knots),11.1,-84.5,40.0,1000.0,San Carlos,Nicaragua,Rio San Juan
53575,AL022022,AL,03,2022,COLIN,2022,7,2,0,0,,,TS,Tropical cyclone of tropical storm intensity (34-63 knots),32.5,-80.4,35.0,1011.0,Colleton County,United States,South Carolina
Dataframe details:
    - Name of the cyclones are in the `name` column.
    - Name of the location is in the `location_name` column.
    - Name of the country is in the `location_country` column.
    - Name of the region is in the `location_region` column.
    - Use `location_country` column if asked about country, `location_region` if asked about region otherwise use `location_name`.
    - Use `basin` column only when user wants basin related information. 
    - Never use `record_identifier` column.
    - The cyclone which was closest approach to a coast, not followed by a landfall is denoted by `C` in `record_identifier` and if number of such cyclone asked in user query add `.groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist()` query.
    - 'HU', 'TS', 'TD', 'EX', 'SD', 'SS', 'LO', 'WV' and 'DB' are denoted in the `status_of_system` column.
    - 'atcf_cyclone_number_for_that_year' column denotes the cyclone number for that year.
    - All of the entries in `status_of_system` column except 'DB' and 'WV' are cyclone `DB` denotes Disturbance and `WV` denotes Tropical Wave.
Coding Instructions:
    - Data is there in the pandas dataframe and dataframe is defined as `df`.
    - Do not provide any written description or interpretation of the code.
    - Respond with the python code only.
    - Do not explain the code.
    - Current year is {datetime.datetime.now().year}.
    - Include `year` column in each response wherever necessary.
    - Provide year along with the cyclone names.
    - Maximum the speed cyclone has the stronger the cyclone is this is also right for Disturbance and Tropical Wave .
    - Add `.groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist()` query when there is calculation of cyclone number in any User Query if not present.
    - Strictly reply the generated code in a single print statement, if User Query is not related to HURDAT2 return 'print("cant_find")'.
    - If the latitude is greater than or equal to zero then the data is for Northern Hemisphere and if latitude is less then zero then the data is of Southern Hemisphere if number of such cyclone asked in user query add `.groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist()` query.
    - If the longitude is greater than zero then the data is for eastern Hemisphere and if longitude is less then or equal zero then the data is of Western Hemisphere if number of such cyclone asked in user query add `.groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist()` query.
    
Examples:
    - User query: Name the cyclone hit after CHANTAL?
    print(df.loc[df.loc[df['name']=='CHANTAL'].tail(1).index[0]+1]["name"])
    
    - User query: Names of cyclones hits in any year.
    print(df[df['year']==1851].groupby('atcf_cyclone_number_for_that_year')['name'].first().tolist())
    
    - User query: Number of cyclone hit in year 1996.
    print(len(df.loc[(df['year'] == 1996) & (df['status_of_system'].isin(['HU', 'TS', 'TD', 'EX', 'SD', 'SS', 'LO'])) ].groupby(['year', 'atcf_cyclone_number_for_that_year'])['name'].first().tolist()))
    
    - How many cylones hit between 1851 and 1858 that made landfall.
    print(len(df.loc[(df['year'].between(1851, 1858)) & (df['record_identifier']=='L')].groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist()))
    
    - When was KEITH hit?
    print(list(df[df['name']=='KEITH']['year'].unique()))
    
    - Is hurrican ALLEN stronger than WILMA?
    print(df.loc[(df['name']=='ALLEN') & (df['status_of_system'].isin(['HU', 'TS', 'TD', 'EX', 'SD', 'SS', 'LO']))]['maximum_sustained_wind_in_knots'].max() > df.loc[(df['name']=='WILMA') & (df['status_of_system'].isin(['HU', 'TS', 'TD', 'EX', 'SD', 'SS', 'LO']))]['maximum_sustained_wind_in_knots'].max())

    - which was the strongest cyclone in the year of 2009?
    - print(df.loc[(df['year'] == 1990) & (df['status_of_system'].isin(['HU', 'TS', 'TD', 'EX', 'SD', 'SS', 'LO', 'WV', 'DB']))]['name'][df.loc[(df['year'] == 1990) & (df['status_of_system'].isin(['HU', 'TS', 'TD', 'EX', 'SD', 'SS', 'LO', 'WV', 'DB']))]['maximum_sustained_wind_in_knots'].idxmax()])

    - If the 'cyclone' which affects maximum country asked then first find the `atcf_id` which affects the maximum country and then find the name of the cyclone for that `atcf_id`.
    - print(df.loc[df['atcf_id'] == df.groupby('atcf_id')['location_country'].nunique().idxmax(), 'name'].iloc[0])

    - which hurricane affect the most number of country?
    - print(df.loc[(df['status_of_system']=='HU') & (df['atcf_id'] == df[df['status_of_system']=='HU'].groupby('atcf_id')['location_country'].nunique().idxmax()), 'name'].iloc[0])

    - Which was the strongest cyclon ever?
    - print( df.loc[df['maximum_sustained_wind_in_knots'].idxmax(), 'name'])


    
    
Consider the Examples style code while generating new code for user query.
Use above 'Dataframe Columns', 'Sample data', 'Dataframe details' and follow the 'Coding Instructions' strictly to generate only python code.
User Query: {user_query}"""
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
        python_result = python_result.strip()
        print("python_result => ", python_result)
    
    except Exception as e:
        python_result = "Python: SyntaxError"
        print("Python: SyntaxError => ", e)
        error = e
        
    return python_result, error


def get_hurdat_response(user_msg):
    try:
        prompt = create_hurdat_prompt(user_msg)
        
        # this will get 3 responses from the ChatGPT
        response = get_chat_gpt_parameterized_response(prompt, temperature=0.0, top_p=1.0, n=3, stream=False, max_tokens=512, presence_penalty=0, frequency_penalty=0 )
        
        print("response +++ ===>> ", response["choices"])
        print("\n\n\n")
        for res in response["choices"]:
            python_code = res["message"]["content"]
            python_result, error = evaluate_code(python_code)

            if python_result and  ( python_result != "Python: SyntaxError" or ( not str(python_result).startswith("Empty DataFrame") ) or not( str(python_result).startswith("cant_find") ) ):
                break
            
        return python_result
    except Exception as e:
        print("error in get hurdat_response => ", e)
        return None
    

def get_formatted_response(user_input, gpt3_output):
    prompt = f"""Create an informative response from the given Dataframe Answer and User query. The response should be in a sentence or paragraph for the below given Dataframe Answer.
Instructions:
  - Provide a sentence-forming output from the given Dataframe Answer concerning the User query.
  - Strictly use the Dataframe Answer provided below. Do not deduce, just use the provided Dataframe Answer.
  - Use every data that is provided in Dataframe Answer. Do not miss any of the data while forming the sentence or paragraph.
  - Dataframe Answer can be in form of NumPy array, dataframe object or any of the Python datatype. Form a proper sentence or paragraph from it.
  - Remove any words that are related to programming like NumPy, dataframe or Python datatypes.
  - Form a sentence with whatever Dataframe Answer is provided.
  - 'UNNAMED' is the name of the cyclone.
  - Never use 'Dataframe Answer' as a string while generating the answer.
Examples:
    - User query: Which one was stronger between 2005 Wilma and 1980 Allen?
    Dataframe Answer: True
    1980 Allen was stronger then 2005 Wilma.
    
    - User query: Which one was stronger between 2005 Wilma and 1980 Allen?
    Dataframe Answer: False
    1980 Allen was stronger then 2005 Wilma.
    
    - User query: when was KEITH hit?
    Dataframe Answer: [1988, 2000]
    Keith cyclone hit in the year 1988 and 2000.
    
    - User query: Could I get a list with the names and ATCF ID?
    Dataframe Answer:  [['TWELVE', 'AL122022'], ['JULIA', 'AL132022'], ['KARL', 'AL142022'], ['LISA', 'AL152022'], ['MARTIN', 'AL162022'], ['NICOLE', 'AL172022']]
    The cyclone hits are as follow.
    TWELVE AL122022
    JULIA AL132022
    KARL AL142022
    LISA AL152022
    MARTIN AL162022
    NICOLE AL172022

    - User query: which cyclone affect the most number of country?
    Dataframe Answer: Unnamed
    The cyclone affects the most number of country was UNNAMED.
    
    - User query: which cyclone affect the most number of country?
    Dataframe Answer: HELENE
    The cyclone affects the most number of country was HELENE.


    
User query: {user_input}
Dataframe Answer:
{gpt3_output}"""
    response = get_chat_gpt_parameterized_response(prompt, temperature=0.0, top_p=1.0, n=1, stream=False, max_tokens=1024, presence_penalty=0, frequency_penalty=0)
    humanize_response = response["choices"][0]["message"]["content"]
    print("Humanize output from ChatGPT => ", humanize_response)
    return humanize_response


def is_valid_hurdat_response(hurdat_response):
    
    if not hurdat_response:
        return False 
    
    if str(hurdat_response).strip().startswith("Empty DataFrame"):
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