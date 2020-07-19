import dropbox
import os
import json


print(f"Opening Dropbox client...")
# ---------------------------------------------------------+
client = dropbox.Dropbox(os.environ['DROPBOX-API-TOKEN'])  #
# ---------------------------------------------------------+
print(f"...Dropbox client opened!")


def get_ghseets_credentials():

    metadata, res = client.files_download(path=os.environ['DROPBOX-PATH-CREDS'])
    as_json = json.loads(res.content)
    file_name = 'credentials.json'
    access = 'w'  # For my readability

    with open(file_name, access) as writefile:
        json.dump(as_json, writefile)

    return file_name

