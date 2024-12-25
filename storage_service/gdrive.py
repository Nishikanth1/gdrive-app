import logging
import os.path
import sys
import io
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

from config.constants import SCOPES, CLIENT_TOKEN_PATH, CLIENT_SECRETS_PATH, TEMP_FILE_DOWNLOAD_PATH, \
    FILE_TYPE_MIME_TYPE, LIST_FOLDERS

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logging.basicConfig(encoding='utf-8', format='%(asctime)s %(levelname)s  %(message)s', level=logging.DEBUG)


class gdriveAuth():
    def __init__(self, user_name, creds_path) -> None:
        self.token = None
        self.token_path = f"{CLIENT_TOKEN_PATH}/token_{user_name}.json"
        self.creds_path = creds_path
        self.is_service_account = False
        with open(self.creds_path) as json_file:
            data = json.load(json_file)
            self.is_service_account= data.get("type", "").lower() == "service_account"
        logger.info(f"Created auth object {self.__dict__}")

    def get_credentials(self, scopes ):
        creds = None
        if self.is_service_account:
            logger.info(f"is_service_account {self.is_service_account} here")
            creds = service_account.Credentials.from_service_account_file(
                            self.creds_path, scopes=scopes)
            logger.info(f"service account creds is {creds.__dict__}")
            return creds        
        if self.token:
            creds = Credentials(self.token)
        elif os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_path, scopes
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                self.token = creds
                with open(self.token_path, "w") as token:
                    token.write(creds.to_json())
        
        return creds

class gdriveOperations():
    def __init__(self, user_name) -> None:
        self.user_name = user_name
        self.creds_path = f"{CLIENT_SECRETS_PATH}/{self.user_name}.json"
        self.auth_obj = gdriveAuth(self.user_name, self.creds_path)
        self.creds = self.auth_obj.get_credentials(SCOPES)
        self.gdrive_service = build("drive", "v3", credentials= self.creds)
        logging.info(f"initiated gdrive ops class with creds for user {self.user_name}")
    
    def list_files(self, page_size=10):
        try:
            logger.info(f"Listing files for user {self.user_name}")
            fields_list = ["id", "name", "fileExtension", "trashed", "modifiedTime", "parents"]
            fields = ", ".join(fields_list)
            folder_list_query = "" if LIST_FOLDERS else "mimeType != 'application/vnd.google-apps.folder'"
            query = "trashed = false " + folder_list_query
            page_token = None
            
            files = []
            while True:
                results = (
                    self.gdrive_service.files()
                    .list(pageSize=page_size, pageToken=page_token,fields=f"nextPageToken, files({fields})", q=query)
                    .execute()
                )
                items = results.get("files", [])
                page_token = results.get("nextPageToken", None)
                if not items:
                    logger.debug("No files found.")
                    return
                logger.debug("Files:")
                for item in items:
                    files.append(item)
                    logger.debug(f"{item['name']} ({item['id']}) ({item.get('fileExtension')}) ({item.get('trashed')})") 
                if not page_token:
                    return files
        except HttpError as error:
            logger.error(f"An error occurred: {error}")        
        except Exception as ex:
            logger.error(f"Exception while listing files {ex}")
    
    def upload_file(self, local_path, parents=[]):
        logger.info(f"uploading file {local_path} parents {parents}")
        file_name = local_path.split("/")[-1]
        file_type = file_name.split(".")[-1]
        mime_type = FILE_TYPE_MIME_TYPE.get(file_type, None)
        if not mime_type:
            message = f"file {file_type} type not supported, corresponding mime type not found. Please update"
            logger.error(message)
            raise Exception(message)
        file_metadata = { 
                         'name' : file_name,
                         "parents": parents,
                         "mimeType": mime_type
                        }        
        media = MediaFileUpload(local_path ,
                          mimetype=mime_type)
        file = self.gdrive_service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()
        logger.info(f"uploaded file {local_path} with response {file} file_metadata {file_metadata}")
        return file

    def delete_file(self, file_id):
        resp = self.gdrive_service.files().delete(fileId=file_id).execute()
        logger.info(f"del resp is {resp} id of file deleted: {file_id}")
        return resp
    
    def get_file(self, file_id):
        file_info = self.gdrive_service.files().get(fileId=file_id).execute()
        return file_info
    
    def download_file(self, file_id):
        file_info = self.get_file(file_id)
        logger.info(f"file info is {file_info}")
        file_name = file_info.get("name")
        
        media_data_request = self.gdrive_service.files().get_media(fileId=file_id)
        # media_data_request = service.files().export_media(
        #       fileId=item['id'], mimeType="text/csv"
        #   )
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, media_data_request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")
        print(f"media_data {file} for file {file_id}")
        
        file_path = f"{TEMP_FILE_DOWNLOAD_PATH}/{file_name}"
        with open(file_path, "+bw") as f:
            f.write(file.getvalue())
        return file_path
    
def main():
    # creds_path = "/home/nishikanth/Projects/secrets/client_secret_699213105659-c2pc5s591ddqm9p484ds9bs31o4mqd7h.apps.googleusercontent.com.json"    
    user_name = "ncs"
    g_ops = gdriveOperations(user_name)
    # g_ops.list_files(1)
    g_ops.download_file("1cn_SYzMhZUZvvGrugeix2F65PQh01x9C")
    
if __name__ == "__main__":
  main()