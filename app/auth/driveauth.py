
from flask import current_app
# from google.cloud import storage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
from ..models import Notes
from . import getcredspath
import os.path,threading,math

import mimetypes,functools


SCOPES=['https://www.googleapis.com/auth/drive.metadata','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive',]
# SERVICE_ACCOUNT_FILE = 'secrets.json'
SERVICE_ACCOUNT_FILE = getcredspath()


class Gdrive:
    MIMETYPES={}
    # @staticmethod
    # def getcreds():
    #     creds = service_account.Credentials.from_service_account_file(
    #     SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    #     return creds

    def __init__(self,*args,**kwargs):
        creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.drive = build('drive', 'v3', credentials=creds)
        self.main_folder_id='1E8IWN4ROK2bICbOvwsc8GZw2bgj96wBy'
        self.files=[]
        self.duplicateslist=[]
        self.failed=[]
        # print('drive:',self.drive)
    def get_num_files(self):
        total=0
        for arr in self.files:
            total+=len(arr)
        return total
    def find_duplicates(self):
        if len(self.files)==0:
            self.get_files()
        merged_arr=functools.reduce(lambda x,y:x+y,self.files)
        sizeset={}
        for file in merged_arr:
            id=file.get('id')
            name=file.get('name')
            in_db=Notes.query.filter_by(gid=id).first()
            if not in_db:
                self.duplicateslist.append(file)
        return self.duplicateslist
    
    def batch_duplicates(self,size=20):
        main_batch=[]
        no_of_batches=math.ceil(len(self.duplicateslist)/size)
        
        for batch in range(no_of_batches):
            batch=[]
            for file in range(size):
                batch.append(file)
            main_batch.append(batch)
        return main_batch
    def create_and_start_tasks(self,main_batch):
        threads=[]
        for batch in main_batch:
            threads.append(threading.Thread(target=self.delete_batch,args=(batch)))
        for thread in threads:
            thread.start()
        for th in threads:
            th.join()
            
    def delete_batch(self,batch):
        for file in batch:
            file_id=file.get('id')            
            try:
                self.drive.files().delete(fileId=file_id).execute()
            except Exception as error:
                self.failed.append(file)
                print ('An error occurred: %s' % error)
        
        
    def test_delete_duplicates(self):
        files=[{'id':'1lwa6LVqOb7l3kYBcHG-0bKejrf9qjDLV'}]
        print('testing delete functionality...')
        print(f'deleting file of id:{files[0]}')
        
        self.delete_batch(files)
        if len(self.failed)>0:
            print(f'failed to delete:{self.failed}')
        return len(self.failed)
        
    def delete_duplicates(self):
        main_batch=self.batch_duplicates()
        self.create_and_start_tasks(main_batch)
        if len(self.failed)>0:
            return self.failed
        return len(self.failed) #returns how many files have failed to delete
    
    def get_files(self,num):
        pageToken=None
        while True:
            results = self.drive.files().list(q = "'" + self.main_folder_id + "' in parents",fields="files(name, id, size), nextPageToken",pageToken=pageToken,pageSize=num).execute()
            # print(results)
            pageToken=results.get('nextPageToken',None)
            items = results.get('files', [])
            self.files.append(items)
            # print(items)
            if pageToken is None:
                break    
        return items

        
        