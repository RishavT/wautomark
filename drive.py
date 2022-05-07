"""Drive utils"""
import sys
import os
import json

from pydrive2.drive import GoogleDrive
from pydrive2.auth import GoogleAuth

SA_JSON_PATH = "sa.json"
DRIVE_JSON_PATH = "drive.json"


def get_pydrive2_service():
    """Returns the pydrive2.drive.GoogleDrive object"""
    auth = GoogleAuth()
    with open(SA_JSON_PATH, encoding="utf-8") as file:
        sa_json = json.load(file)
    auth.settings["service_config"] = {
        "client_json_file_path": SA_JSON_PATH,
        "client_user_email": sa_json["client_email"],
    }
    auth.ServiceAuth()
    return GoogleDrive(auth)


def get_folder_link_from_id(folder_id):
    """Returns the drive link given a folder ID"""
    return f"https://drive.google.com/drive/folders/{folder_id}"


def upload(local_path, pyd_service):
    """Uploads a file and returns the file ID"""
    file = pyd_service.CreateFile({"title": os.path.basename(local_path)})
    file.SetContentFile(local_path)
    file.Upload()
    return file["id"]


def add_parent(file_id, parent_id, pyd_service):
    """Adds a parent folder to the given file ID"""
    request = pyd_service.auth.service.parents().insert(
        fileId=file_id, body={"id": parent_id}
    )
    return request.execute()


def get_default_folder_id():
    """Returns the default fodler ID (to upload files to) as configured in
    DRIVE_JSON_PATH json"""
    with open(DRIVE_JSON_PATH, encoding="utf-8") as file:
        return json.load(file)["root_folder_id"]


def upload_to_folder(local_path, folder_id=None, pyd_service=None):
    """Uploads a file and adds `folder_id` as its parent. Returns the newly
    uploaded file ID, folder_id (as a tuple)"""
    pyd_service = pyd_service or get_pydrive2_service()
    folder_id = folder_id or get_default_folder_id()
    file_id = upload(local_path, pyd_service)
    assert add_parent(file_id, folder_id, pyd_service)
    return file_id, folder_id


def test():
    """Uploads the given file (1st arg in cmd) to the root folder and prints
    the file id"""
    filepath = sys.argv[1]
    file_id, folder_id = upload_to_folder(filepath)
    print(f"Uploaded {file_id} to {folder_id}")


if __name__ == "__main__":
    test()
