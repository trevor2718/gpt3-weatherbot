# gpt3-weatherbot

# Instructions to use the package 
1. Setting up of api keys, Once the keys are obtained place them keys in api_key.py file \
  weather_key = "your weather token here" \
  openapi_key = "your open api key here "

Run this command to make sure that all the changes stays in your local directly \
``` $ git update-index --skip-worktree api_key.py ``` 
  
The openapi key can be created here https://platform.openai.com/account/api-keys


2. The setup has been tested on Ubuntu 20.04 with python3.9.5 version. It is recommented to create a python environment \
 ``` $ pip install -r requirements.txt ``` \
 This might take some time to install the necessary packages 

3. To run the chatbot application use \
``` $ streamlit run chatbot_app.py ``` \
This will allow you to run the application on your local server. Copy the server in a browser and use it to interact with the chatbot. \
The chatbot has the minimal interface to test and develop the application. 

 
