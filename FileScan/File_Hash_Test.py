import os, hashlib, time
from PyFunc import *

# DteStarTime, dteStartHour, dteStartMin, dteSQLStamp are pulled from PyFunc.py

# Define Constants
arrSQLInsert = []
strRunningScript = sys.argv[0]

for root, dirs, files in os.walk('/home/gulogulodesu/Wallpaper/Humanpaper/'): # Drive or Folder to walk
	for name in files:
		strFileCorrectPath = os.path.join(root, name).replace('"', '`').replace("'", "`").replace("\\", "\\\\") # Clean file path name for insertion into database
		if len(strFileCorrectPath) < 255: # Verify that the file path is not longer than field size in table
			try:
				objMD5Hash = hashlib.md5() ## My note: or equally "m = hashlib.md5()"
				objFileOpen = file(os.path.join(root, name), 'rb') # Open file in Binary mode
				while True:
					objChunk = objFileOpen.read(128)
					if len(objChunk) == 0: break # end of file
				    	objMD5Hash.update(objChunk)
				strFileHash = objMD5Hash.hexdigest()
				objFileOpen.close()
				intExtension = int(len(os.path.join(root, name)) - 4)
				os.rename(os.path.join(root, name), os.path.join(root) + strFileHash + os.path.join(root, name)[intExtension:])
				print os.path.join(root) + strFileHash + os.path.join(root, name)[intExtension:]
				del(strFileHash)
				del(strFileCorrectPath)
				del(objChunk)
				del(objMD5Hash)
			except (ValueError, IOError):
				print os.path.join(root, name)
				objFileOpen.close()
				pass

# Call funciton to display script run time
funcPythonRunTime(time.localtime())

# Clear all variables the script has used
locals().clear()
