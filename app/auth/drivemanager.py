
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
import requests
import mimetypes
import functools
import sys


SCOPES = ['https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive', ]
# SERVICE_ACCOUNT_FILE = 'secrets.json'
SERVICE_ACCOUNT_FILE = getcredspath()
FOLDER_ID = '1E8IWN4ROK2bICbOvwsc8GZw2bgj96wBy'


class URLS:
    BASE_URL = 'https://uon-notes-api.herokuapp.com/api'
    AllNotesUrl = BASE_URL+'/notes/all'
    AllUnitsUrl = BASE_URL+'/units/all'
    UnitNotesUrl = BASE_URL+'/unit/notes/all'
    AllCoursesUrl = BASE_URL+'/courses/all'


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
        self.failed=0
        # print('drive:',self.drive)

    def get_num_files(self):
        total = 0
        for arr in self.files:
            total += len(arr)
        return total

    def find_duplicates(self):
        #it generally finds all files not in the db but in google drive
        if len(self.files) == 0:
            self.get_files()
        sizeset = {}
        remotegids=self.getremoteGIDS()#get all file ids in database
        for file in self.total_files:#go through all the files in google drive
            id = file.get('id')
            name = file.get('name')
            in_db = Notes.query.filter_by(gid=id).first()
            if not id in remotegids:#if file not in database ,i dont care about it
                self.duplicateslist.append(file)
        return self.duplicateslist

    def search(self,query):
        results=self.drive.files().list(q=f"fullText contains '{query}'").execute()
        if results:
            return results

    def batch_duplicates(self, batch_size=20):
        main_batch = self.duplicateslist
        no_of_batches = math.ceil(len(main_batch)/batch_size)
        batch = [[] for f in range(no_of_batches)]
        for i, file in enumerate(main_batch):
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

    def delete_batch(self, duplicates):
        batch = self.drive.new_batch_http_request()
        for file in duplicates:
            file_id = file.get('id')
            batch.add(self.drive.files().delete(fileId=file_id),callback=self.handleResponse)
        try:
            batch.execute()
        except Exception as err:
            raise err
        
    def handleResponse(self,request_id,response,exception):
        if exception is not None:
            print('exception:',exception)
            self.failed+=1
            raise Exception
        else:
            return False
        
            # name = file.get('name')
            # if self.testing:
            #     print(f'simulated deletion of {name}')
            # else:
            #     try:
            #         if self.has_permissions(file_id):
            #             self.drive.files().delete(fileId=file_id).execute()
            #         else:
            #             self.failed.append(file)
            #     except Exception as error:
            #         raise error

# def delete_duplicates(self):
    #     main_batch = self.batch_duplicates()
    #     try:
    #         self.create_and_start_tasks(main_batch)
    #     except Exception as e:
    #         raise e
    #     return False
    
    def delete_duplicates(self):
        try:
            self.delete_batch(self.duplicateslist)
        except Exception as error:
            raise error
        return False
    
    def calculate_storage(self):
        if len(self.total_files)==0:
            self.get_files()
        size=round(sum([round(int(file.get('size'))/(1024**2),2) for file in self.total_files if file.get('size')]))
        return size
            
    def get_metadata(self, file_id, options=None):
        if options:  # specific specific metadata to get
            result = self.drive.files().get(
                fileId=file_id, fields=f"{options}").execute()
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
            self.total_files = functools.reduce(lambda x, y: x+y, self.files)
            if pageToken is None:
                break
        return items
    
    def delete_file(self,id):
        try:
            self.drive.files().delete(fileId=id).execute()
            return {'success':'deleted succesfully'}
        except Exception as e:
            return {'error':str(e)}
            
        
    def has_permissions(self,file_id):
        resp = self.drive.permissions().list(fileId=file_id,fields="*").execute()
        permissions=resp.get('permissions')
        if len(permissions)>0:
            return permissions
        else: return False
    
    @classmethod
    def run_delete_duplicates(cls,really_delete=False):
        print('testing delete functions...')
        if really_delete:
            gdrive = Gdrive()
        else:
            gdrive = Gdrive(testing=True)
        if gdrive.testing:
            print('testing mode activated\n')
        else:
            print('testing mode not active, this is legit, there is no going back\n')
        print('getting files from google drive...')
        pageSize = 30
        gdrive.get_files(pageSize)
        print(
            f'found {len(gdrive.files)} total pages of files found, each page contains a maximum of {pageSize} files')
        print(f"storage occupied in google drive:{gdrive.calculate_storage()}mb")
        gdrive.find_duplicates()
        print(f'found {len(gdrive.duplicateslist)} duplicates')
        if len(gdrive.duplicateslist)>0:
            print('deleting...')
        try:
            gdrive.delete_duplicates()
        except Exception as e:
            print(f'tests failed in deleting method \n error:{e}')
            return
        if gdrive.failed>0:
            print(f'failed to delete {self.failed} files due to permission errors')
        print('All tests passed ok')
        
  
    @classmethod
    def test_metadata(cls):
        print('getting metadata')
        results = []
    
        gdrive = Gdrive(testing=True)
        ids = []
        files = Notes.query.all()
        print(f'found {len(files)} files')
        for file in files:
            ids.append(file.gid)
        ids.append('1I8T7BUBi3VPhbcBkC9xt-fBCHNYAuPLWF5tGiq5fdrE')
        if len(ids) == 0:
            return
        for id in ids:
            gdrive.has_permissions(id)
            results.append(gdrive.get_metadata(id))
        if len(results) > 0:
            print('tests passed ok')
            print(f'file metadata recieved\n{results}')

    @classmethod
    def runtests(cls):
        print('run tasks, choose option\n')
        print('1:test getting file metadata')
        print('2:deleting duplicates\n')
        print('3:get drive storage usage')
        x = int(input("choose:"))
        if x == 1:
            Gdrive.test_metadata()
        elif x == 2:
            Gdrive.run_delete_duplicates(True)
        else:
            print('invalid choice try again')
            return


    def getremoteGIDS(self):
        gids=[]
        res=requests.get(URLS.AllNotesUrl).json()
        for item in res.get('notes'):
            gids.append(item.get('gid'))
        return gids
        
