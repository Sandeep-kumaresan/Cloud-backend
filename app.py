from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.mydatabase
collection = db.mycollection

@app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({'_id': str(result.inserted_id)}), 201

@app.route('/items', methods=['GET'])
def get_items():
    items = list(collection.find())
    for item in items:
        item['_id'] = str(item['_id'])
    return jsonify(items), 200

@app.route('/items/<id>', methods=['GET'])
def get_item(id):
    item = collection.find_one({'_id': ObjectId(id)})
    if item:
        item['_id'] = str(item['_id'])
        return jsonify(item), 200
    return jsonify({'error': 'Item not found'}), 404

@app.route('/items/<id>', methods=['PUT'])
def update_item(id):
    data = request.json
    result = collection.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.modified_count:
        return jsonify({'message': 'Item updated'}), 200
    return jsonify({'error': 'Item not found'}), 404

@app.route('/items/<id>', methods=['DELETE'])
def delete_item(id):
    result = collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'message': 'Item deleted'}), 200
    return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
