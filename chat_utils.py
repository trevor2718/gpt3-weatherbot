from flask import session

def update_previous_chat(user_msg, chatbot_msg):
    if "previous_chat" in session and session['previous_chat']:
        previous_chat = session['previous_chat']
    else:
        previous_chat = f"User: {user_msg}"
        session['previous_chat']
    return previous_chat


def get_previous_chat():
    if "previous_chat" in session and session['previous_chat']:
        # print("previous chat => ", session['previous_chat'])
        session['previous_chat'] = ""
        return session['previous_chat']
    return ""


def set_previous_chat(dialogs):
    if "previous_chat" in session and session['previous_chat']:
        session['previous_chat'] += dialogs
        
        # creating ordered unique dialog list
        dialog_list = list( dict.fromkeys(session['previous_chat'].split("\n")[-10:]) )
        
        if dialog_list and dialog_list[0].startswith("Chatbot"):
            del dialog_list[0]
        session['previous_chat'] = "\n".join(dialog_list)
    else:
        session['previous_chat'] = dialogs
    return
