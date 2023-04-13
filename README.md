# MyRadar Chatbot
## Steps to setup the repository.
1. Clone the repo.
2. Create a virtual environment using python3.8 or python3.9.
3. Activate the environment and install the `requirements.txt`.
4. Edit the .env file and add `openai_key` and `myradar_api_key`.
5. Initialize database using `python init_db.py`.
6. Now run the application using `python app.py`.

#

## MyRadar Chatbot Routes

- `/` 
    - The root URL will display the chatbot UI.
- `/get_chat_gpt_reply`
    - This URL is called internally to get ChatGPT reply.
- `/download_data`
    - This URL can be used to download the data from the official HURDAT2 website(https://www.nhc.noaa.gov/data/). We preprocess the downloaded data and save it on our local system so that we can access it later.

