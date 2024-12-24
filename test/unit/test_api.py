import pytest
import io
from unittest.mock import MagicMock
from flask import Response

from app import create_app

MOCK_LIST_DATA = [
        {
            "fileExtension": "pdf",
            "id": "10Pbq2BkWzvFKcIKtIuXBmjD7CMZddHEh",
            "modifiedTime": "2024-12-24T12:14:58.000Z",
            "name": "Deloitte-SOC2.pdf",
            "parents": [
                "1xaWM-nIXdPXd_4cyC5ZnIsgfS588jrWl"
            ],
            "trashed": False
        },
    ]

MOCK_UPLOAD_FILE = {
    "id": "1OK7yAKlXFuIuTQTzSwvTNAs67Hhvd5kt"
}

MOCK_DELETE_FILE = ""

DOWNLOADED_FILE_PATH = "/tmp/abc.txt"
with open(DOWNLOADED_FILE_PATH, "+bw") as f:
    f.write(b"single line")                 
                    
@pytest.fixture()
def app(mocker):
    mock_op_obj = MagicMock()
    mock_op_obj.list_files.return_value = MOCK_LIST_DATA
    mock_op_obj.upload_file.return_value = MOCK_UPLOAD_FILE
    mock_op_obj.delete_file.return_value = MOCK_DELETE_FILE

    mock_op_obj.download_file.return_value = DOWNLOADED_FILE_PATH
    mock_gops = MagicMock()
    mock_gops.return_value = mock_op_obj
    mocker.patch("app.gdriveOperations", mock_gops)

    mock_send_file = MagicMock()
    mocker.patch("app.send_file", mock_send_file)
    mock_file_response = Response(
        response="File content here",
        status=200,
        headers={"Content-Disposition": f'attachment; filename="{DOWNLOADED_FILE_PATH}"'}
    )   
    mock_send_file.return_value = mock_file_response
    
    
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_app_healtcheck(client):
    response = client.get("/healthcheck")
    assert response._status_code == 200
    assert response.json["message"] == 'App is up and running'

def test_list_files(client):
    response = client.get("/v1/list")
    assert response._status_code == 200
    assert response.json["files"] == MOCK_LIST_DATA
    
def test_upload_file(client):
    data = {'parent_id': 'parent_id123'}
    data = {key: str(value) for key, value in data.items()}
    data['input_file'] = (io.BytesIO(b"abcdef"), 'test.jpg')
    response = client.post(
        "/v1/upload", data=data,
        content_type='multipart/form-data',
        headers = {
            "x-user-name": "mockuser1"
        }
    )
    assert response._status_code == 201
    assert response.json == MOCK_UPLOAD_FILE
    
def test_upload_file_fails_without_file_input(client):
    data = {'parent_id': 'parent_id123'}
    data = {key: str(value) for key, value in data.items()}
    response = client.post(
        "/v1/upload", data=data,
        content_type='multipart/form-data',
        headers = {
            "x-user-name": "mockuser1"
        }
    )
    assert response._status_code == 400    

def test_delete_file(client):
    response = client.delete("/v1/delete/abcd1234")
    assert response._status_code == 200
    assert response.json["data"] == MOCK_DELETE_FILE

def test_download_file(client):
    response = client.get("/v1/download/abcd1234")
    assert response._status_code == 200
    import pdb; pdb.set_trace()    
    assert response.headers['Content-Disposition'] ==  f'attachment; filename="{DOWNLOADED_FILE_PATH}"'