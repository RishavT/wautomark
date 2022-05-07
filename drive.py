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


def main():
    """Uploads the given file (1st arg in cmd) to the root folder and prints
    the file id"""
    filepath = sys.argv[1]
    with open(DRIVE_JSON_PATH, encoding="utf-8") as file:
        folder_id = json.load(file)["root_folder_id"]
    pyd_service = get_pydrive2_service()
    file_id = upload(filepath, pyd_service)
    assert add_parent(file_id, folder_id, pyd_service)
    print(f"Upload {file_id} to {folder_id}")


if __name__ == "__main__":
    main()
