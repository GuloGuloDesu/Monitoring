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
        
