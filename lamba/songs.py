import boto3, json
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('music')

def lambda_handler(event, context):
    params = event.get('queryStringParameters') or {}
    artist = params.get('artist')
    title  = params.get('title')
    year   = params.get('year')
    album  = params.get('album')

    results = []

    if artist and not year and not album and not title:
        results = query('artist', artist)

    elif artist and title and not year and not album:
        results = query('artist', artist, 'title-lsi', 'title', title)

    elif artist and year and not album and not title:
        results = query('artist', artist, 'year-lsi', 'year', year)

    elif artist and album and not year and not title:
        results = query('artist', artist, 'album-lsi', 'album', album)

    elif artist and year and album and not title:
        results = [r for r in query('artist', artist, 'year-lsi', 'year', year) if r.get('album') == album]

    elif artist and year and title and not album:
        results = [r for r in query('artist', artist, 'year-lsi', 'year', year) if r.get('title','').lower() == title.lower()]

    elif artist and album and title and not year:
        results = [r for r in query('artist', artist, 'album-lsi', 'album', album) if r.get('title','').lower() == title.lower()]

    elif artist and year and album and title:
        results = [r for r in query('artist', artist, 'year-lsi', 'year', year) if r.get('album') == album and r.get('title','').lower() == title.lower()]

    elif title and not artist and not year and not album:
        results = query('title', title, 'title-gsi')

    elif title and year and not artist and not album:
        results = [r for r in query('title', title, 'title-gsi') if r.get('year') == year]

    elif title and album and not artist and not year:
        results = [r for r in query('title', title, 'title-gsi') if r.get('album') == album]

    elif title and year and album and not artist:
        results = [r for r in query('title', title, 'title-gsi') if r.get('year') == year and r.get('album') == album]

    elif year and not artist and not album and not title:
        results = query('year', year, 'year-gsi')

    elif album and not artist and not year and not title:
        results = query('album', album, 'album-gsi')

    elif year and album and not artist and not title:
        results = [r for r in query('year', year, 'year-gsi') if r.get('album') == album]

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,DELETE'},
        'body': json.dumps(results)
    }

def query(key, val, index=None, sort_key=None, sort_val=None):
    condition = Key(key).eq(val)
    if sort_key and sort_val:
        condition = condition & Key(sort_key).eq(sort_val)
    params = {'KeyConditionExpression': condition}
    if index:
        params['IndexName'] = index
    return table.query(**params).get('Items', [])