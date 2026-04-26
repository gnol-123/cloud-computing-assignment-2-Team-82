from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from pathlib import Path
import sys, base64

app = Flask(__name__)
app.secret_key = 'sample-key'
CORS(app, supports_credentials=True)

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
img_dir = project_root / "artifacts" / "images"
Path(img_dir).mkdir(parents=True, exist_ok=True)

from utils.DynamoDB import DynamoDB
from utils.S3 import S3

# Initialise DBs and S3 -----------------------------------------------------------------------------------

# *** (TODO) SET TABLE AND BUCKET NAMES *** #

MUSIC_TABLE = "music"
LOGIN_TABLE = "login"
S3_BUCKET = 'cloud-computing-a2-s4054917'

songsDB = DynamoDB()
songsDB.get_table(MUSIC_TABLE)


loginDB = DynamoDB()
loginDB.get_table(LOGIN_TABLE)

s3 = S3()
s3.get_bucket(S3_BUCKET)

# AUTH -----------------------------------------------------------------------------------------------------

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    result = loginDB.query(keyString='email', query=email)[0]

    print(f"result: {result}")

    if result is None:
        return jsonify({'message': 'User not found'}), 404
    if password == result['password']:

        session['email'] = email
        session['username'] = result['user_name']

        return jsonify({
            'message': 'Login successful',
            'email': email,
            'username': result['user_name']
        }), 200
    
    else:
        return jsonify({'message': 'Incorrect password'}), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'logged out'}), 200

# Querying -------------------------------------------------------------------------------------------------------------------------------------

@app.route('/songs', methods=['GET'])
def query_songs():
    artist = request.args.get('artist')
    title  = request.args.get('title')
    year   = request.args.get('year')
    album  = request.args.get('album')

    result = {}

    # artist only in main index ----------------------------------------------------------------------------------------------------------------

    if artist and not year and not album and not title:
        results = songsDB.query(keyString='artist', query=artist)
        
    # artist + title in main index -------------------------------------------------------------------------------------------------------------

    elif artist and title and not year and not album:
        results = songsDB.query(keyString='artist', query=artist, sortKeyString='title', sortKeyQuery=title)

    # artist by year in year-lsi  --------------------------------------------------------------------------------------------------------------

    elif artist and year and not album and not title:
        results = songsDB.query(keyString='artist', query=artist, indexName='year-lsi', sortKeyString='year', sortKeyQuery=year)

    # artist by album in album gsi -------------------------------------------------------------------------------------------------------------

    elif artist and album and not year and not title:
        results = songsDB.query(keyString='artist', query=artist, indexName='album-lsi', sortKeyString='album', sortKeyQuery=album)

    # artist by year by album in year-lsi ------------------------------------------------------------------------------------------------------

    elif artist and year and album and not title:
        results = songsDB.query(keyString='artist', query=artist, indexName='year-lsi', sortKeyString='year', sortKeyQuery=year)
        results = [res for res in results if res.get('album') == album]

    # artist by year by title in year-lsi ------------------------------------------------------------------------------------------------------

    elif artist and year and title and not album:
        results = songsDB.query(keyString='artist', query=artist, indexName='year-lsi', sortKeyString='year', sortKeyQuery=year)
        results = [res for res in results if res.get('title', '').lower() == title.lower()]

    # artist by album by title in album-lsi -----------------------------------------------------------------------------------------------------

    elif artist and album and title and not year:
        results = songsDB.query(keyString='artist', query=artist, indexName='album-lsi', sortKeyString='album', sortKeyQuery=album)
        results = [res for res in results if res.get('title', '').lower() == title.lower()]

    # all four using year-lsi -------------------------------------------------------------------------------------------------------------------

    elif artist and year and album and title:
        results = songsDB.query(keyString='artist', query=artist, indexName='year-lsi', sortKeyString='year', sortKeyQuery=year)
        results = [res for res in results if res.get('album') == album and res.get('title', '').lower() == title.lower()]

    # title in title-gsi ------------------------------------------------------------------------------------------------------------------------

    elif title and not artist and not year and not album:
        results = songsDB.query(keyString='title', query=title, indexName='title-gsi')

    # title by year in title gsi ----------------------------------------------------------------------------------------------------------------

    elif title and year and not artist and not album:
        results = songsDB.query(keyString='title', query=title, indexName='title-gsi')
        results = [res for res in results if res.get('year') == year]

    # title by album in title-gsi ---------------------------------------------------------------------------------------------------------------

    elif title and album and not artist and not year:
        results = songsDB.query(keyString='title', query=title, indexName='title-gsi')
        results = [res for res in results if res.get('album') == album]

    # title by year by album in title-gsi -------------------------------------------------------------------------------------------------------

    elif title and year and album and not artist:
        results = songsDB.query(keyString='title', query=title, indexName='title-gsi')
        results = [res for res in results if res.get('year') == year and res.get('album') == album]

    # year - year-gsi ---------------------------------------------------------------------------------------------------------------------------

    elif year and not artist and not album and not title:
        results = songsDB.query(keyString='year', query=year, indexName='year-gsi')

    # album - album-gsi -------------------------------------------------------------------------------------------------------------------------

    elif album and not artist and not year and not title: 
        results = songsDB.query(keyString='album', query=album, indexName='album-gsi')
    
    # year + album - year-gsi -------------------------------------------------------------------------------------------------------------------

    elif year and album and not artist and not title:
        results = songsDB.query(keyString='year', query=year, indexName='year-gsi')
        results = [res for res in results if res.get('album') == album]

    else:
        results = []

    return jsonify(results), 200

    # Get image --------------------------------------------------------------------------------------------------------------------------------

@app.route('/image/<artist>', methods=['GET'])
def get_image(artist):
    key = f"img/{artist}"
    fPath = img_dir / f"{artist}.jpg"
    s3.download(key=key, filePath=fPath)
    
    return send_file(fPath, mimetype='image/jpeg')

# main ---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)




