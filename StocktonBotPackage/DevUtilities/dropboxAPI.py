import dropbox
import os
import json


print(f"Opening Dropbox client...")
# ---------------------------------------------------------+
client = dropbox.Dropbox(os.environ['DROPBOX-API-TOKEN'])  #
# ---------------------------------------------------------+
print(f"...Dropbox client opened!")


# TODO: Add accounts to switch between if rate limit quota is exhausted

def get_ghseets_credentials():

    """
    The API token / credentials file
    is stored in dropbox as JSON file.

    It's stored in dropbox as an extra
    layer of protection, because Python
    doesn't seem to support environment
    variables with JSON- meaning the token
    would be exposed in plaintext without this.

    :return: The file name for credentials.
    """

    metadata, res = client.files_download(path=os.environ['DROPBOX-PATH-CREDS'])  # Get the path of your file, starting with / as the root.
    as_json = json.loads(res.content)
    file_name = 'credentials.json'

    with open(file_name, 'w') as writefile:
        json.dump(as_json, writefile)

    return file_name
