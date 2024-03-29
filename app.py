from flask import Flask, render_template,request, jsonify, send_from_directory, session
import json
import datetime
import uuid
from dotenv import dotenv_values
import geocoder
import time

# manual file imports
from chat_utils import update_previous_chat, get_previous_chat, set_previous_chat
from db_utils import get_db_connection, insert_to_db, check_daily_limit
from chat_gpt_utils import get_chat_gpt_response, get_location_from_chat_gpt
from myradar_utils import get_forecast_data, get_lat_long, get_chatbot_reply, find_datetime_location, convert_timestamp


config = dotenv_values(".env") 

app = Flask(__name__)
app.secret_key = "chatbot-app-secret"
app.config.from_object(__name__)


@app.before_request
def make_session_permanent():
    session.permanent = False


@app.route('/static/<path:path>')
def static_path(path):
    return send_from_directory('static', path)


@app.route("/reset_session", methods=["POST", "GET"])
def reset_session():
    session.clear()
    session.modified = True
    return "success"


@app.route('/get_chat_gpt_reply', methods=["POST"])
def _get_chat_gpt_reply():
    
    r_data = {}
    chat_uuid = ""
    location = "Orlando, FL"
    date_time = "now"
    
    if "location" not in session:
        session["location"] = location

    if request.method == "POST":
        
        ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        user_msg = request.form.get("user_msg")
        if (user_msg is not None) or (not user_msg) or (not user_msg.strip == ""):
            
            # set unique token per user
            if "unique_token" not in session:
                session["unique_token"] = str(uuid.uuid4())
            
            chat_uuid = session["unique_token"]

            # check max/min tokens
            if len(user_msg) > 256 or len(user_msg.split(" ")) > 128:
                r_data = {
                    "flag": "fail",
                    "msg": "Input text too large. Please provide smaller one.",
                }
                return r_data
            
            # previous_chat = get_previous_chat()
            previous_chat = ""

            # print("previous chat => ", previous_chat)
            openai_response = get_location_from_chat_gpt(user_msg)
            chatbot_reply = openai_response["choices"][0]["message"]["content"]
            new_location, new_date_time = find_datetime_location(chatbot_reply)
            
            # print("NER prompt chatbot reply => ", chatbot_reply)
            # print("detecteed new location => ",new_location, "\ndetected new datetime => ", new_date_time)
            
            if new_location and new_location.strip() != "" and ( not new_location.strip().lower() == "none"):
                # print("location detected if condition location => ", new_location)
                # print("*****")
                session["location"] = new_location
            
            if new_date_time and new_date_time.strip() != "" and ( not new_date_time.strip().lower() == "none"):
                # print("if condition location => ", date_time)
                date_time = new_date_time
            
            if "location" in session and session["location"]:
                # print("session location 92 => ", session['location'])
                chatbot_reply, openai_response = get_chatbot_reply(user_msg, previous_chat, session["location"], date_time)
                    
            g = geocoder.ip(ip_addr)
              
            # insert into db
            insert_to_db(chat_uuid, user_msg, chatbot_reply, previous_chat.replace("\n", "<br />"), json.dumps( openai_response),ip_addr, g.city )
            
            dialogs = f"{ previous_chat.strip() }\nUser: {user_msg}\nChatbot: {chatbot_reply}\n"
            
            # set previous chat most recent 10 chats
            set_previous_chat( dialogs.lstrip() )
            
            
            # not using server chat timings. just sending from sever to client
            cur_time = str(datetime.timedelta(seconds=666))
            r_data = {
                "flag": "success",
                "msg": chatbot_reply,
                "time": cur_time
            }
            return jsonify(r_data)
        else:
            # not using server chat timings. just sending from sever to client
            cur_time = str(datetime.timedelta(seconds=666))
            r_data = {
                "flag": "fail",
                "msg": "Please provide valid input.",
                "time": cur_time
            }
            return jsonify(r_data)

    
@app.route('/')
def _chat_gpt():
    return render_template("chat_gpt.html")


@app.route('/history')
def _history():
    conn = get_db_connection()
    data=conn.execute('''SELECT min(created) AS created, min(user_location) as user_location, min(user_ip) as user_ip, chat_uuid
    FROM chat_details
    GROUP BY chat_uuid ORDER BY id DESC;''').fetchall()
    conn.close()
    return render_template("history.html", data=data)


@app.route('/chat_history',methods=['GET','POST'])
def chat_history():
    chat_uuid=request.args.get("chat_uuid")
    conn = get_db_connection()
    data=conn.execute("SELECT * FROM chat_details where chat_uuid=?", (chat_uuid,)).fetchall()
    conn.close()
    return render_template("index.html",data=data)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")