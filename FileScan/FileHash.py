import os
import hashlib
import time
import gc
import md5
import threading

gc.enable()

start_time = time.localtime() # Timer to determine script run time

#Insert database connection stuff here

class FileScan(theading.Thread):
    def __init__ (self, file_correct_path=None):
        threading.Thread.__init__(self)
        self.file_correct_path = file_correct_path
    def run(self):
            if len(file_correct_path) < 255: #DB Field size is 255
                try:
                    #Pull created, modified dates of file
                    file_info = os.stat(os.path.join(root, name))
                    md5_hash = md5.new()
                    #Open file in binary mode to calculate md5 of entire file 
                    file_open = file(os.path.join(root, name), 'rb')
                    while True:
                        file_chunk = file_open.read(1024)
                        if len(file_chunk) == 0: break
                        md5_hash.update(file_chunk)
                    file_hash = md5_hash.hexdigest()
