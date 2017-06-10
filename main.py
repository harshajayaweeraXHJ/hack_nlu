from flask import Flask
from flask import request
from concurrency_module import ThreadPool
import requests

pool = ThreadPool(10)

# Simple domain ontology map
entity_map = {}
entity_map["age_group"]["mother"] = "50 +"
entity_map["gender"]["mother"] = "Female"



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

def is_all_slot_filled(parameter):
    is_allslot_filled = True
    for key in parameter:
        if not parameter[key]:
            is_allslot_filled = False
    return is_allslot_filled and bool(parameter)

def query_items(spec_json, end_point):
    responce = requests.get(url=end_point)
    return responce

def derive_query_spec(entity_map):


def handle_message(param):
    URL = "https://graph.facebook.com/v2.6/me/messages?access_token=EAACksADeIqABACCgAO6SydQZCAS4WQmJhEiz5I7OycuEoiCnWClqb7Id1JER6QBg65WKMAU2Nl4YYh0f0ZBkG8oqXXa7TAlY8uS9fSh0wgNAZC1A8EcGN106s9btrKoc1dG7axeHZBOQoCz6aTz3ZCZARVAlcvGkuXBAKUFoI5xgZDZD"
    print("fb input ", param)
    entry = param["entry"][0]
    messaging = entry["messaging"][0]
    message = messaging["message"]
    message_text = message["text"]
    print("USER SAY ", message_text)
    # Pass it to NLU engine
    apiai_result = autorize_apiai(message_text)
    apiai_result_json = apiai_result.json()
    print(apiai_result_json)

    if not bool(is_all_slot_filled(apiai_result_json["result"]["parameters"])):
        fulfillment = apiai_result_json["result"]["fulfillment"]
        speech = fulfillment["speech"]
        print("BOT SAY ", speech)
        message = fb_text_message("1551434831567297", speech)
        status = sendData(URL, message)
        print(status)

    else:
        event = apiai_result_json["result"]["parameters"]["any"]
        color = apiai_result_json["result"]["parameters"]["color"]
        item = apiai_result_json["result"]["parameters"]["item"]
        receiver = apiai_result_json["result"]["parameters"]["receiver"]

        print("BOT SAY Quering using ", event, " ", color, " ", item, " ", receiver)

        query_items()

        message = fb_text_message("1551434831567297",
                                  "Quering using " + event + " " + color + " " + item + " " + receiver)
        status = sendData(URL, message)
        print(status)


app = Flask(__name__)

@app.route("/webhook", methods=['GET', 'POST'])
def hook():
    if request.method == 'POST':
        # Extract user message
        param = request.get_json()
        pool.map(handle_message, [param])









        # print("APIAP res")
        # print(apiai_result.json())
        #
        #
        # message = fb_text_message("1551434831567297", "hello from swifty")
        #
        # status = sendData(url, message)
        # print(status)
        return str(200)

    if request.method == 'GET':
        print(request.args.get("hub.challenge"))
        print("Subscribed............................................................")
        return request.args.get("hub.challenge"), 200



