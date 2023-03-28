import os 
import openai
import streamlit as st
from streamlit_chat import message
from get_location import  get_coordinates
from get_weather import get_weather
from process_json.extract_data import get_template
from chatbot.chat_message_history import ChatBot

info = True 



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
if(region):
    # Get the full address and the coordinates based on information provided by user 
    full_address, latitude, longitude  = get_coordinates(region)
    # Get weather from the api call 
    weather_data = get_weather(latitude,longitude)
    template_weather_data = get_template(weather_data)

    template = """  You are a chatbot having a conversation about the above weather data. 
                    You are a polite chatbot and very interactive. You must provide very accurate and correct information, 
                    If you are unsure anout an answer just ask could you provide some more information, the information you have given is insufficient. 

    {chat_history} Human: {human_input} Chatbot:"""
    template = template + template_weather_data[0:10000]

    chatbot = ChatBot(template=template)
    print(chatbot)

    current_temp = weather_data["currently"]["temperature"]
if(region and not st.session_state['generated']):
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
    output = chatbot.get_reply(user_input)
    st.session_state.generated.append(output)
    st.session_state.past.append(user_input)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))
        if(info):
            print(st.session_state['past'][i], st.session_state["generated"][i])
            print(100*"-")