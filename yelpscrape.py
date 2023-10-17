import json
import boto3
import datetime
import decimal
import http.client


url = 'api.yelp.com'
path = '/v3/businesses/search'
key = '9fPSrN94Flj8XuH__7gVV-18xpUs-6dmP4O-Mi_j7pPcIvMNnhjrltSkwaEYDrlFpKjO6xKckWwp8xTGNvOiruQf2mkwkPVixzL7cHBWVr0PGcxQdzqsD_f20yknZXYx'
client_id = 'rhysTRPrN08v-bU8fDUX5Q'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')
restaurants = set()

def lambda_handler(event, context):
    types = ['chinese', 'italian', 'american', 'korean', 'japanese']

    for cuisine in types:
        offset = 0
        while offset < 20:
            conn = http.client.HTTPSConnection(url)
            query_params = f'location=Manhattan&offset={offset*50}&limit=50&term={cuisine}+restaurants&sort_by=best_match'
            headers = {
                'Authorization': f'Bearer {key}',
            }
            conn.request("GET", f"{path}?{query_params}", headers=headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode('utf-8'))
            addItems(data["businesses"], cuisine)
            offset += 1

    return {
        'statusCode': 200,
        'body': json.dumps('Data scraped from Yelp and stored in DynamoDB!')
    }

# Add items to DynamoDB
def addItems(data, cuisine):
    global restaurants

    with table.batch_writer() as batch:
        for cur in data:
            if cur["alias"] not in restaurants:
                restaurants.add(cur["alias"])
                coordinates = {
                    'longitude': decimal.Decimal(str(cur["coordinates"]["longitude"])),
                    'latitude': decimal.Decimal(str(cur["coordinates"]["latitude"]))
                }
                response = table.put_item(
                    Item={
                        'BusinessID': cur["id"],
                        'Name': cur["name"],
                        'Address': cur["location"]["display_address"],
                        'Coordinates': coordinates,
                        'NumberOfReviews': decimal.Decimal(str(cur["review_count"])),
                        'Rating': decimal.Decimal(str(cur["rating"])),
                        'ZipCode': cur["location"]["zip_code"],
                        'Type': cuisine,
                        'InsertedAtTimestamp': str(datetime.datetime.now())
                    }
                )

