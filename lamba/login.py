import boto3, json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    email = body.get('email')
    password = body.get('password')

    results = table.query(
        KeyConditionExpression=Key('email').eq(email)
    )
    items = results.get('Items', [])

    if not items or items[0]['password'] != password:
        return response(401, {'message': 'email or password is invalid'})

    user = items[0]
    return response(200, {'message': 'Login successful', 'email': email, 'username': user['user_name']})

def response(status, body):
    return {
        'statusCode': status,
        'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'},
        'body': json.dumps(body)
    }