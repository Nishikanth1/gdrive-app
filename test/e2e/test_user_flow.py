import pytest
import requests
import json
import io

TEST_SERVICE_ACCOUNT_CREDS_PATH = "/home/nishikanth/Projects/secrets/test-service-account.json"
TEST_SERVICE_ACCOUNT_CREDS = {}
with open(TEST_SERVICE_ACCOUNT_CREDS_PATH) as json_file:
    TEST_SERVICE_ACCOUNT_CREDS = json.load(json_file)

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5000"

def test_user_flow(base_url):
    # auth step
    # use service account as we cannot use Oauth for api testing
    test_user_name = "ncs10"
    req_body = {
         "user_name": test_user_name,
         "creds": TEST_SERVICE_ACCOUNT_CREDS
    }
    auth_resp = requests.post(
                            f"{base_url}/v1/auth",
                            json=req_body,
                            headers = {
                                "Content-Type": 'application/json'
                            }
                    )
    assert auth_resp.status_code == 201
    assert auth_resp.json() == {}

    user_header = {
        "x-user-name":test_user_name
    }

    # verify list api
    list_resp = requests.get(
        f"{base_url}/v1/list",
        headers= user_header
        )
    assert len(list_resp.json()["files"]) > 0

    # verify upload api
    upload_file_name = "test.jpg"
    files = {
        'input_file' : (upload_file_name, io.BytesIO(b"abcdef"))
    }
    upload_response = requests.post(
        f"{base_url}/v1/upload",
        data = {},
        headers=user_header,
        files=files
    )
    upload_response_json = upload_response.json()
    uploaded_file_id = upload_response_json["id"]
    assert uploaded_file_id
    
    list_resp = requests.get(
            f"{base_url}/v1/list",
            headers= user_header
        )
    gdrive_files = list_resp.json()["files"]
    uploaded_file_exists = [file_info for file_info in gdrive_files if file_info["id"] == uploaded_file_id]
    assert uploaded_file_exists
    
    
    # download the uploaded file
    download_response = requests.get(
        f"{base_url}/v1/download/{uploaded_file_id}",
        headers= user_header
    )
    assert download_response.status_code == 200
    assert download_response.headers['Content-Disposition'] ==  f'attachment; filename={upload_file_name}'
    
    
    # delete the uploaded file
    delete_response = requests.delete(
        f"{base_url}/v1/delete/{uploaded_file_id}",
        headers=user_header
    )
    assert delete_response.status_code == 200
    
    # verify that deleted file is not found in list api
    list_resp = requests.get(
            f"{base_url}/v1/list",
            headers= user_header
        )
    gdrive_files = list_resp.json()["files"]
    uploaded_file_exists = [file_info for file_info in gdrive_files if file_info["id"] == uploaded_file_id]
    assert not uploaded_file_exists    