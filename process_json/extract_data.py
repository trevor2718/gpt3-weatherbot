import json 
import os 
import datetime


def convert_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def format_float(value):
    return "{:.3f}".format(value) if value is not None else "not available"

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
    time = convert_time(weather_data.get("time"))
    summary = weather_data.get("summary")
    icon = weather_data.get("icon")
    sunrise_time = convert_time(weather_data.get("sunriseTime"))
    sunset_time = convert_time(weather_data.get("sunsetTime"))
    moon_phase = format_float(weather_data.get("moonPhase"))
    precip_intensity = format_float(weather_data.get("precipIntensity"))
    precip_intensity_max = format_float(weather_data.get("precipIntensityMax"))
    precip_intensity_max_time = convert_time(weather_data.get("precipIntensityMaxTime"))
    precip_probability = format_float(weather_data.get("precipProbability"))
    precip_type = weather_data.get("precipType")
    temperature_min = format_float(weather_data.get("temperatureMin"))
    temperature_min_time = convert_time(weather_data.get("temperatureMinTime"))
    temperature_max = format_float(weather_data.get("temperatureMax"))
    temperature_max_time = convert_time(weather_data.get("temperatureMaxTime"))
    temperature_low = format_float(weather_data.get("temperatureLow"))
    temperature_low_time = convert_time(weather_data.get("temperatureLowTime"))
    temperature_high = format_float(weather_data.get("temperatureHigh"))
    temperature_high_time = convert_time(weather_data.get("temperatureHighTime"))
    apparent_temperature_min = format_float(weather_data.get("apparentTemperatureMin"))
    apparent_temperature_min_time = convert_time(weather_data.get("apparentTemperatureMinTime"))
    apparent_temperature_max = format_float(weather_data.get("apparentTemperatureMax"))
    apparent_temperature_max_time = convert_time(weather_data.get("apparentTemperatureMaxTime"))
    apparent_temperature_low = format_float(weather_data.get("apparentTemperatureLow"))
    apparent_temperature_low_time = convert_time(weather_data.get("apparentTemperatureLowTime"))
    apparent_temperature_high = format_float(weather_data.get("apparentTemperatureHigh"))
    apparent_temperature_high_time = convert_time(weather_data.get("apparentTemperatureHighTime"))
    dew_point = format_float(weather_data.get("dewPoint"))
    wind_speed = format_float(weather_data.get("windSpeed"))
    wind_gust = format_float(weather_data.get("windGust"))
    wind_gust_time = convert_time(weather_data.get("windGustTime"))
    wind_bearing = format_float(weather_data.get("windBearing"))
    cloud_cover = format_float(weather_data.get("cloudCover"))
    humidity = format_float(weather_data.get("humidity"))
    pressure = format_float(weather_data.get("pressure"))
    visibility = format_float(weather_data.get("visibility"))
    uv_index = format_float(weather_data.get("uvIndex"))
    uv_index_time = convert_time(weather_data.get("uvIndexTime"))
    ozone = format_float(weather_data.get("ozone"))


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