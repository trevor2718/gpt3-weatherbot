########### Python 3.2 #############

import urllib.request, json
import os 
import json

weather_key = os.environ["WEATHER_KEY"]

def get_weather(longitude,latitue,save=True):
    try:
        url = f"https://api.myradar.dev/forecast/{longitude},{latitue}?extend=hourly&units=us&lang=en"

        hdr ={
        # Request headers
        'Cache-Control': 'no-cache',
        'Subscription-Key': weather_key,
        }

        req = urllib.request.Request(url, headers=hdr)

        req.get_method = lambda: 'GET'
        response = urllib.request.urlopen(req)
        weather_data = json.loads(response.read())
        if(save):
            with open("weather.json","w") as fw:
                json.dump(weather_data, fw, indent = 6)

        return weather_data
    except Exception as e:
        print(e)

get_weather(20,-30)