import json
import boto3

def lambda_handler(event, context):
    print(event)

    session_state = event.get("sessionState", {})
    resp = {"statusCode": 200, "sessionState": session_state}

    sqs = boto3.client('sqs')
    sqs_url = "https://sqs.us-east-1.amazonaws.com/726664406105/helloworld"
    slots = event.get("interpretations", [{}])[0].get('intent', {}).get('slots', {})
    massage = {key: value["value"]["interpretedValue"] for key, value in slots.items() if value and "value" in value and "interpretedValue" in value["value"]}
    message_body = json.dumps(massage)   

    response = sqs.send_message(QueueUrl=sqs_url, MessageBody=message_body)
    return response
    # # messageBody = "Hi"
    # # ret = sqs_send.send_message(QueueUrl=sendQueueUrl, MessageBody=messageBody)
    # # sqs = boto3.resource('sqs')
    # # queue = sqs.Queue("https://sqs.us-east-1.amazonaws.com/726664406105/DiningSuggestionsQueue")
    # # print(queue.url)

    # cuisine = ['chinese', 'italian', 'indian', 'american', 'mexican']

    # slots = event.get("interpretations", [{}])[0].get('intent', {}).get('slots', {})

    # if not slots:
    #     resp["sessionState"]["dialogAction"] = {"type": "Close"}
    #     return resp

    # if "proposedNextState" in event:
    #     resp["sessionState"]["dialogAction"] = event["proposedNextState"]["dialogAction"]

    #     if not slots.get("Location") or slots["Location"]["value"]['interpretedValue'].lower() not in ["new york", "manhattan"]:
    #         resp["sessionState"]["dialogAction"] = {"type": "ElicitSlot", "intentName": "DiningSuggestionsIntent", "slotToElicit": "Location"}
    #         return resp

    #     if not slots.get("Cuisine") or slots["Cuisine"]["value"]['interpretedValue'].lower() not in [c.lower() for c in cuisine]:
    #         resp["sessionState"]["dialogAction"] = {"type": "ElicitSlot", "intentName": "DiningSuggestionsIntent", "slotToElicit": "Cuisine"}
    #         return resp

    #     if not slots.get("DiningTime"):
    #         resp["sessionState"]["dialogAction"] = {"type": "ElicitSlot", "intentName": "DiningSuggestionsIntent", "slotToElicit": "DiningTime"}
    #         return resp

    #     if not slots.get("NumberOfPeople"):
    #         resp["sessionState"]["dialogAction"] = {"type": "ElicitSlot", "intentName": "DiningSuggestionsIntent", "slotToElicit": "NumberOfPeople"}
    #         return resp

    #     if not slots.get("Contact"):
    #         resp["sessionState"]["dialogAction"] = {"type": "ElicitSlot", "intentName": "DiningSuggestionsIntent", "slotToElicit": "Contact"}
    #         return resp
    # else:
    #     resp["sessionState"]["dialogAction"] = {"type": "Close"}

    # # if all([slots.get("Location"), slots.get("Cuisine"), slots.get("DiningTime"), slots.get("NumberOfPeople"), slots.get("Contact")]):

    # message = {key: value["value"]["interpretedValue"] for key, value in slots.items() if value and "value" in value and "interpretedValue" in value["value"]}
    # response = sqs.send_message(QueueUrl=sqs_url, MessageBody=json.dumps(message))
    # print("message",message)

    # return resp
