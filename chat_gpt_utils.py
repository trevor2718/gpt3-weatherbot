import openai
from dotenv import dotenv_values
from flask import session

config = dotenv_values(".env") 

openai.api_key = config["openai_key"]

def get_chat_gpt_response(previous_chat, prompt):
    msg_list = [
          {
            "role": "user",
            "content": prompt
        }
    ]
    
    # print("previous_chat ", previous_chat)
    # print(" get_chat_gpt_response msg_list prompt => ", prompt )
    # print("===================================")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=msg_list )

    # print(completion)
    # res_str = completion["choices"][0]["message"]["content"]
    return completion


def get_location_from_chat_gpt(user_msg):
    
    prompt = f'''Act as a NER model and find only location and datetime from the given sentence. Do not form a sentence. Strictly follow the instruction below. If none found then provide NO_DATA_FOUND.\neg.\nInput: Is it going to rain in Texas tomorrow?\nOutput: Location: Texas\nDatetime: Tomorrow\nInput: Where is Cincinnati?\nOutput: Location: Cincinnati\nDatetime: None\nInput: Who is the president?\nOutput: NO_DATA_FOUND.\nInput: {user_msg.strip()}\nOutput: '''

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
