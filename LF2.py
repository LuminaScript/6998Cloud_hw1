
import json
import boto3
import random
from boto3.dynamodb.conditions import Key, Attr
def getRestaurantFromES(cuisine):
    region = 'us-east-1'
    service = 'es'

    # Create an AWS session
    session = boto3.Session(region_name=region)
    credentials = session.get_credentials()

    # Set the Elasticsearch host and index
    host = 'search-restaurants-qq3egiabgr6mjj2q46kkw25v5a.us-east-1.es.amazonaws.com'
    index = 'restaurants'

    # Initialize the Elasticsearch client using boto3
    es_client = boto3.client('es', region_name=region)

    # Define the search query
    query = {
        "size": 1300,
        "query": {
            "query_string": {
                "default_field": "cuisine",
                "query": cuisine
            }
        }
    }

    # Execute the Elasticsearch query
    es_response = es_client.search(
        ElasticsearchDomain=host,
        Index=index,
        Body=json.dumps(query)
    )
    
    rest_resp = json.loads(es_response['body'].read().decode('utf-8'))
    print(rest_resp)

    hits = rest_resp['hits']['hits']
    restaurantIds = []
    for hit in hits:
        restaurantIds.append(str(hit['_source']['Business ID']))
    
    return restaurantIds

def getRestaurantFromDynamoDb(restaurantIds):
    restaurant = []
    client = boto3.resource('dynamodb')
    table = client.Table('yelp-restaurants')
    for restaurantId in restaurantIds:
        response = table.get_item(Key={'Business ID': restaurantId})
        restaurant.append(response)
    return restaurant
    
    
def lambda_handler(event, context):

    sqs = boto3.client('sqs')
    sqs_url = "https://sqs.us-east-1.amazonaws.com/726664406105/helloworld"
    resp = sqs.receive_message(
        QueueUrl=sqs_url, 
        AttributeNames=['SentTimestamp'],
        MessageAttributeNames=['All'],
        VisibilityTimeout=0,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )
    print("resp:", resp)
    message = resp['Messages'][0]
    if message is None:
        print("Empty message")
    else:
        print("Not Empty Message")
    sqs.delete_message(
            QueueUrl=sqs_url,
            ReceiptHandle=message['ReceiptHandle']
        )
    print('Received and deleted message: %s' % resp)
    print("Message: ", message)
    
    
    message = json.loads(message["Body"])
    cuisine = message["Cuisine"]
    location = message["Location"]
    time = message["DiningTime"]
    numOfPeople = message["NumberOfPeople"]
    contact = message["Contact"]
    # phoneNumber = "+1" + phoneNumber
    if not cuisine:
        print("No Cuisine or PhoneNum key found in message")
    else:
        print("Successfully parse message from queue")
        
    rest = getRestaurantFromES(cuisine)

    messageToSend = 'Hello! Here are my {cuisine} restaurant suggestions in {location} for {p} people/person: {}'.format(
            cuisine=cuisine,
            location=location,
            p = numOfPeople,
            r = rest
            
    )
    
    ses = boto3.client('ses', region_name='us-east-1')  # Use the appropriate region.

    # Define your email content
    sender = 'yueqili0816@gmail.com'
    recipient = contact
    subject = "Your Customized Resaraunt Recommendations"

    # Send the email
    response = ses.send_email(
        Source=sender,
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': messageToSend}}
        }
    )

    print("Sns_Response: ", sns_resp)
    
    
    
    return {'statusCode': 200, 'body': json.dumps("LF2 running successfully")}
