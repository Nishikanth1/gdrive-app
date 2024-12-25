import pytest
import requests
import json
import io

# TEST_SERVICE_ACCOUNT_CREDS_PATH = "/home/nishikanth/Projects/secrets/test-service-account.json"
# TEST_SERVICE_ACCOUNT_CREDS = {}
# with open(TEST_SERVICE_ACCOUNT_CREDS_PATH) as json_file:
#     TEST_SERVICE_ACCOUNT_CREDS = json.load(json_file)
# TODO Replace below hardcoded with above read from file
TEST_SERVICE_ACCOUNT_CREDS = {
  "type": "service_account",
  "project_id": "data-starlight-445418-k8",
  "private_key_id": "e507c9c3110492d7a31f84d491aed317a84f16ba",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC15XIVAL0wnNX+\nWqaTHw9rggK+iQ67i6eya8Wg1QCpKEkk0y9EsJ3823HRzkaRy+hNOCcE8EPhtGlA\n+cUofKR+HJNOr53J7uZExy759mUCv7aAKprhg8VJWpOOECi+C9kHOL9Ur+YfmE4U\neJPeFKs2cpACkYdoI9Y58ViVDhnjscsP0wRglgqMxXdGQGMCc8UlUY8WZtYFdYsf\nMkxJAJIA7p9fmNKAkZK8ZParYNLc8xrCtB12ZPqDvuslx427tWMdVSLX62WmXGGg\nqAJUnHEux2dDYLGIAxPTfLPdkZiQ2h5FKJq7W4UE6C423Y61yFb3Wqg2IGMwVfEU\nVjYjpS7BAgMBAAECggEADEDzyYRuOlsmc2cp95lNEaIFi05yZqIG3xcxjh8rVzn2\ni3uKoKcBTap+5XJvAJ1q/eC9iDCjcg4UVSM+a/bRoglMxy0/hP4KFzIP8RjvPxsp\nMUMtgem9na5zaEugYwUrTrg883iSGSjKgciJtZlQ228mUnX5WEOpx+eBXzE+/z66\nhbgFF5U4c92OHqDvWexsze4b8GD0wu6yXXYnSlhLozoMEGoZpRJCRxhZaEKbzOcb\nqUsRSvftMtXGNziJFbms/QIBOvfKaV5qMLyX3oLHtydYXAm9i4/jIb8Yj7TJ7XLm\nhd9fc7HndoBgLX/C0Acdq7MVqiQ7MNNPq6xOEl/DUQKBgQD+faVZKbrDuVNg7s1+\nxUZgbu8LGVDy0U1ZflG7ICS8uPBQKlKyh/teEEg4MQ9WtjHjNVMSUduOwyUarwd3\nYJzYAl9lkevcqPpPOumCwTAyTqXE2s+nFLntx+fE6HyxKCqW7fiMD+9SCsPL1Av+\nJQl+g9tF7BOoBaR7Qmfnhs4BNQKBgQC2+Zc1/k3LFTMAWt3fm8Mupo9nJGejFGnB\ntbiwNdAt6KC0xQHQ7b/RcN/GCdQA9qIa06vs0J77OAy8ZtGyYEU1MO+x99WXL8gI\nlt6HSB8r6yUVbUHqqFDvrWb9/JlrQEfayvz0V0Ra2MCrkbs5BYeappiHJ3Bx0ERO\nKOiU2Z4U3QKBgQDoV1vzSHbbpEIsODliqMb02bLiJi3SUiZVM095EQKZThsQhWNU\n3XMv0JuuuZOwbcykDBYYnqVd9GnWr7+YTJtFVv0zZQK6RYepeDaiiq/u7gDH9aEp\ngHGzVhQSoNLehrZDb2XAsfejpnJVj/WXBMdjOwyhDMRxXR1q7xift2IylQKBgQCM\naL17hnlF9S+c/x2xwQKnYtM6j/ojb7+0EXH3bmQhRplD/sXlAPyoiNh/TP1t+9Tr\nhzEwWesV1q4XSUNzgWK6baISTJ+QE++Jf9SltVeOSTS824mwu5bYRZV6JAPLBJnf\nMNOp4OmoWRqIzh0ApdioeV0kocQs4mf4HnZT+ybO1QKBgBRu9GXcwjdEOIcDmUnI\npbLquwldtVPkcFCBffRj6i9JSsmPj1ky9F2gO0VHQ/tMCQD6GWIpTTqA3ojBX/cN\nGzOLEEY+/GTNnJDZEWuTUS+doOZ3t0OAwmPsNlqCRfTF2LHBBkth1pNxLH8PEX0f\n20TB6PSfvXhCLHYsp2ESDLdC\n-----END PRIVATE KEY-----\n",
  "client_email": "integration-test-account@data-starlight-445418-k8.iam.gserviceaccount.com",
  "client_id": "117010168489787425309",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/integration-test-account%40data-starlight-445418-k8.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

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