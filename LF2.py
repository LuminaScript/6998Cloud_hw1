import json
import boto3
from boto3.dynamodb.conditions import Key

def search_restaurants_from_es(es_client, cuisine):
    try:
        # Define the Elasticsearch search query
        search_query = {
            "size": 1300,
            "query": {
                "match": {
                    "Cuisine": cuisine
                }
            }
        }

        # Execute the Elasticsearch query
        es_response = es_client.search(
            index='restaurants',
            body=search_query
        )

        hits = es_response['hits']['hits']
        restaurant_ids = [str(hit['_source']['BusinessID']) for hit in hits]
        return restaurant_ids
    except Exception as e:
        print(f"Error searching Elasticsearch: {e}")
        return []

def get_restaurants_from_dynamodb(dynamodb_table, restaurant_ids):
    restaurants = []
    for restaurant_id in restaurant_ids:
        response = dynamodb_table.query(KeyConditionExpression=Key("BusinessID").eq(restaurant_id))
        for item in response.get("Items", []):
            restaurants.append(item)
    return restaurants

def lambda_handler(event, context):
    # Initialize clients
    es_client = boto3.client('es', region_name='us-east-1')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    dynamodb_table = dynamodb.Table('yelp-restaurants')
    
    # Receive and parse the SQS message
    sqs = boto3.client('sqs')
    sqs_url = "https://sqs.us-east-1.amazonaws.com/726664406105/helloworld"
    response = sqs.receive_message(
        QueueUrl=sqs_url,
        AttributeNames=['SentTimestamp'],
        MessageAttributeNames=['All'],
        VisibilityTimeout=0,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=0
    )
    
    message = response.get('Messages', [])[0]
    
    if message is None:
        print("Empty message")
    else:
        print("Not Empty Message")
        sqs.delete_message(
            QueueUrl=sqs_url,
            ReceiptHandle=message['ReceiptHandle']
        )

        print('Received and deleted message:', response)
        print("Message:", message)

        message_data = json.loads(message["Body"])
        cuisine = message_data.get("Cuisine")
        location = message_data.get("Location")
        time = message_data.get("DiningTime")
        num_of_people = message_data.get("NumberOfPeople")
        contact = message_data.get("Contact")

        if not cuisine:
            print("No Cuisine key found in the message")
            return {'statusCode': 200, 'body': json.dumps("LF2 running successfully")}

        # Query Elasticsearch for restaurant IDs
        restaurant_ids = search_restaurants_from_es(es_client, cuisine)
        
        # Query DynamoDB for restaurant details
        restaurants = get_restaurants_from_dynamodb(dynamodb_table, restaurant_ids)
        
        message_to_send = f"Hello! Here are my {cuisine} restaurant suggestions in {location} for {num_of_people} people:\n"
        for i, restaurant in enumerate(restaurants, start=1):
            message_to_send += f"{i}. {restaurant.get('Name', 'Unknown Name')}, located at {restaurant.get('Address', ['Unknown Address'])[0]} with a rating of {restaurant.get('Rating', 'Unknown Rating')}\n"
        
        message_to_send += "\nEnjoy your meal!"
        
        # Send an email using SES
        ses = boto3.client('ses', region_name='us-east-1')
        sender = 'yueqili0816@gmail.com'
        recipient = contact
        subject = "Your Customized Restaurant Recommendations"
        response = ses.send_email(
            Source=sender,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': message_to_send}}
            }
        )
        
        print("Email sent successfully")

    return {'statusCode': 200, 'body': json.dumps("LF2 running successfully")}

