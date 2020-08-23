from google.cloud import storage
from apiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
from notes01.app import getuploadpath
import os.path

SCOPES = ['https://www.googleapis.com/auth/drive']

class FileUploader:
    @staticmethod
    def getDrive():
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json', SCOPES)
                creds = flow.run_local_server(port=8080)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('drive', 'v3', credentials=creds)
        return service

    def __init__(self,file,name,unit,urls={},*args,**kwargs):
     
        self.file=file
        self.unit=unit
        self.name=name
        self.urls=urls
        self.uploadpath=os.path.join(getuploadpath(),self.name)
    
    def driveupload(self,drive):
        folder_id='1E8IWN4ROK2bICbOvwsc8GZw2bgj96wBy'
        file_metadata = {
            'name': self.name,
            'mimeType': 'application/pdf',
            'unit':self.unit,
            'parents': [folder_id]

        }
        media = MediaFileUpload(f'{self.file}',
                                mimetype='application/pdf',
                                resumable=True
                                )
        id=drive.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
    
        return id
    def delete_file(self):
        file_path=self.uploadpath
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print('deleted succesfully')
            except Exception as e:
                print(sys.exec_info()[0])
        else:
            print('file not found ')
        
    
    def cloud_upload(self,bucket_name):
        name=self.name
        storage_client=storage.Client()
        bucket=storage_client.bucket(bucket_name)
        blob=bucket.blob(name)
        blob.upload_from_file(self.file)
        print(f'{name} uploaded to {name}')