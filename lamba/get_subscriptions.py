import boto3, json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    params = event.get('queryStringParameters') or {}
    email = params.get('email')
    user_name = params.get('user_name')

    result = table.get_item(Key={'email': email, 'user_name': user_name}).get('Item')
    if not result:
        return response(404, {'message': 'Invalid User'})

    return response(200, result.get('subscriptions', []))

def response(status, body):
    return {
        'statusCode': status,
        'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'},
        'body': json.dumps(body)
    }