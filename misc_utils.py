import os
import glob
import requests
from dotenv import dotenv_values

config = dotenv_values(".env") 

myradar_api_key = config["myradar_api_key"]

download_dir = "hurdat_data"
pwd = os.getcwd()

def get_latest_csv_file():
    try:
        if not os.path.exists(download_dir):
            return False
        
        if not os.path.exists(f"{download_dir}/final_csv_data.csv"):
            return False
        
        csv_files = glob.glob(f"{download_dir}/*.csv")
        
        if csv_files and len(csv_files):
            # sort the files by last created time
            new_files = sorted(csv_files, key=lambda x: os.stat(x).st_atime)
            last_file = new_files[-1]
            
            # return the last created file
            return last_file
        else:
            print("No csv file found. Please hit the URL to load and process the file.")
            return False
    except Exception as e:
        print("unable to get the latest csv data file => ", e)
        return False
                
        
def get_location_name(latitude, longitude):
    try:

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
            json_data = r_data.json()
            latitude = json_data["latitude"]
            longitude = json_data["longitude"]
            return latitude, longitude

        print("please provide valid latitude and longitudes")
        return "NaN", "NaN"
    except Exception as e:
        print("error from myradar api => ", e)
        return "NaN", "NaN"
