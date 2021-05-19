import argparse

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pandas as pd


class Request:
    """
    Represents a Request to get Pokemon-related data from an API.
    """
    def __init__(self):
        """
        Initialize Request details.
        """
        self.mode = None
        self.csv_path = None

    def __str__(self):
        return f"mode: {self.mode}\n" \
               f"csv_path: {self.csv_path}"


def setup_request_commandline():
    """
    Uses argparse module to accept arguments provided through command
    line. Provided arguments are parsed and passed into a Request object.
    :return: a Request with provided arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("mode",
                        choices=("list", "edit"))
    parser.add_argument("csv_path")

    try:
        args = parser.parse_args()
        _request = Request()
        _request.mode = args.mode
        _request.csv_path = args.csv_path
        return _request
    except Exception as e:
        print(f"Error! Could not read arguments.\n{e}")
        quit()


# static facade class
class ShareEditor:

    _folder_dict = {}

    @staticmethod
    def _get_parent(drive, child_item):
        parent_id = child_item['parents'][0]['id']
        if parent_id in ShareEditor._folder_dict.keys():
            return ShareEditor._folder_dict.get(parent_id, None)
        parent = drive.CreateFile({'id': parent_id})
        ShareEditor._folder_dict[parent_id] = parent
        return parent

    @staticmethod
    def _get_path(drive, item):
        if item['parents'][0]['isRoot']:
            return "ROOT/" + item['title']
        parent_item = ShareEditor._get_parent(drive, item)
        return ShareEditor._get_path(drive, parent_item) + "/" + item['title']

    @staticmethod
    def _write_csv(output_path, dataset):
        df = pd.DataFrame(dataset)
        df.to_csv(output_path, index=False)

    @staticmethod
    def _read_csv(input_path):
        df = pd.read_csv(input_path)
        return df

    @staticmethod
    def _is_in_my_drive(drive, item):
        try:
            ShareEditor._get_path(drive, item)
        except IndexError:
            return False
        return True

    @staticmethod
    def _get_role(user):
        if user['role'] == 'writer':
            return 'editor'
        elif user.get('additionalRoles', False):
            return 'commenter'
        elif user['role'] == 'reader':
            return 'reader'
        return ''

    @staticmethod
    def _get_permission(items, email):
        permission = {key: ['' for _ in items] for key in ['anyoneWithLink', 'reader', 'commenter', 'editor']}

        for i, item in enumerate(items):
            item.FetchMetadata(fields='permissions')
            for user in item['permissions']:
                permission['anyoneWithLink'][i] = ShareEditor._get_role(user)
                if user['id'] == 'anyoneWithLink':
                    break
                elif user.get('emailAddress', None) == email:
                    continue
                permission[ShareEditor._get_role(user)][i] += ',' + user['emailAddress']

        for key in ['reader', 'commenter', 'editor']:
            for i in range(len(items)):
                permission[key][i] = permission[key][i].strip(',')

        return permission

    @staticmethod
    def _get_shared(drive):
        email = drive.GetAbout()['user']['emailAddress']
        items = drive.ListFile({'q': f"'{email}' in owners and trashed=false and 'me' in owners"}).GetList()
        items = [item for item in items if item['shared']]

        for item in items:
            ShareEditor._folder_dict[item['id']] = item
            item.FetchMetadata(fields='permissions')

        items = [item for item in items if ShareEditor._is_in_my_drive(drive, item)]
        dataset = {
            'id': [item['id'] for item in items],
            'path': [ShareEditor._get_path(drive, item) for item in items],
            'type': ['folder' if item['mimeType'] == 'application/vnd.google-apps.folder' else 'file' for item in items]
        }

        dataset.update(ShareEditor._get_permission(items, email))
        return dataset

    @staticmethod
    def _insert_permission():
        pass

    @staticmethod
    def _remove_permission():
        pass

    @staticmethod
    def list_shared(drive, output_path):
        dataset = ShareEditor._get_shared(drive)
        ShareEditor._write_csv(output_path, dataset)

    @staticmethod
    def edit_shared(drive, input_path):
        df = pd.DataFrame(ShareEditor._read_csv(input_path))

        id_set = set(df['id'])

        for _id in id_set:
            row = df.loc[df['id'] == _id]
            if len(row) > 1:
                print(f"skipping {row['name']}: more than one entry exists")
                continue
            item = drive.CreateFile({'id': _id})
            for permission in item.FetchMetadata(fields='permissions'):
                pass


def main(_request=None):
    token = "token.json"
    gauth = GoogleAuth()
    try:
        gauth.LoadCredentialsFile(token)
    except Exception:  # TODO: change to specific exception
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile(token)
    drive = GoogleDrive(gauth)

    action = {
        "list": ShareEditor.list_shared,
        "edit": ShareEditor.edit_shared
    }

    action[request.mode](drive, _request.csv_path)
    print("finished execution")


if __name__ == "__main__":
    request = setup_request_commandline()
    main(request)
