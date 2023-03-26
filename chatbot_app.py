import os 
import openai
import streamlit as st
from streamlit_chat import message


st.title("🤖 chatBot : openAI GPT-3 for weather")
placeholder = st.empty()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

first_message = "Welcome to the chatbot, Please enter the area to get the weather details \n for example: New York "

def get_text():
    input_text = st.text_input("You: ",value="", key="input",placeholder="Please ask your questions about the weather in the region: ")
    return input_text 

region  = st.text_input("You: ",value="", key="input_",placeholder=first_message)
if(region and not st.session_state['generated']):
    st.session_state.generated.append(f"You have asked for details in region: {region}")
    st.session_state.past.append(f"I would like to know the weather details of: {region}")
    # message(st.session_state['past'][0], is_user=True, key=str(400) + '_user')
    # message(st.session_state["generated"][0], key=str(400))

user_input = get_text()
if user_input:
    output = "Testing mode on"
    st.session_state.generated.append(output)
    st.session_state.past.append(user_input)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))