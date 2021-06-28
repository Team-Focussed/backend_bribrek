#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_mongoengine import MongoEngine
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


DB_URI = os.environ.get("DB_URI")
#print(DB_URI)
app.config["MONGODB_HOST"] = DB_URI

db = MongoEngine()
db.init_app(app)

class Players(db.Document):
    name = db.StringField(required=True)
    score = db.IntField(default=0)
    endpoint = db.StringField(required=True)
    def to_json(self):
        return {"name": self.name,
                "score": self.score}

@app.route('/', methods=['GET'])
@cross_origin()
def query_records():
    endpoint = request.args.get('endpoint')
    top = request.args.get('top')
    if not top:
        top = 10
    else:
        top = int(top)
    print(top)
    records = Players.objects(endpoint=endpoint).limit(top)
    if not endpoint:
        return jsonify({'error': 'invalid endpoint'})
    else:
        return jsonify(records.order_by("-score"))
    
@app.route('/me', methods=['GET'])
@cross_origin()
def query_records_me():
    name = request.args.get('name')
    endpoint = request.args.get('endpoint')
    records = Players.objects(endpoint=endpoint).order_by("-score").as_pymongo()
    position = 1
    for i in records:
        i["position"] = position
        position += 1
        if i["name"] == name and i["endpoint"] == endpoint:
            del i["_id"]
            return jsonify(i)
        
    return jsonify({'error': 'no such record or no name provided'})
        
  
    



@app.route('/', methods=['POST'])
@cross_origin()
def update_record():
    record = request.get_json()
    print(record)
    user = Players.objects(name=record['name'],endpoint=record['endpoint']).first()
    if not user:
        user = Players(**record).save()
        return jsonify(user.to_json()),201
    elif record['score'] > user['score']:
        print("updated!")
        user.update(score=record['score'])
    return jsonify(user.to_json()),200


if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True)