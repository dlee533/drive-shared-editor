# drive-shared-editor
List/bulk edit the shared status of google drive files/folders using csv

## Steps:

1. Enable the [Google Drive API](https://developers.google.com/drive/api/v3/enable-drive-api)

2. [Authenticate](https://developers.google.com/drive/api/v3/about-auth) your users and place the token in the src directory

3. Install PyDrive and Pandas using pip command

4. Run the program (src/shared.py) using command line interface

```cmd
: to list the shared files in My Drive
cd path/to/src
python shared.py list 
python shared.py list output.csv

: to edit the shared files in My Drive
: first edit the csv from list above, change only the reader, commenter, and editor columns
python shared.py edit to_be_edited.csv
```

## Note
- [Google Drive's sharing propagation](https://developers.google.com/drive/api/v3/manage-sharing)

## Reference:
- https://developers.google.com/drive/api/v3/quickstart/python
- https://developers.google.com/drive/api/v3/enable-drive-api
- https://developers.google.com/workspace/guides/create-credentials
- https://youtu.be/tGDn3V-mIOM
- https://youtu.be/9K2P2bWEd90
- https://learndataanalysis.org/google-drive-api-in-python-getting-started-lesson-1/
- https://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.html
- https://github.com/googleworkspace/PyDrive
- https://developers.google.com/drive/api/v3/manage-sharing
