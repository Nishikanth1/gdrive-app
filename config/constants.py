import os

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive"
    ]

CLIENT_SECRETS_PATH = os.environ.get("CLIENT_SECRETS_PATH","/tmp/gdrive-app/cred/")
CLIENT_TOKEN_PATH = os.environ.get("CLIENT_TOKEN_PATH","/tmp/gdrive-app/token/")
TEMP_FILE_STORAGE_PATH = os.environ.get("TEMP_FILE_STORAGE_PATH","/tmp/gdrive-app/files/")
TEMP_FILE_DOWNLOAD_PATH = os.environ.get("CLIENT_SECRETS_PATH","/tmp/gdrive-app/downloads/")


LIST_FOLDERS = os.environ.get("LIST_FOLDERS", "True").lower() == "true"

#TODO make below logic to get values from online to avoid harcoding
FILE_TYPE_MIME_TYPE = {
    "csv": "text/csv",
    "jpeg": "application/json",
    "jpg": "application/json",
    "pdf": "application/pdf",
    "xls": "application/vnd.ms-excel"
}