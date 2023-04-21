import openai
from dotenv import dotenv_values
from flask import session
import tiktoken

config = dotenv_values(".env") 

openai.api_key = config["openai_key"]


def trim_prompt_length(prompt, token_len):
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

    if len(encoding.encode(prompt)) > token_len:
        print(f"Prompt is too long, Need to trim, Using first {token_len} tokens")
        encoded_prompt = encoding.encode(prompt)[:token_len]
        prompt = encoding.decode( encoded_prompt )
        print("last sentence from the prompt => ", prompt[-100:])
    return prompt


def get_chat_gpt_response(previous_chat, prompt):
    
    max_input_token = 3072
    prompt = trim_prompt_length(prompt, max_input_token)
    
    msg_list = [
          {
            "role": "user",
            "content": prompt
        }
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=msg_list,
        temperature=0.0,
        top_p=1.0,
        n=3,
        stream= False,
        max_tokens= 192,
        presence_penalty= 0,
        frequency_penalty= 0
    )

    # print(completion)
    # res_str = completion["choices"][0]["message"]["content"]
    return completion


def get_chat_gpt_parameterized_response(prompt, temperature=0.0, top_p=1.0, n=1, stream=False, max_tokens=1024, presence_penalty=0, frequency_penalty=0):
    
    max_input_token = 2560
    prompt = trim_prompt_length(prompt, max_input_token)
    
    msg_list = [
          {
            "role": "user",
            "content": prompt
        }
    ]
       
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=msg_list,
        temperature=temperature,
        top_p=top_p,
        n=n,
        stream=stream,
        max_tokens=max_tokens,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty
    )

    return completion


def get_location_from_chat_gpt(user_msg):
    
    prompt = f'''Act as a NER model and find only location and datetime from the given sentence. Do not form a sentence. Strictly follow the instruction below. If none found then provide NO_DATA_FOUND.\neg.\nInput: Is it going to rain in Texas tomorrow?\nOutput: Location: Texas\nDatetime: Tomorrow\nInput: Where is Cincinnati?\nOutput: Location: Cincinnati\nDatetime: None\nInput: Who is the president?\nOutput: NO_DATA_FOUND.\nInput: {user_msg.strip()}\nOutput: '''

    max_input_token = 2560
    prompt = trim_prompt_length(prompt, max_input_token)
    
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
