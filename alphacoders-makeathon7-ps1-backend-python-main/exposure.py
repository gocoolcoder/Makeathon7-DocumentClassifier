import flask
import os
import json
from flask_cors import CORS
from werkzeug import secure_filename
import classify
import time
from flask import request, jsonify
import requests

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

timestamp = str(int(time.time() * 1000))
UPLOAD_FOLDER = './uploads/'+timestamp
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload_files',methods=['POST'])
def add_tasks():
    
    try:
        collection = []
        print(request.files)
        file = request.files.to_dict()
        print(file)
        if file:
            for key,value in file.items():
                filename = secure_filename(value.filename)
                value.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                collection.append(UPLOAD_FOLDER+'/'+filename)

        response = classify.classify(collection)
    except:
        code = "FAILURE"
        message = "Module Error"
        response = json.dumps({"code": code , "message" : message})
   
    return response

@app.route('/delete',methods=['DELETE'])
def delete():
    
    try:
        data = requests.get(url = "http://localhost:3000/api/documents/") 
        data = data.text
        for i in json.loads(data):
            API_ENDPOINT = "http://localhost:3000/api/documents/" + str(i['id'])
            r = requests.delete(url = API_ENDPOINT) 
        code = "SUCCESS"
        message = "Deleted All Rows"
        response = json.dumps({"code": code , "message" : message})
    except:
        code = "FAILURE"
        message = "Delete Error"
        response = json.dumps({"code": code , "message" : message})
       
   
    return response

app.run(host='0.0.0.0')