from flask import Flask
from flask import request
from concurrency_module import ThreadPool
import requests

pool = ThreadPool(10)

# Simple domain ontology map
ontology_entity_map = {"age_group" : {"mother" : "50 +"}, "gender" : {"mother" : "Female"}}



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

def fb_generic_template(id, message):
    return {"recipient": {"id": id}, "message": message["message"]}

def is_all_slot_filled(parameter):
    is_allslot_filled = True
    for key in parameter:
        if not parameter[key]:
            is_allslot_filled = False
    return is_allslot_filled and bool(parameter)

def query_items(spec_json, end_point):
    headers = {'content-type': 'application/json'}
    responce = requests.post(url=end_point, json=spec_json, headers=headers)
    return responce.json()

def derive_query_spec(entity_map):
    query_spec = {"name" : "", "description" : "", "price" :"", "brand" : "", "category" : "", "size" : "", "gender" : "", "age_group" : "", "color" : ""}

    query_spec["category"]  = entity_map["item"]

    query_spec["color"]  = entity_map["color"]
    receiver = entity_map["receiver"]
    receiver = receiver.lower()

    query_spec["age_group"] = ontology_entity_map["gender"][receiver]

    query_spec["gender"] = ontology_entity_map["age_group"][receiver]

    return query_spec


def generate_template_carousel(items):
    carousel = { "message": { "attachment": { "type": "template", "payload": { "template_type": "generic", "elements": [] } } }}
    elements = []
    for item in items:
        element = { "title": "", "image_url": "", "subtitle": "", "buttons": [ { "type": "postback", "title": "Buy now", "payload": "DEVELOPER_DEFINED_PAYLOAD" } ] }
        element["image_url"] = item["image_url"]
        element["title"] = item["name"]
        element["subtitle"] = item["description"] + ". " + item["price"]
        elements.append(element)
        print("elements", elements)
    carousel["message"]["attachment"]["payload"]["elements"] = elements
    return carousel

def handle_message(param):
    URL = "https://graph.facebook.com/v2.6/me/messages?access_token=EAACksADeIqABACCgAO6SydQZCAS4WQmJhEiz5I7OycuEoiCnWClqb7Id1JER6QBg65WKMAU2Nl4YYh0f0ZBkG8oqXXa7TAlY8uS9fSh0wgNAZC1A8EcGN106s9btrKoc1dG7axeHZBOQoCz6aTz3ZCZARVAlcvGkuXBAKUFoI5xgZDZD"
    INVENTORY_ENDPOINT = "https://da7c56dc.ngrok.io/api/getResults"


    print("fb input ", param)
    entry = param["entry"][0]
    messaging = entry["messaging"][0]

    SENDER_ID = messaging["sender"]["id"]

    message = messaging["message"]
    message_text = message["text"]

    # Pass it to NLU engine
    apiai_result = autorize_apiai(message_text)
    apiai_result_json = apiai_result.json()
    print(apiai_result_json)

    if not bool(is_all_slot_filled(apiai_result_json["result"]["parameters"])):
        fulfillment = apiai_result_json["result"]["fulfillment"]
        speech = fulfillment["speech"]
        print("BOT SAY ", speech)
        message = fb_text_message(SENDER_ID, speech)
        status = sendData(URL, message)
        print(status)

    else:


        required_entities = apiai_result_json["result"]["parameters"]
        query_spec = derive_query_spec(required_entities)
        suggested_items = query_items(query_spec, INVENTORY_ENDPOINT)
        template_carousel =generate_template_carousel(suggested_items)

        msg = fb_text_message(SENDER_ID, "Gotcha! I found following designs are very popular these days :D")
        status = sendData(URL, msg)
        print(status)

        generic_template =fb_generic_template(SENDER_ID, template_carousel)
        status = sendData(URL, generic_template)
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



