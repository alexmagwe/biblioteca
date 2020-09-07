import pprint
from google.cloud import storage
from apiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import pickle
import requests
from notes01.app import getuploadpath
import os.path

SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'secrets.json'

class FileUploader:
    @staticmethod
    def getcreds():
        creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return creds
        

    def __init__(self,file,name,unit,urls={},*args,**kwargs):
     
        self.file=file
        self.unit=unit
        self.name=name
        self.urls=urls
        self.uploadpath=os.path.join(getuploadpath(),self.name)
        
    
    def driveupload(self,creds):
        drive = build('drive', 'v3', credentials=creds)
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
        
        self.id=id 
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
