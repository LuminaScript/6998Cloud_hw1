
import json
import boto3
import random
from boto3.dynamodb.conditions import Key, Attr

def connect():
    sqs_client = boto3.client('sqs', region_name='us-east-1')
    sqs_url = 'https://sqs.us-east-1.amazonaws.com/726664406105/resq'

    resp = sqs_client.receive_message(
        QueueUrl=sqs_url, 
        AttributeNames=['SentTimestamp'],
        MessageAttributeNames=['All'],
        VisibilityTimeout=0,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )

    try:
        if 'Messages' in resp:
            print("There are messages in Resp")
            message_attribute = resp['Messages'][0]
            query = json.loads(message_attribute['Body'])
            receipt_handle = message_attribute['ReceiptHandle']
            sqs_client.delete_message(QueueUrl=sqs_url, ReceiptHandle=receipt_handle)
            return query
    except: 
        print("Pull SQS message failed")
        return {}

def loadsInit(received):
    msg_detail = received
    location = msg_detail['Location']
    cuisine_type = msg_detail['Cuisine']
    rev_time = msg_detail['DiningTime']
    num_people = msg_detail['NumberOfPeople']
    phone_num = msg_detail['Contact']
    send_message = "Hello! Here are my {} restaurant suggestions in Manhattan for {} people for today at {}".format(cuisine_type, num_people, rev_time)
    return phone_num, send_message, cuisine_type

def recommend(cuisine):
    cuisine_to_restaurants = {
        'chinese': ['restaurant_id_1', 'restaurant_id_2', 'restaurant_id_3'],
        'italian': ['restaurant_id_4', 'restaurant_id_5', 'restaurant_id_6'],
        # ... other cuisines and their restaurant IDs
    }
    return cuisine_to_restaurants.get(cuisine, [])

def searchDB(recommendsID, send_message):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-restaurants')

    for track, id in enumerate(recommendsID, 1):
        response = table.scan(FilterExpression=Attr('id').eq(id))
        try: 
            item = response['Items'][0]
            name = item["name"]
            address = ' '.join(item["address"])
            curMsg = ' {0}. {1}, located at {2}.'.format(track, name, address)
            send_message += curMsg
        except:
            print("DynamoDB Response Failed")

    send_message += " Enjoy your meal!"
    return send_message

def sendSNS(phone_num, message):
    final_num = phone_num if phone_num.startswith('+1') else '+1' + phone_num
    client = boto3.client('sns')
    try:
        response = client.publish(PhoneNumber=final_num, Message=message)
    except KeyError:
        print("SNS send failed")

def lambda_handler(event, context):
    received = connect()
    if not received:
        return {'statusCode': 200, 'body': json.dumps("No message in SQS, LF2 exited early.")}

    phone_num, send_message, cuisine_type = loadsInit(received)
    recommendsID = recommend(cuisine_type)
    if not recommendsID:
        return {'statusCode': 200, 'body': json.dumps("No recommendations found for given cuisine, LF2 exited early.")}

    final_message = searchDB(recommendsID, send_message)
    sendSNS(phone_num, final_message)

    return {'statusCode': 200, 'body': json.dumps("LF2 running successfully")}
