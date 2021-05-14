from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def main():

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)
    files = drive.ListFile()
    print(files)


if __name__ == "__main__":
    main()
