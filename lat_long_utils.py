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

def create_hurdat_prompt_lat(user_query,dataframe):
    df=dataframe
    # print("using data from => ", latest_csv_file)
    column_names = "index, atcf_id, basin, atcf_cyclone_number_for_that_year, name, year, month, day, hours_in_utc, minutes_in_utc, record_identifier, record_identifier_desc, status_of_system, status_of_system_desc, latitude, longitude, maximum_sustained_wind_in_knots, minimum_pressure_in_millibars,location_name,location_country,location_region"
    
    prompt = f"""Below are the HURDAT2 CSV database columns loaded into dataframe.
Dataframe Columns:
{column_names}
Sample Dataframe data:
{df.iloc[0:5]}
Dataframe details:
    - The dataframe `df` contains data for the user query {user_query}.
    - You need to extract only columns from the df that user has asked for.
    - The dataframe df contains preprocessed data where cyclones occurred within a certain distance of a specific location. 
    - There is no need to filter by the `basin`, `location_name`, `location_country`, or `location_region` in any queries  strictly.
    - Name of the cyclones are in the `name` column.
    - 'atcf_cyclone_number_for_that_year' column denotes the cyclone number for that year.
    - Use `maximum_sustained_wind_in_knots` column for calculating the speed of the wind.
    - One `atcf_id` indicates one cyclone.
    - `atcf_id` given in order oldest first latest last.
    
Coding Instructions:
    - Data is there in the pandas dataframe and dataframe is defined as `df`.
    - Respond with the python code only.
    - Current year is {datetime.datetime.now().year}.
    - Include `year` column in each response wherever necessary.
    - Provide year along with the cyclone names.
    - Maximum the value of `maximum_sustained_wind_in_knots` cloumn has the stronger the cyclone is.
    - Add `.groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist()` query when there is calculation of cyclone number in any User Query if not present.
    - Strictly reply the code in print statement, if User Query is not related to HURDAT2 return 'print("cant_find")'.
    - Do not define variables, strictly provide code in one line.
    - Strictly do not use print more than once.

Examples:
- User query: How many cyclones occurred nearly 100 km from a specific location?
print("There were a total of", len(df.groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "cyclones that occurred nearly 100 km from the specific location.")

- User query: How many cyclones occurred nearly 100 km from a specific location in the year of 2022?
print("In 2022, there were a total of", len(df[(df['year'] == 2022)].groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "cyclones that occurred nearly 100 km from the specific location.")

- User query: How many cyclones occurred nearly 100 km from a specific location with a maximum speed of 150?
print("There were a total of", len(df[(df['maximum_sustained_wind_in_knots'] == 150)].groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "cyclones with a maximum speed of 150 that occurred nearly 100 km from the specific location.")

- User query: How many cyclones occurred nearly 100 km from Florida? And which?
print("There were a total of", len(df.groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "cyclones that occurred nearly 100 km from Florida. The cyclones are:", df.groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist())

- User query: How many hurricanes occurred nearly 10 miles from London?
print("There were a total of", len(df[(df['status_of_system'] == 'HU')].groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "hurricanes that occurred nearly 10 miles from London.")

- User query: How many hurricanes occurred nearly 10 miles from London and which?
print("There were a total of", len(df[(df['status_of_system'] == 'HU')].groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "hurricanes that occurred nearly 10 miles from London. The hurricanes are:", df[(df['status_of_system'] == 'HU')].groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist())

- User query: Any cyclone occured near 100km from florida has name ALLEN?
print('ALLEN' in df['name])

Consider the coding convention given in the Examples and follow the same code style while generating new code for user query.
Use above 'Dataframe Columns', 'Sample data', 'Dataframe details' and follow the 'Coding Instructions' strictly to generate only python code.
User Query: {user_query}"""
    # print(prompt)
    return prompt


