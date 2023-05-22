from flask import Flask, render_template,request, jsonify, send_from_directory, session
import json
import datetime
import uuid
from dotenv import dotenv_values
import geocoder
import time

# manual file imports
# from chat_utils import update_previous_chat, get_previous_chat, set_previous_chat
# from db_utils import get_db_connection, insert_to_db, check_daily_limit
from chat_gpt_utils import find_weather_question, get_chat_gpt_response, get_location_from_chat_gpt,get_distance_info,find_matching_points
from myradar_utils import get_chatbot_reply, find_datetime_location,get_hurdat_response, is_valid_hurdat_response, get_formatted_response
from load_hurdat_data import download_latest_data
from convert_dataset import convert_to_df
from lat_long_utils import *
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
    
    try:
    
        r_data = {}
        chat_uuid = ""
        location = ""
        date_time = "now"
        
        if "location" not in session:
            session["location"] = location

        if request.method == "POST":
            
            ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            user_msg = request.form.get("user_msg")
            if (user_msg is not None) or (not user_msg) or (not user_msg.strip() == ""):
                
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
                
                # check whether chat is about hurricane or weather\
                print("user msg => ", user_msg)
                distance_info = get_distance_info(user_msg)
                if distance_info not in ['not_found' , '''["not_found"]''','''['not_found']''']:
                    unique_cyclones = find_matching_points(distance_info)
                    hurdat_response_lat = get_hurdat_response_lat(user_msg,unique_cyclones)
                    hurdat_flag_lat = is_valid_hurdat_response_lat(hurdat_response_lat)

                    if hurdat_flag_lat:
                        humanize_response_lat = get_formatted_response_lat(user_msg, hurdat_response_lat)
                        humanize_response_lat = humanize_response_lat.replace("\n","<br />")
                        
                        # got the answer from the HURDAT2 database
                        cur_time = str(datetime.timedelta(seconds=666))
                        r_data = {
                            "flag": "success",
                            "msg": humanize_response_lat,
                            "time": cur_time
                        }
                        return jsonify(r_data)

                    
                    

                # break
                else:
                    hurdat_response = get_hurdat_response(user_msg)
                    hurdat_flag = is_valid_hurdat_response(hurdat_response)
                    
                    
                    # return to chatbot here if flag is true
                    if hurdat_flag:
                        # Get formatted response from ChatGPT
                        humanize_response = get_formatted_response(user_msg, hurdat_response)
                        humanize_response = humanize_response.replace("\n","<br />")
                        
                        # got the answer from the HURDAT2 database
                        cur_time = str(datetime.timedelta(seconds=666))
                        r_data = {
                            "flag": "success",
                            "msg": humanize_response,
                            "time": cur_time
                        }
                        return jsonify(r_data)
                    elif hurdat_flag=="empty":
                        humanize_response = get_formatted_response(user_msg, hurdat_response)
                        humanize_response = humanize_response.replace("\n","<br />")
                        
                        # got the answer from the HURDAT2 database
                        cur_time = str(datetime.timedelta(seconds=666))
                        r_data = {
                            "flag": "success",
                            "msg": humanize_response,
                            "time": cur_time
                        }
                        return jsonify(r_data)
                
                
                openai_response = get_location_from_chat_gpt(user_msg)
                chatbot_reply = openai_response["choices"][0]["message"]["content"]
                new_location, new_date_time = find_datetime_location(chatbot_reply)
                
                # print("NER prompt chatbot reply => ", chatbot_reply)
                # print("detecteed new location => ",new_location, "\ndetected new datetime => ", new_date_time)
                
                if new_location and new_location.strip() != "" and ( not new_location.strip().lower() == "none"):
                    # print("location detected if condition location => ", new_location)
                    # print("*****")
                    session["location"] = new_location
                
                else:
                    # print(session)
                    is_weather_question=find_weather_question(user_msg)
                    # print("*****",is_weather_question)
                    if is_weather_question == "1" and  session['location']=="":
                        cur_time = str(datetime.timedelta(seconds=666))
                        r_data = {
                            "flag": "success",
                            "msg": "Please provide the location",
                            "time": cur_time
                        }
                        session["previous_question"]= user_msg
                        
                        return jsonify(r_data)
                    else:
                        chatbot_reply, openai_response = get_chatbot_reply(user_msg, previous_chat, session["location"], date_time)
                            
                        cur_time = str(datetime.timedelta(seconds=666))
                        r_data = {
                            "flag": "success",
                            "msg": chatbot_reply,
                            "time": cur_time
                        }
                        return jsonify(r_data)
            
                if new_date_time and new_date_time.strip() != "" and ( not new_date_time.strip().lower() == "none"):
                    # print("if condition location => ", date_time)
                    date_time = new_date_time
                
                if "location" in session and session["location"]:
                    print("==================",session['location'])
                    print('location in session')
                    if "previous_question" in session and  session['previous_question'] != "":
                        print("yes")
                        user_msg = session["previous_question"] + " location:"+ user_msg 
                        session.pop("previous_question")

                    
                        chatbot_reply, openai_response = get_chatbot_reply(user_msg, previous_chat, session["location"], date_time)
                            
                        cur_time = str(datetime.timedelta(seconds=666))
                        r_data = {
                            "flag": "success",
                            "msg": chatbot_reply,
                            "time": cur_time
                        }
                        return jsonify(r_data)
                    else:
                        print('ergegegergergerg')
                        chatbot_reply, openai_response = get_chatbot_reply(user_msg, previous_chat, session["location"], date_time)
                            
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
    except Exception as e :
        # print("==========================",e)
        # if "That model is currently overloaded with other requests." in e :
        #     print("======================================++++++++++++++++++++++++++++++++++")
        #     cur_time = str(datetime.timedelta(seconds=666))
        #     r_data = {
        #         "flag": "success",
        #         "msg": "Openai is overloaded please ask the question one more time",
        #         "time": cur_time
        #     }
        #     return jsonify(r_data)

        cur_time = str(datetime.timedelta(seconds=666))
        r_data = {
            "flag": "success",
            "msg": "Answer not available in database",
            "time": cur_time
        }
        return jsonify(r_data)

        

    
@app.route('/')
def _chat_gpt():
    session.clear()
    return render_template("chat_gpt.html")


@app.route('/download_data')
def _preprocess_data():
    try:
        file_path = download_latest_data()
        print("downlaoded path => ", file_path)
        if file_path:
            df_path = convert_to_df(file_path)
            if df_path:
                return "Data loaded successfully."
            else:
                return "Could not convert the data. Please try again later."
        else:
            return "Could not load the data. Please try again later."
    except Exception as e:
        return "Error while preprocessing the data. Please try again later."


@app.route('/history', methods=["POST"])
def _history():
    conn = get_db_connection()
    data=conn.execute('''SELECT min(created) AS created, min(user_location) as user_location, min(user_ip) as user_ip, chat_uuid
    FROM chat_details
    GROUP BY chat_uuid ORDER BY id DESC;''').fetchall()
    conn.close()
    return render_template("history.html", data=data)


@app.route('/chat_history',methods=['POST'])
def chat_history():
    chat_uuid=request.args.get("chat_uuid")
    conn = get_db_connection()
    data=conn.execute("SELECT * FROM chat_details where chat_uuid=?", (chat_uuid,)).fetchall()
    conn.close()
    return render_template("index.html",data=data)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")