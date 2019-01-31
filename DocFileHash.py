import _mysql
import hashlib
import threading
from datetime import datetime
from datetime import timezone
from PyFunc import *

#start_time = time.localtime() # Timer to determine script run time

#Insert database connection stuff here

class FileScan:
    def __init__(self, file_directory, file_name):
        self.file_directory = file_directory
        self.file_name = file_name
        self.file_path = os.path.join(self.file_directory, self.file_name)

    def __repr__(self):
        return "Running"

    def Scan(self):
        print(self.file_path)
        #Pull created, modified dates of file
        file_info = os.stat(self.file_path)
        file_size = file_info[6]
        file_modified = datetime.fromtimestamp(file_info[8])
        md5_hash = hashlib.md5()
        #Open file in binary mode to calculate md5 of entire file 
        file_open = open(self.file_path, 'rb')
        while True:
            file_chunk = file_open.read(1024)
            if len(file_chunk) == 0: break
            md5_hash.update(file_chunk)
        file_open.close()
        self.file_hash = md5_hash.hexdigest()
        return(self.file_hash)

directory = "/home/local_admin/Git/Monitoring"
for root, subdirs, files in os.walk(directory):
    for file_name in files:
        print(FileScan(root, file_name).Scan())

print(python_run_time(time.localtime()))
