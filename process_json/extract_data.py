import json 
import os 
import datetime


def convert_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def data_template_hourly(weather_data):

    # Convert the UNIX timestamp to a datetime object
    timestamp = datetime.datetime.fromtimestamp(weather_data.get("time", 0))

    # Generate the paragraph
    paragraph = f"At {timestamp:%I:%M %p} on {timestamp:%A, %B %d, %Y}, the current weather condition is {weather_data.get('summary', 'not available')}. " \
            f"The temperature is {weather_data.get('temperature', 'not available')} degrees Fahrenheit, with an apparent temperature of {weather_data.get('apparentTemperature', 'not available')} degrees Fahrenheit. " \
            f"The dew point is {weather_data.get('dewPoint', 'not available')} degrees Fahrenheit, and the relative humidity is {weather_data.get('humidity', 'not available') * 100}%. " \
            f"The wind speed is {weather_data.get('windSpeed', 'not available')} miles per hour, with gusts up to {weather_data.get('windGust', 'not available')} miles per hour from the direction of {weather_data.get('windBearing', 'not available')} degrees. " \
            f"The cloud cover is {weather_data.get('cloudCover', 'not available')}, and the visibility is {weather_data.get('visibility', 'not available')} miles. " \
            f"The atmospheric pressure is {weather_data.get('pressure', 'not available')} millibars, and the ozone level is {weather_data.get('ozone', 'not available')}. " \
            f"There is a {weather_data.get('precipProbability', 'not available') * 100}% chance of {weather_data.get('precipType', 'not available')} " \
            f"with an intensity of {weather_data.get('precipIntensity', 'not available')} inches per hour. " \
            f"The UV index is {weather_data.get('uvIndex', 'not available')}."

    return paragraph

def data_template_daily(weather_data):

    # Extract data from dictionary
    time = convert_time(weather_data.get("time", 0 ))
    summary = weather_data.get("summary" ,'not available')
    icon = weather_data.get("icon",'not available')
    sunrise_time = convert_time(weather_data.get("sunriseTime",0))
    sunset_time = convert_time(weather_data.get("sunsetTime",0))
    moon_phase = weather_data.get("moonPhase",'not available')
    precip_intensity = weather_data.get("precipIntensity",'not available')
    precip_intensity_max = weather_data.get("precipIntensityMax",'not available')
    precip_intensity_max_time = convert_time(weather_data.get("precipIntensityMaxTime",0))
    precip_probability = weather_data.get("precipProbability",'not available')
    precip_type = weather_data.get("precipType",'not available')
    temperature_min = weather_data.get("temperatureMin",'not available')
    temperature_min_time = convert_time(weather_data.get("temperatureMinTime",0))
    temperature_max = weather_data.get("temperatureMax",'not available')
    temperature_max_time = convert_time(weather_data.get("temperatureMaxTime",0))
    temperature_low = weather_data.get("temperatureLow",'not available')
    temperature_low_time = convert_time(weather_data.get("temperatureLowTime",0))
    temperature_high = weather_data.get("temperatureHigh",'not available')
    temperature_high_time = convert_time(weather_data.get("temperatureHighTime",0))
    apparent_temperature_min = weather_data.get("apparentTemperatureMin",0)
    apparent_temperature_min_time = convert_time(weather_data.get("apparentTemperatureMinTime",0))
    apparent_temperature_max = weather_data.get("apparentTemperatureMax",'not available')
    apparent_temperature_max_time = convert_time(weather_data.get("apparentTemperatureMaxTime",0))
    apparent_temperature_low = weather_data.get("apparentTemperatureLow",'not available')
    apparent_temperature_low_time = convert_time(weather_data.get("apparentTemperatureLowTime",0))
    apparent_temperature_high = weather_data.get("apparentTemperatureHigh",'not available')
    apparent_temperature_high_time = convert_time(weather_data.get("apparentTemperatureHighTime",0))
    dew_point = weather_data.get("dewPoint",'not available')
    wind_speed = weather_data.get("windSpeed",'not available')
    wind_gust = weather_data.get("windGust",'not available')
    wind_gust_time = convert_time(weather_data.get("windGustTime",0))
    wind_bearing = weather_data.get("windBearing",'not available')
    cloud_cover = weather_data.get("cloudCover",'not available')
    humidity = weather_data.get("humidity",'not available')
    pressure = weather_data.get("pressure",'not available')
    visibility = weather_data.get("visibility",'not available')
    uv_index = weather_data.get("uvIndex",'not available')
    uv_index_time = convert_time(weather_data.get("uvIndexTime",0))
    ozone = weather_data.get("ozone",'not available')


    # Generate paragraph
    paragraph = f"On {time}, the weather is expected to be {summary} The current condition is {icon} with a chance of rain. "
    paragraph += f"Sunrise is at {sunrise_time}, and sunset is at {sunset_time}. The moon phase is {moon_phase}. "
    paragraph += f"There is a {precip_probability}% chance of precipitation, with a {precip_intensity} inches per hour intensity "
    paragraph += f"and a maximum intensity of {precip_intensity_max} inches per hour at {precip_intensity_max_time}. "
    paragraph += f"The precipitation type is expected to be {precip_type}."
    paragraph += f"On this day, the minimum temperature is expected to be {temperature_min} degrees Fahrenheit, occurring at {temperature_min_time}. "
    paragraph += f"The maximum temperature is expected to be {temperature_max} degrees Fahrenheit, occurring at {temperature_max_time}. "
    paragraph += f"During the day, the temperature high will reach {temperature_high} degrees Fahrenheit at {temperature_high_time}, "
    paragraph += f"and the temperature low will reach {temperature_low} degrees Fahrenheit at {temperature_low_time}. "
    paragraph += f"The apparent temperature will be a minimum of {apparent_temperature_min} degrees Fahrenheit at {apparent_temperature_min_time}, "
    paragraph += f"and a maximum of {apparent_temperature_max} degrees Fahrenheit at {apparent_temperature_max_time}. "
    paragraph += f"The apparent temperature high will reach {apparent_temperature_high} degrees Fahrenheit at {apparent_temperature_high_time}, "
    paragraph += f"and the apparent temperature low will reach {apparent_temperature_low} degrees Fahrenheit at {apparent_temperature_low_time}."
    paragraph += f"The dew point temperature is {dew_point} degrees Fahrenheit. "
    paragraph += f"The wind speed is {wind_speed} mph with gusts up to {wind_gust} mph at {wind_gust_time}, "
    paragraph += f"blowing from {wind_bearing} degrees. "
    paragraph += f"The cloud cover is {cloud_cover} and the humidity is {humidity}. "
    paragraph += f"The atmospheric pressure is {pressure} millibars and visibility is {visibility} miles. "
    paragraph += f"The UV index is {uv_index} at {uv_index_time}. "
    paragraph += f"The ozone level is {ozone} dobson units."

    return paragraph

