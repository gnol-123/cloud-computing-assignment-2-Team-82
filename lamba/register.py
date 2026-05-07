import boto3, json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    email = body.get('email')
    username = body.get('user_name')
    password = body.get('password')

    if not email or not username or not password:
        return response(400, {'message': 'All fields are required'})

    existing = table.query(KeyConditionExpression=Key('email').eq(email))
    if existing.get('Items'):
        return response(409, {'message': 'The email already exists'})

    table.put_item(Item={'email': email, 'user_name': username, 'password': password})
    return response(201, {'message': 'Registration successful'})

def response(status, body):
    return {
        'statusCode': status,
        'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'},
        'body': json.dumps(body)
    }