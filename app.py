import logging
import sys 
import json 

from flask import Flask, request, make_response
from werkzeug.utils import secure_filename

from storage_service.gdrive import gdriveOperations, gdriveAuth
from config.constants import SCOPES, CLIENT_SECRETS_PATH

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(handler)
logger = app.logger

@app.route('/healthcheck')
def hello_world():
    return 'App is up and running'

@app.route('/v1/auth', methods = ['POST'])
def auth():
    request_data = request.get_json()
    creds_json = request_data.get("creds", {})
    if not creds_json:
        resp = make_response({"message": "need creds to auth"}, 401)        
        return resp
    user_name = request_data.get("user_name", {})
    creds_path = f"{CLIENT_SECRETS_PATH}/{user_name}.json"
    with open(creds_path, "w") as f:
        json.dump(creds_json, f, ensure_ascii=False, indent=4)
    
    auth_obj = gdriveAuth(user_name)    
    creds = auth_obj.get_credentials(creds_path, SCOPES)
    resp = make_response({}, 201)
    return resp
    
    
@app.route('/v1/list')
def list_files():
    user_name = request.headers.get('x-user-name', "")
    response = make_response({})
    try:
        g_ops = gdriveOperations(user_name=user_name)
        files = g_ops.list_files(1)
        response_body = {
            "files": files
        }
        response = make_response(response_body, 200)
    except Exception as ex:
        err = {
            "message": f"list failed due to {ex}"
        }
        response = make_response(err, 500)
    return response

@app.route('/v1/upload', methods = ['POST'])
def upload_file():   
    f = request.files['input_file'] 
    if not f:
        err = {
            "message": "input file not found"
        }
        resp = make_response(err, 400)
        return resp
    
    user_name = request.headers.get('x-user-name', "")
    try:
        filename = secure_filename(f.filename)
        f.save(filename)
    except Exception as f_ex:
        message = f"Exception while saving upload file locally {f_ex}"
        logger.error(message)
        err = {
            "message": message
        }
        return make_response(err, 500)
    
    try:
        g_ops = gdriveOperations(user_name=user_name)
        file_info = g_ops.upload_file(local_path=filename)
    except Exception as g_ex:
        message = f"Error while uploading file to storage {g_ex}"
        logger.error(message)
        err = {
            "message": message
        }

    resp = make_response(file_info, 201)
    return resp
        
if __name__ == '__main__':
    app.run(debug = True)
