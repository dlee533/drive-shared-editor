import argparse

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class Request:
    """
    Represents a Request to get Pokemon-related data from an API.
    """
    def __init__(self):
        """
        Initialize Request details.
        """
        self.mode = None
        self.cred_path = None
        self.output = None

    def __str__(self):
        return f"Mode: {self.mode}\n" \
               f"cred_path: {self.cred_path}\n" \
               f"output: {self.output}"


def setup_request_commandline():
    """
    Uses argparse module to accept arguments provided through command
    line. Provided arguments are parsed and passed into a Request object.
    :return: a Request with provided arguments
    """
    parser = argparse.ArgumentParser()
    # parser.add_argument("mode",
    #                     choices=("list", "", ""))
    parser.add_argument("cred_path")
    parser.add_argument("output")

    try:
        args = parser.parse_args()
        request = Request()
        # request.mode = args.mode
        request.cred_path = args.cred_path
        request.output = args.output
        return request
    except Exception as e:
        print(f"Error! Could not read arguments.\n{e}")
        quit()


folder_dict = {}


def get_parent(drive, child_item):
    parent_id = child_item['parents'][0]['id']
    if parent_id in folder_dict.keys():
        return folder_dict.get(parent_id, None)
    parent = drive.CreateFile({'id': parent_id})
    parent['title']
    folder_dict[parent_id] = parent
    return parent


def get_path(drive, item):
    if item['parents'][0]['isRoot']:
        return "ROOT/" + item['title']
    parent_item = get_parent(drive, item)
    return get_path(drive, parent_item) + "/" + item['title']


def generate_csv(output_path, items):
    with open(output_path, 'w') as f:
        f.write('path,type\n')
        for item in items:
            f.write(f'"{item[0]}","{item[1]}"\n')


def main(request=None):
    cred_path = "token.json" if request is None else request.cred_path
    output_path = "output.csv" if request is None else request.output
    gauth = GoogleAuth()
    try:
        gauth.LoadCredentialsFile(cred_path)
        if gauth.access_token_expired is True:
            raise Exception("token expired")
    except Exception:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile(cred_path)
    drive = GoogleDrive(gauth)
    email = drive.GetAbout()['user']['emailAddress']
    items = drive.ListFile({'q': f"'{email}' in owners and trashed=false"}).GetList()
    items = [item for item in items if item['shared']]
    print("length =", len(items))
    for item in items:
        folder_dict[item['id']] = item
    result = []
    for i in range(len(items)):
        item = items[i]
        print(i+1)
        try:
            result.append((get_path(drive, item), 'folder' if item['mimeType'] == 'application/vnd.google-apps.folder' else 'file'))
        except Exception:
            pass
    print(len(result))
    generate_csv(output_path, result)


if __name__ == "__main__":
    # # command line
    # request = setup_request_commandline()
    # main(request)

    # ide
    main()
