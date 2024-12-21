import logging
import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logging.basicConfig(encoding='utf-8', format='%(asctime)s %(levelname)s  %(message)s', level=logging.DEBUG)

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive"
    ]

class auth():
    def __init__(self) -> None:
        self.token = None

    def get_credentials(self, creds_path, scopes):
        creds = None
        if self.token:
            creds = Credentials(self.token)
        elif os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, scopes
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                self.token = creds
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
        
        return creds

class gdriveOperations():
    def __init__(self, creds_path) -> None:
        self.auth_obj = auth()
        self.creds = self.auth_obj.get_credentials(creds_path, SCOPES)
    
    def list_files(self, page_size=10):
        try:
            service = build("drive", "v3", credentials= self.creds)
            fields_list = ["id", "name", "fileExtension", "trashed", "modifiedTime"]
            fields = ", ".join(fields_list)
            query = "trashed = false and  mimeType != 'application/vnd.google-apps.folder'"
            page_token = None
            
            files = []
            while True:
                results = (
                    service.files()
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
    
def main():
    creds_path = "/home/nishikanth/Projects/secrets/client_secret_699213105659-c2pc5s591ddqm9p484ds9bs31o4mqd7h.apps.googleusercontent.com.json"    
    g_ops = gdriveOperations(creds_path=creds_path)
    g_ops.list_files(1)
    
    
if __name__ == "__main__":
  main()