def data_alerts(weather_data):
    # Convert the UNIX timestamp to a datetime object
    timestamp_start = datetime.datetime.fromtimestamp(weather_data.get("time", 0))
    timestamp_stop = datetime.datetime.fromtimestamp(weather_data.get("expires", 0))

    # Generate the paragraph
    paragraph = f" You are requested to pay attention to the alert \n" \
                f"Alert {weather_data.get('severity', 'not available')} " \
                f"{weather_data.get('title', 'not available')} has been issued for the region " \
                f" From {timestamp_start:%I:%M %p} on {timestamp_start:%A, %B %d, %Y}  to " \
                f" to {timestamp_stop:%I:%M %p} on {timestamp_stop:%A, %B %d, %Y}  to " \
                f"The details of the warning are {weather_data.get('description', 'not available')} \n\n" 
    return paragraph 

def get_template(weather_data):

    current_data = data_template_hourly(weather_data["currently"])

    hourly_data = "" 
    for d in weather_data["hourly"]["data"]:
        hourly_data = hourly_data + data_template_hourly(d)
        hourly_data = hourly_data + "\n"
    hour_summary = weather_data["hourly"]["summary"]
    hour_icon = weather_data["hourly"]["icon"]

    daily_data = "" 
    for d in weather_data["daily"]["data"]:
        daily_data = daily_data + data_template_daily(d)
        daily_data = daily_data + "\n"
    daily_summary = weather_data["daily"]["summary"]
    daily_icon = weather_data["daily"]["icon"]
        
    template = f"The weather details for region with {weather_data.get('latitude', 'not available')} and " \
            f"longitude {weather_data.get('longitude', 'not available')} which is in timezone " \
            f"{weather_data.get('imezone', 'not available')} \n\n" \
            f"Weather details right now are {current_data} \n\n\n" \
            f"For the next few hours the weather is predicted as {hour_summary} with {hour_icon} \n" \
            f"For the each hour the weather details are {hourly_data} \n\n\n" \
            f"For the next few days the weather is predicted as {daily_summary} with {daily_icon} \n" \
            f"For the each hour the weather details are {daily_data} \n\n\n"          

    if("alerts" in weather_data):
        alerts = weather_data["alerts"]
        alert_data = "" 
        for d in alerts:
            alert_data = alert_data + data_alerts(d)
        template = template + alert_data

    return template 