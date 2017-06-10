from flask import Flask
from flask import request
import requests




def sendData(url, json):
    headers = {'content-type': 'application/json'}
    r = requests.post(url, json=json, headers=headers)
    return r.status_code

def autorize_apiai(user_say):
    user_say.replace(" ", "%20")
    headers = {'Authorization': 'Bearer 8ea1b54f6d874008b0fd0a24f03afcfc'}
    url = "https://api.api.ai/api/query?v=20150910&query=" + user_say + "&lang=en&sessionId=a6c2c168-e045-4714-8e00-90d41941b45b&timezone=2017-06-10T15:49:44+0530"
    responce = requests.get(url=url, headers=headers)
    return responce

def fb_text_message(id, message):
    return {"recipient": {"id": id}, "message": {"text": message}}

app = Flask(__name__)

@app.route("/webhook", methods=['GET', 'POST'])
def hook():
    if request.method == 'POST':

        # Extract user message
        param = request.get_json()
        entry = param["entry"][0]
        messaging = entry["messaging"][0]
        message = messaging["message"]
        message_text = message["text"]
        print("USER SAY ", message_text)
        # Pass it to NLU engine
        apiai_result = autorize_apiai(message_text)
        print(apiai_result.json())

        # url = "https://graph.facebook.com/v2.6/me/messages?access_token=EAACksADeIqABACCgAO6SydQZCAS4WQmJhEiz5I7OycuEoiCnWClqb7Id1JER6QBg65WKMAU2Nl4YYh0f0ZBkG8oqXXa7TAlY8uS9fSh0wgNAZC1A8EcGN106s9btrKoc1dG7axeHZBOQoCz6aTz3ZCZARVAlcvGkuXBAKUFoI5xgZDZD"

        # print("APIAP res")
        # print(apiai_result.json())
        #
        #
        # message = fb_text_message("1551434831567297", "hello from swifty")
        #
        # status = sendData(url, message)
        # print(status)
        return "success"

    if request.method == 'GET':
        print(request.args.get("hub.challenge"))

        return request.args.get("hub.challenge"), 200



