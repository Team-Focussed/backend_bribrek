#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


app = Flask(__name__)

DB_URI = os.environ.get("DB_URI")
print(DB_URI)
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
def query_records():
    endpoint = request.args.get('endpoint')
    records = Players.objects(endpoint=endpoint)
    if not endpoint:
        return jsonify({'error': 'invalid endpoint'})
    else:
        return jsonify(records.order_by("-score"))


@app.route('/', methods=['POST'])
def update_record():
    record = request.get_json()
    user = Players.objects(name=record['name'],endpoint=record['endpoint']).first()
    if not user:
        user = Players(**record).save()
        return jsonify(user.to_json()),201
    else:
        user.update(score=record['score'])
    return jsonify(user.to_json()),200


if __name__ == "__main__":
    app.run(debug=True)