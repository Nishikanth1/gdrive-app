import os

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive"
    ]

CLIENT_SECRETS_PATH = os.get("CLIENT_SECRETS_PATH","/tmp/gdrive-app/cred/")
CLIENT_TOKEN_PATH = os.get("CLIENT_TOKEN_PATH","/tmp/gdrive-app/token/")
TEMP_FILE_STORAGE_PATH = os.get("TEMP_FILE_STORAGE_PATH","/tmp/gdrive-app/files/")
TEMP_FILE_DOWNLOAD_PATH = os.get("CLIENT_SECRETS_PATH","/tmp/gdrive-app/downloads/")