def bak_create_hurdat_prompt_lat(user_query,dataframe):
    df=dataframe
    # print("using data from => ", latest_csv_file)
    column_names = "index, atcf_id, basin, atcf_cyclone_number_for_that_year, name, year, month, day, hours_in_utc, minutes_in_utc, record_identifier, record_identifier_desc, status_of_system, status_of_system_desc, latitude, longitude, maximum_sustained_wind_in_knots, minimum_pressure_in_millibars,location_name,location_country,location_region"
    
    prompt = f"""
Below are the HURDAT2 CSV database columns loaded into dataframe.
Dataframe Columns:
{column_names}
Sample Dataframe data:
{df.iloc[0:5]}
Dataframe details:
    - The dataframe df contains preprocessed data where cyclones occurred within a certain distance of a specific location. Strictly there is no need to filter by the `location_name`, `location_country`, or `location_region` in any queries.
    - Name of the cyclones are in the `name` column.
    - 'atcf_cyclone_number_for_that_year' column denotes the cyclone number for that year.
    - Use `maximum_sustained_wind_in_knots` column for calculating the speed of the wind.
    - One `atcf_id` indicates one cyclone.
    - `atcf_id` given in order oldest first latest last.
    
Coding Instructions:
    - Data is there in the pandas dataframe and dataframe is defined as `df`.
    - Respond with the python code only.
    - Current year is {datetime.datetime.now().year}.
    - Include `year` column in each response wherever necessary.
    - Provide year along with the cyclone names.
    - Maximum the speed cyclone has the stronger the cyclone is.
    - Add `.groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist()` query when there is calculation of cyclone number in any User Query if not present.
    - Strictly reply the code in print statement, if User Query is not related to HURDAT2 return 'print("cant_find")'.

Examples:
    - User query: How many cyclones occurred nearly 100 km from a specific location?
        print("There were a total of", len(df.groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "cyclones that occurred nearly 100 km from the specific location.")

    - User query: How many cyclones occurred nearly 100 km from a specific location in the year of 2022?
        print("In 2022, there were a total of", len(df[(df['year'] == 2022)].groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "cyclones that occurred nearly 100 km from the specific location.")

    - User query: How many cyclones occurred nearly 100 km from a specific location with a maximum speed of 150?
        print("There were a total of", len(df[(df['maximum_sustained_wind_in_knots'] == 150)].groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "cyclones with a maximum speed of 150 that occurred nearly 100 km from the specific location.")

    - User query: How many cyclones occurred nearly 100 km from Florida? And which?
        print("There were a total of", len(df.groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "cyclones that occurred nearly 100 km from Florida. The cyclones are:", df.groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist())

    - User query: How many hurricanes occurred nearly 10 miles from London?
        print("There were a total of", len(df[(df['status_of_system'] == 'HU')].groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "hurricanes that occurred nearly 10 miles from London.")

    - User query: How many hurricanes occurred nearly 10 miles from London and which?
        print("There were a total of", len(df[(df['status_of_system'] == 'HU')].groupby(['year', 'atcf_cyclone_number_for_that_year', 'name']).size()), "hurricanes that occurred nearly 10 miles from London. The hurricanes are:", df[(df['status_of_system'] == 'HU')].groupby(['year','atcf_cyclone_number_for_that_year'])['name'].first().tolist())

    Consider the Examples style code while generating new code for user query.
Use above 'Dataframe Columns', 'Sample data', 'Dataframe details' and follow the 'Coding Instructions' strictly to generate only python code.
User Query: {user_query}"""
    # print(prompt)
    return prompt


def evaluate_code_lat(python_code,dataframe):
    error = ""
    try:
        print("generated python code =>1 ", python_code)
        df=dataframe
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


def get_hurdat_response_lat(user_msg,dataframe):
    try:
        prompt = create_hurdat_prompt_lat(user_msg,dataframe)
        
        # this will get 3 responses from the ChatGPT
        response = get_chat_gpt_parameterized_response(prompt, temperature=0.0, top_p=1.0, n=3, stream=False, max_tokens=512, presence_penalty=0, frequency_penalty=0 )
        
        print("response +++ ===>> ", response["choices"])
        print("\n\n\n")
        for res in response["choices"]:
            python_code = res["message"]["content"]
            python_result, error = evaluate_code_lat(python_code,dataframe)

            if python_result and  ( python_result != "Python: SyntaxError" or ( not str(python_result).startswith("Empty DataFrame") ) or not( str(python_result).startswith("cant_find") ) ):
                break
            
        return python_result
    except Exception as e:
        print("error in get hurdat_response => ", e)
        return None
    

def get_formatted_response_lat(user_input, gpt3_output):
    prompt = f"""Create an informative response from the given Dataframe Answer and User query. The response should be in a sentence or paragraph for the below given Dataframe Answer.
Instructions:
  - Provide a sentence-forming output from the given Dataframe Answer concerning the User query.
  - Strictly use the Dataframe Answer provided below. Do not deduce, just use the provided Dataframe Answer.
  - Use every data that is provided in Dataframe Answer. Do not miss any of the data while forming the sentence or paragraph.
  - Dataframe Answer can be in form of NumPy array, dataframe object or any of the Python datatype. Form a proper sentence or paragraph from it.
  - Remove any words that are related to programming like NumPy, dataframe or Python datatypes.
  - Form a sentence with whatever Dataframe Answer is provided.
  - 'UNNAMED' is the name of the cyclone.
  - If 'Dataframe Answer' contains false or true convert that into sentence framing answer.
  - Never use 'Dataframe Answer' as a string while generating the answer.
Examples:
    - User query :Which one was stronger between 2005 Wilma and 1980 Allen?
    Dataframe Answer :True
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
User query: {user_input}
Dataframe Answer:
{gpt3_output}"""
    response = get_chat_gpt_parameterized_response(prompt, temperature=0.0, top_p=1.0, n=1, stream=False, max_tokens=1024, presence_penalty=0, frequency_penalty=0)
    humanize_response = response["choices"][0]["message"]["content"]
    print("Humanize output from ChatGPT => ", humanize_response)
    return humanize_response


def is_valid_hurdat_response_lat(hurdat_response):
    
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