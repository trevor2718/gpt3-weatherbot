import os 
import openai
import streamlit as st
from streamlit_chat import message
from get_location import  get_coordinates
from get_weather import get_weather


st.title("🤖 chatBot : openAI GPT-3 for weather")
placeholder = st.empty()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

first_message = "Welcome to the chatbot, Please enter the region to get the weather details \n" \
                "for example: New York" 

def get_text():
    input_text = st.text_input("You: ",value="", key="input",placeholder="Please ask your questions about the weather in the region: ")
    return input_text 

region  = st.text_input("Please enter the region: ",value="", key="input_",placeholder=first_message)
if(region and not st.session_state['generated']):
    # Get the full address and the coordinates based on information provided by user 
    full_address, latitude, longitude  = get_coordinates(region)
    weather_data = get_weather(latitude,longitude)
    current_temp = weather_data["currently"]["temperature"]
    if(full_address):
        st.session_state.generated.append(f"You have asked for details in region: {region} \n " \
                                            f"Full address: {full_address} \n " \
                                            f"latitude: {latitude} \n " \
                                            f"longitude: {longitude} \n" \
                                            f"Current Temperature : {current_temp} \N{DEGREE SIGN}F")
        st.session_state.past.append(f"I would like to know the weather details of: {region}")
    else:
        st.session_state.generated.append(f"{region} is not a valid region, please enter a valid region")
        st.session_state.past.append(f"")     
    region = None


user_input = get_text()
if user_input:
    output = "Testing mode on"
    st.session_state.generated.append(output)
    st.session_state.past.append(user_input)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))