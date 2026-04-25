from flask import Flask, request, jsonify, session
from flask_cors import CORS
from pathlib import Path
import sys

app = Flask(__name__)
app.secret_key = 'sample-key'
CORS(app, supports_credentials=True)

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.DynamoDB import DynamoDB
from utils.S3 import S3

# Initialise DBs and S3 -----------------------------------------------------------------------------------

songsDB = DynamoDB()
songsDB.get_table("music")

loginDB = DynamoDB()
loginDB.get_table("login")

s3 = S3()
s3.get_bucket('cloud-computing-a2-s4054917')

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

