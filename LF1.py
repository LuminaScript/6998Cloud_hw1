import json
import boto3

def lambda_handler(event, context):
    print("Incoming event:", event)

    resp = {
        "statusCode": 200,
        "sessionState": event.get("sessionState", {})
    }

    interpretations = event.get('interpretations', [{}])
    slots = interpretations[0].get('intent', {}).get('slots', {})
    user_response = event.get('inputTranscript')

    res_action = {}

    sqs = boto3.resource('sqs')
    queue = sqs.Queue('https://sqs.us-east-1.amazonaws.com/726664406105/DiningSuggestionsQueue')
    cuisines = ['chinese', 'italian', 'indian', 'american', 'mexican']

    current_slot_to_elicit = resp["sessionState"].get("dialogAction", {}).get("slotToElicit")

    # Handle slot elicitation
    if not slots.get("Location"):
        res_action = {"type": "ElicitSlot", "slotToElicit": "Location"}

    elif current_slot_to_elicit == "Location" and user_response.lower() not in ['manhattan', 'new york']:
        slots['Location'] = None
        res_action = {"type": "ElicitSlot", "slotToElicit": "Location"}
        resp["sessionState"]["dialogAction"] = res_action
        return resp

    elif not slots.get("Cuisine"):
        res_action = {"type": "ElicitSlot", "slotToElicit": "Cuisine"}
        resp["sessionState"]["dialogAction"] = res_action
        return resp
    elif current_slot_to_elicit == "Cuisine" and user_response.lower() not in cuisines:
        slots['Cuisine'] = None
        res_action = {"type": "ElicitSlot", "slotToElicit": "Cuisine"}
        resp["sessionState"]["dialogAction"] = res_action
        return resp
    elif not slots.get("DiningTime"):
        res_action = {"type": "ElicitSlot", "slotToElicit": "DiningTime"}
        resp["sessionState"]["dialogAction"] = res_action
        return resp
    elif not slots.get("NumberOfPeople"):
        res_action = {"type": "ElicitSlot", "slotToElicit": "NumberOfPeople"}
        resp["sessionState"]["dialogAction"] = res_action
        return resp
    elif not slots.get("Contact"):
        res_action = {"type": "ElicitSlot", "slotToElicit": "Contact"}
        resp["sessionState"]["dialogAction"] = res_action
        return resp
    else:
    # all slots are filled
        if all([slots.get("Location"), slots.get("Cuisine"), slots.get("DiningTime"), slots.get("NumberOfPeople"), slots.get("Contact")]):
            massage = {key: value["value"]["interpretedValue"] for key, value in slots.items() if value and "value" in value and "interpretedValue" in value["value"]}
            response = queue.send_message(MessageBody=json.dumps(massage))
            print("SQS send_message response:", response)
        else:
            print("Not all slots filled. Skipping SQS message.")

  
    if "proposedNextState" not in event:
        resp["sessionState"]["dialogAction"] = {"type": "Close"}
    else:
        resp["sessionState"]["dialogAction"] = res_action


    return resp
