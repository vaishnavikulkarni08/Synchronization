from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import json
import logging
import os
import time

app = Flask(__name__)
try:
    # Attempt to connect to the MongoDB Atlas cluster
    client = MongoClient('mongodb+srv://someshbhosale2:somesh@cluster0.atanct9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['synchronisation']  # Database name
    collection = db['hospitalData']
    print("Connected to MongoDB Atlas successfully!")
except Exception as e:
    print("Error connecting to MongoDB Atlas:", e)

logging.basicConfig(level=logging.DEBUG)

# Define a simple schema
hospital_schema = {
    "name": str,
    "address": str,
    "contact": str,
    "doctor": str,
    "patient": str
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/synchronize', methods=['GET'])
def synchronize():
    return render_template('synchronize.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        start_time = time.time()
        file = request.files['jsonFile']
        if file.filename.endswith('.json'):
            # Get the size of the uploaded file
            file_size = os.path.getsize(file.filename)
            data = json.load(file)
            if isinstance(data, list):
                for document in data:
                    if isinstance(document, dict):
                        collection.insert_one(document)
                    else:
                        raise ValueError("Document must be a dictionary")
            else:
                raise ValueError("Data must be a list of dictionaries")
            end_time = time.time()
            upload_time = end_time - start_time
            # Convert bytes to kilobytes
            file_size_kb = file_size / 1024
            logging.info("Hospital data Uploaded Successfully !")
            return jsonify({'message': 'Hospital data Uploaded Successfully !', 'upload_time': upload_time, 'file_size': file_size_kb})
        else:
            logging.error("Invalid file format")
            return jsonify({'error': 'Invalid file format'})
    except Exception as e:
        logging.error("Error uploading hospital data: %s", e)
        return jsonify({'error': 'Error uploading hospital data'})

@app.route('/retrieve', methods=['GET'])
def retrieve_data():
    try:
        # Retrieve all hospital data from MongoDB collection
        data = list(collection.find({}))
        # Convert ObjectId to string for _id fields
        for document in data:
            document['_id'] = str(document['_id'])
        logging.info("Hospital data retrieved from the database")
        return jsonify({'data': data})  # Convert to JSON and return as an object with 'data' key
    except Exception as e:
        logging.error("Error retrieving hospital data from the database: %s", e)
        return jsonify({'error': 'Error retrieving hospital data from the database'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
