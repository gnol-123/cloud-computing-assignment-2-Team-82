import boto3, json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    email = body.get('email')
    user_name = body.get('user_name')
    artist = body.get('artist')
    title = body.get('title')

    user = table.get_item(Key={'email': email, 'user_name': user_name}).get('Item')
    if not user:
        return response(404, {'message': 'Invalid User'})

    table.update_item(
        Key={'email': email, 'user_name': user_name},
        UpdateExpression='SET subscriptions = list_append(if_not_exists(subscriptions, :empty), :new)',
        ExpressionAttributeValues={':new': [{'artist': artist, 'title': title}], ':empty': []}
    )
    return response(201, {'message': 'Subscribed!'})

def response(status, body):
    return {
        'statusCode': status,
        'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'},
        'body': json.dumps(body)
    }