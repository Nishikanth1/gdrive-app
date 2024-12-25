import logging
import sys 
import json 

from flask import Flask, request, make_response, send_file
from werkzeug.utils import secure_filename

from storage_service.gdrive import gdriveOperations, gdriveAuth
from config.constants import SCOPES, CLIENT_SECRETS_PATH, TEMP_FILE_STORAGE_PATH

def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    app.logger.addHandler(handler)
    logger = app.logger

    @app.route('/healthcheck')
    def healthcheck():
        return make_response({"message": 'App is up and running'}, 200) 
    
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
        
        auth_obj = gdriveAuth(user_name, creds_path)    
        creds = auth_obj.get_credentials(SCOPES)
        resp = make_response({}, 201)
        return resp
        
    @app.route('/v1/list')
    def list_files():
        user_name = request.headers.get('x-user-name', "")
        response = make_response({})
        try:
            g_ops = gdriveOperations(user_name=user_name)
            files = g_ops.list_files()        
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
        input_file = request.files.get('input_file')
        parent_id = request.form.get('parent_id')
        parents = [parent_id]
        logger.info(f"parents is {parents}")    
        
        if not input_file:
            err = {
                "message": "input file not found"
            }
            return make_response(err, 400)
        
        user_name = request.headers.get('x-user-name', "")
        try:
            filename = secure_filename(input_file.filename)
            filepath = f"{TEMP_FILE_STORAGE_PATH}/{filename}"
            input_file.save(filepath)
        except Exception as f_ex:
            message = f"Exception while saving upload file locally {f_ex}"
            logger.error(message)
            err = {
                "message": message
            }
            return make_response(err, 500)
        
        try:
            g_ops = gdriveOperations(user_name=user_name)
            file_info = g_ops.upload_file(filepath, parents)
        except Exception as g_ex:
            message = f"Error while uploading file to storage {g_ex}"
            logger.error(message)
            err = {
                "message": message
            }
            return make_response(err, 500)

        resp = make_response(file_info, 201)
        return resp

    @app.route('/v1/delete/<string:file_id>', methods = ['DELETE'])
    def delete_file(file_id):
        logger.info(f"file_id {file_id}")
        user_name = request.headers.get('x-user-name', "")
        try:
            g_ops = gdriveOperations(user_name=user_name)
            file_info = g_ops.delete_file(file_id=file_id)
        except Exception as g_ex:
            message = f"Error while deleting file from storage {g_ex}"
            logger.error(message)
            err = {
                "message": message
            }
            return make_response(err, 500)
        return make_response({"data": file_info}, 200)

    @app.route('/v1/download/<string:file_id>')
    def download_file(file_id):
        user_name = request.headers.get('x-user-name', "")
        try:
            g_ops = gdriveOperations(user_name=user_name)
            file_path = g_ops.download_file(file_id=file_id)
        except Exception as g_ex:
            message = f"Error while downloading file from storage {g_ex}"
            logger.error(message)
            err = {
                "message": message
            }
            return make_response(err, 500)
        return send_file(file_path, as_attachment=True)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug = True)
