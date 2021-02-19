
from flask import current_app
# from google.cloud import storage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
from ..models import Notes
from . import getcredspath
import os.path
import threading
import math

import mimetypes
import functools


SCOPES = ['https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive', ]
# SERVICE_ACCOUNT_FILE = 'secrets.json'
SERVICE_ACCOUNT_FILE = getcredspath()
FOLDER_ID='1E8IWN4ROK2bICbOvwsc8GZw2bgj96wBy'


class Gdrive:
    MIMETYPES = {}
    def __init__(self, testing=False, *args, **kwargs):
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.drive = build('drive', 'v3', credentials=creds)
        self.main_folder_id = FOLDER_ID
        self.files = []
        self.duplicateslist = []
        self.testing = testing
        # print('drive:',self.drive)

    def get_num_files(self):
        total = 0
        for arr in self.files:
            total += len(arr)
        return total

    def find_duplicates(self):
        if len(self.files) == 0:
            self.get_files()
        merged_arr = functools.reduce(lambda x, y: x+y, self.files)
        sizeset = {}
        for file in merged_arr:
            id = file.get('id')
            name = file.get('name')
            in_db = Notes.query.filter_by(gid=id).first()
            if not in_db:
                self.duplicateslist.append(file)
        return self.duplicateslist

    def batch_duplicates(self, batch_size=20):
        main_batch = self.duplicateslist
        no_of_batches = math.ceil(len(main_batch)/batch_size)
        batch = [[] for f in range(no_of_batches)]
        for i,file in enumerate(main_batch):
            batch_no = i//batch_size
            batch[batch_no].append(file)
        return batch

    def create_and_start_tasks(self, main_batch):
        threads = []
        for batch in main_batch:
            threads.append(threading.Thread(
                target=self.delete_batch, args=[batch]))
        for thread in threads:
            try:
                thread.start()
            except Exception as e:
                raise e
        for th in threads:
            th.join()

    def delete_batch(self, batch):
        for file in batch:
            file_id = file.get('id')
            name=file.get('name')
            if self.testing:
                print(f'simulated deletion of {name}')
            else:
                try:
                    self.drive.files().delete(fileId=file_id).execute()
                except Exception as error:
                    raise error

    # def delete_duplicates(self):
    #     main_batch = self.batch_duplicates()
    #     try:
    #         self.create_and_start_tasks(main_batch)
    #     except Exception as e:
    #         return e
    #     return False
    def delete_duplicates(self):
        try:
            self.delete_batch(self.duplicateslist)
        except Exception as error:
            return error
        return False
        
    def get_metadata(self,file_id):
        result = self.drive.files().get(fileId=file_id,
        fields="name, size, webContentLink, webViewLink, iconLink, mimeType").execute()
        return result
        

    def get_files(self, num=30):
        pageToken = None
        while True:
            results = self.drive.files().list(q="'" + self.main_folder_id + "' in parents",
                                              fields="files(name, id, size, webContentLink, webViewLink, iconLink, mimeType), nextPageToken", pageToken=pageToken, pageSize=num).execute()
            # print(results)
            pageToken = results.get('nextPageToken', None)
            items = results.get('files', [])
            self.files.append(items)
            # print(items)
            if pageToken is None:
                break
        return items

    @classmethod
    def test_delete_duplicates(cls):
        print('testing delete functions...')
        gdrive = Gdrive(testing=True)
        if gdrive.testing:
            print('testing mode activated\n')
        else:
            print('testing mode not active\n')
            return
        print('getting files from google drive...')
        pageSize = 30
        gdrive.get_files(pageSize)
        print(
            f'found {len(gdrive.files)} total pages of files found, each page contains a maximum of {pageSize} files')
        gdrive.find_duplicates()
        print(f'found {len(gdrive.duplicateslist)} duplicates')
        print('testing deletion...')
        if gdrive.delete_duplicates():
            print('tests failed in deleting method/n')
            return 
        print('All tests passed ok')
    @classmethod
    def test_metadata(cls):
        print('getting metadata')
        results=[]
        gdrive=Gdrive(testing=True)
        ids=[]
        files=Notes.query.all()
        print(f'found {len(files)} files')
        for file in files:
            ids.append(file.gid)
        if len(ids)==0:
            return
        for id in ids:
            results.append(gdrive.get_metadata(id))
        if len(results)>0:
            print('tests passed ok')
            print(f'file metadata recieved\n{results}')
    
    @classmethod
    def runtests(cls):
        print('run tests, choose option\n')
        print('1:test getting file metadata')
        print('2:test deleting duplicates\n')
        x=int(input("choose:"))
        if x==1:
            Gdrive.test_metadata()
        elif x==2:
            Gdrive.test_delete_duplicates()
        else:
            print('invalid choice try again')
            return
            
            
