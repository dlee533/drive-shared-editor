import argparse

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import logging
import pandas as pd
import enum
import datetime
import os


class Roles(enum.Enum):
    READER = enum.auto()
    COMMENTER = enum.auto()
    EDITOR = enum.auto()


class Request:
    def __init__(self):
        """
        Initialize Request details.
        """
        self.mode = None
        self.input = None
        self.output = None

    def __str__(self):
        return f"mode: {self.mode}\n" \
               f"input: {self.input}\n" \
               f"output: {self.output}"


def setup_request_commandline():
    """
    Uses argparse module to accept arguments provided through command
    line. Provided arguments are parsed and passed into a Request object.
    :return: a Request with provided arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("mode",
                        choices=("list", "edit"))
    parser.add_argument("-input", "--input")
    parser.add_argument("-output", "--output")

    try:
        args = parser.parse_args()

        if args.mode == "edit" and (args.input is None or  not os.path.isfile(args.input)):
            parser.error("edit requires path to csv as input")
        _request = Request()
        _request.mode = args.mode
        _request.input = args.input
        _request.output = args.output

        return _request
    except Exception as e:
        print(f"Error! Could not read arguments.\n{e}")
        quit()


class ShareManager:

    def __init__(self):
        self._drive = None
        self._folder_dict = {}

    def list(self, output_path=None):
        if self._drive is None:
            self._get_drive()

        email = self._drive.GetAbout()['user']['emailAddress']
        items = self._drive.ListFile({'q': f"'{email}' in owners and trashed=false and 'me' in owners"}).GetList()
        items = [item for item in items if self._is_shared_by_me(item)]

        headers = ['id', 'path', 'type', 'reader', 'commenter', 'editor']
        dataset = {header: [] for header in headers}

        for item in items:
            dataset['id'].append(item['id'])
            dataset['path'].append(self._get_path(item))
            dataset['type'].append('folder' if item['mimeType'] == 'application/vnd.google-apps.folder' else 'file')
            permission = self._get_permission(item)
            dataset['reader'].append(permission[0])
            dataset['commenter'].append(permission[1])
            dataset['editor'].append(permission[2])

        df = pd.DataFrame(dataset)
        if output_path is None:
            output_path = f'shared_{datetime.datetime.now().strftime("%m%d%Y_%H%M%S")}.csv'
        df.to_csv(output_path, index=False)

    def edit(self, input_path):
        if self._drive is None:
            self._get_drive()
        # df = pd.read_csv(input_path)
        # email = drive.GetAbout()['user']['emailAddress']
        #
        # df = pd.DataFrame(ShareEditor._read_csv(input_path))
        #
        # id_set = set(df['id'])
        #
        # for _id in id_set:
        #     row = df.loc[df['id'] == _id]
        #     if len(row) > 1:
        #         print(f"skipping {row['name']}: more than one entry exists")
        #         continue
        #     item = drive.CreateFile({'id': _id})
        #     for permission in item.FetchMetadata(fields='permissions'):
        #         pass

    def _is_shared_by_me(self, item):
        if not item['shared']:
            return False
        try:
            self._get_path(item)
        except IndexError:
            logging.log(10, f"{item['title']} is not in My Drive")  # 10 = DEBUG
            return False

        return True

    def _get_path(self, item):
        path = self._folder_dict.get(item['id'], False)

        if path is not False:
            return path
        elif item['parents'][0]['isRoot']:
            path = f'ROOT/{item["title"]}'
            if 'folder' in item['mimeType']:
                self._folder_dict[item['id']] = path
            return path

        parent = self._drive.CreateFile({'id': item['parents'][0]['id']})
        path = f'{self._get_path(parent)}/{item["id"]}'

        if 'folder' in item['mimeType']:
            self._folder_dict[item['id']] = path

        return path

    def _get_drive(self):
        if self._drive is not None:
            return

        token = "token.json"

        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(token)

        if gauth.access_token_expired:
            gauth.LocalWebserverAuth()
            gauth.SaveCredentialsFile(token)

        self._drive = GoogleDrive(gauth)

    def _get_permission(self, item):
        email = self._drive.GetAbout()['user']['emailAddress']

        permission = {
            Roles.READER: [],
            Roles.EDITOR: [],
            Roles.COMMENTER: []
        }
        item.FetchMetadata(fields='permissions')

        for user in item['permissions']:
            if user.get('emailAddress', None) == email:
                continue
            permission[self._get_role(user)].append(user.get('emailAddress', 'anyoneWithLink'))

        return ','.join(permission[Roles.READER]), ','.join(permission[Roles.COMMENTER]), ','.join(permission[Roles.EDITOR])

    @staticmethod
    def _get_role(user):
        if user['role'] == 'writer':
            return Roles.EDITOR
        elif user.get('additionalRoles', False):
            return Roles.COMMENTER
        elif user['role'] == 'reader':
            return Roles.READER
        return ''


def test_list():
    manager = ShareManager()
    manager.list()

    print("finished execution")


def main(_request=None):
    manager = ShareManager()

    if _request.mode == "list":
        manager.list(output_path=_request.output)
    else:
        manager.edit(input_path=_request.input)

    print("finished execution")


if __name__ == "__main__":
    request = setup_request_commandline()
    main(request)

    # test_list()
