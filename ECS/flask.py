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

# Initialise DBs and S3
songsDB = DynamoDB()
songsDB.get_table("music")

loginDB = DynamoDB()
loginDB.get_table("login")

s3 = S3()
s3.get_bucket('cloud-computing-a2-s4054917')




