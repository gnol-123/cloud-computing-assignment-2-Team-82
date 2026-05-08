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
        return response(404, {'message': 'User not found'})

    subs = user.get('subscriptions', [])
    new_subs = [s for s in subs if not (s['artist'] == artist and s['title'] == title)]

    if len(new_subs) == len(subs):
        return response(404, {'message': f'{title} not found in subscriptions'})

    table.update_item(
        Key={'email': email, 'user_name': user_name},
        UpdateExpression='SET subscriptions = :updated',
        ExpressionAttributeValues={':updated': new_subs}
    )
    return response(200, {'message': 'Subscription removed'})

def response(status, body):
    return {
        'statusCode': status,
        'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'},
        'body': json.dumps(body)
    }