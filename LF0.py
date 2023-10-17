import boto3
client = boto3.client('lexv2-runtime')
def lambda_handler(event, context):
    
    msg_from_user = event['messages'][0]['unstructured']['text']
    
    print(f"Message from frontend: {msg_from_user}")
    
    # Initiate conversation with Lex
    response = client.recognize_text(
                                botId='JGMME1KT7Z', # MODIFY HERE
                                botAliasId='TSTALIASID', # MODIFY HERE
                                localeId='en_US',
                                sessionId='testuser',
                                text=msg_from_user)
    
    msg_from_lex = response.get('messages', [])
    if msg_from_lex:
        
        print(f"Message from Chatbot: {msg_from_lex[0]['content']}")
        print(response)
        
        resp = {
                    'statusCode': 200,
                    'messages': [
                        {
                            'type': "unstructured",
                            'unstructured': {
                                'text': msg_from_lex[0]['content']
                            }
                        }
                    ]
        }
        return resp
