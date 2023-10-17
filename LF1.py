import json
import boto3

def lambda_handler(event, context):
    print("Incoming event:", event)

    resp = {
        "statusCode": 200,
        "sessionState": event.get("sessionState", {})
    }

    # interpretations = event.get('interpretations', [{}])
    slots = event['interpretations'][0]['intent']['slots']

    res_action = {}

    sqs = boto3.client('sqs', region_name='us-east-1')
    queue = 'https://sqs.us-east-1.amazonaws.com/726664406105/resq'
    cuisines = ['chinese', 'italian', 'indian', 'american', 'mexican']
  
    current_slot_to_elicit = resp["sessionState"].get("dialogAction", {}).get("slotToElicit")
    if "proposedNextState" not in event:
        resp["sessionState"]["dialogAction"] = {"type": "Close"}
    else:
        resp["sessionState"]["dialogAction"] = event["proposedNextState"]["dialogAction"]
        if slots["Location"] is None:
            res_action = {"type": "ElicitSlot", "slotToElicit": "Location"}
            resp["sessionState"]["dialogAction"] = res_action
            print("step 1")
            return resp
        
        elif current_slot_to_elicit == "Location" and ('new york' not in slots["location"]["value"]['interpretedValue']):
            slots['Location'] = None
            res_action = {"type": "ElicitSlot", "slotToElicit": "Location"}
            resp["sessionState"]["dialogAction"] = res_action
            print("step 2")
            return resp
        
        elif slots["Cuisine"] is None:
            res_action = {"type": "ElicitSlot", "slotToElicit": "Cuisine"}
            resp["sessionState"]["dialogAction"] = res_action
            print("step 3")
            return resp
        elif current_slot_to_elicit == "Cuisine" and (slots["Cuisine"]["value"]['interpretedValue'] not in cuisines):
            slots['Cuisine'] = None
            res_action = {"type": "ElicitSlot", "slotToElicit": "Cuisine"}
            resp["sessionState"]["dialogAction"] = res_action
            print("step 4")
            return resp
        elif slots["DiningTime"] is None:
            res_action = {"type": "ElicitSlot", "slotToElicit": "DiningTime"}
            resp["sessionState"]["dialogAction"] = res_action
            print("step 5")
            return resp
        elif slots["NumberOfPeople"] is None:
            res_action = {"type": "ElicitSlot", "slotToElicit": "NumberOfPeople"}
            resp["sessionState"]["dialogAction"] = res_action
            print("step 6")
            return resp
        elif slots["Contact"] is None:
            res_action = {"type": "ElicitSlot", "slotToElicit": "Contact"}
            resp["sessionState"]["dialogAction"] = res_action
            print("step 7")
            return resp
    # print("step 8")
    massage = {key: value["value"]["interpretedValue"] for key, value in slots.items() if value and "value" in value and "interpretedValue" in value["value"]}
    message_body = json.dumps(massage)
    
    # Send the message to SQS with the correct MessageBody parameter
    response = sqs.send_message(QueueUrl=queue, MessageBody=message_body)
    print("message", massage)
    print("SQS send_message response:", response)
    print("resp",resp)
    return resp

