# shared-google-drive
List/bulk edit the shared status of google drive files/folders using csv

## TODO:
* readme
* bulk editing: unshare files that are shared


##Steps:

1. Install the Google client library
```cmd
  pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

2. Enable the Google Drive API
    1. Go to the [Google API Console](https://console.cloud.google.com/apis/dashboard)
    2. Create/select a project
    3. In the sidebar on the left, expand APIs & auth and select APIs.
    4. In the displayed list of available APIs, click the Drive API link and click Enable API.

3. 

##Reference:
- https://developers.google.com/drive/api/v3/quickstart/python
- https://developers.google.com/drive/api/v3/enable-drive-api
- https://developers.google.com/workspace/guides/create-credentials
- https://youtu.be/tGDn3V-mIOM
- https://youtu.be/9K2P2bWEd90
- https://learndataanalysis.org/google-drive-api-in-python-getting-started-lesson-1/
- https://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.html
- https://github.com/googleworkspace/PyDrive