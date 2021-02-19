
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


class Gdrive:
    MIMETYPES = {}
    # @staticmethod
    # def getcreds():
    #     creds = service_account.Credentials.from_service_account_file(
    #     SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    #     return creds

    def __init__(self, testing=False, *args, **kwargs):
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.drive = build('drive', 'v3', credentials=creds)
        self.main_folder_id = '1E8IWN4ROK2bICbOvwsc8GZw2bgj96wBy'
        self.files = []
        self.duplicateslist = []
        self.failed = []
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
                    self.failed.append(file)
                    raise error

    def delete_duplicates(self):
        main_batch = self.batch_duplicates()
        try:
            self.create_and_start_tasks(main_batch)
        except Exception as e:
            return e
        return False # returns how many files have failed to delete

    def get_files(self, num=30):
        pageToken = None
        while True:
            results = self.drive.files().list(q="'" + self.main_folder_id + "' in parents",
                                              fields="files(name, id, size), nextPageToken", pageToken=pageToken, pageSize=num).execute()
            # print(results)
            pageToken = results.get('nextPageToken', None)
            items = results.get('files', [])
            self.files.append(items)
            # print(items)
            if pageToken is None:
                break
        return items

    @classmethod
    def test(cls):
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
        print(
            f'found {len(gdrive.duplicateslist)} duplicates\n batching duplicates...')
        batches = gdrive.batch_duplicates()
        print(f'batching done,{len(batches)} batches made')
        for i,batch in enumerate(batches):
            print(f'{len(batch)} files in batch {i}')
        print('testing deletion...')
        try:
            gdrive.create_and_start_tasks(batches)
        except Exception as e:
            print('tests failed/n',e)
            return
        print('All tests passed ok')
