## About The Project
A small application to integrate with Gdrive. This application can authenticate to gdrive, list the files, upload a file, download a file, delete a file from users gdrive.

## Getting Started
### Installation

1. Install python 3.8 or above
2. Clone the repo
   ```sh
   git clone https://github.com/Nishikanth1/gdrive-app.git
   ```
3. Install dependencies using
   ```sh
   make install
   make setup
   ```
4. Demo: run the flask server
   ```sh
   source .venv/bin/activate
   python app.py
    ```
5. run the unit tests
   ```sh
   make unit-test
    ```
6. run the integration test.
    - export TEST_SERVICE_ACCOUNT_CREDS_PATH with path of the service account credentials needed for the integration test.
    - bring up the server
   ```sh
   source .venv/bin/activate
   python app.py  
    ```
    - open a different shell, run below command
    ```sh
        make integration-test 
    ```
## APIs
1. POST /v1/auth
2. GET /v1/list/
3. GET /v1/download/<str:fileId>
4. POST /v1/upload/
5. DELETE /v1/delete/<str:fileId>