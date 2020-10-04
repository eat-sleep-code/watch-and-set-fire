from firebase_admin import credentials, initialize_app, storage
from functions import Paths, Echo, Console
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import argparse
import os
import shutil
import sys
import time

version = '2020.10.03'

os.environ['TERM'] = 'xterm-256color'


console = Console()
echo = Echo()
paths = Paths()
fileTime = 0

# === Argument Handling ========================================================

parser = argparse.ArgumentParser()
parser.add_argument('--path', dest='path', help='Set the path that will be watched for changes', required=True, type=str)
parser.add_argument('--recursive', dest='recursive', help='Set whether sub directories will also be watched', type=bool)
parser.add_argument('--includePattern', dest='includePattern', help='Set the pattern of files to watch', type=str)
parser.add_argument('--ignorePattern', dest='ignorePattern', help='Set the pattern of files to be ignored', type=str)
parser.add_argument('--bucket', dest='bucket', help='Set the Firebase storage bucket URI', required=True, type=str)
parser.add_argument('--destination', dest='destination', help='Set the destination within the Firebase storage bucket.', type=str)
args = parser.parse_args()

path = args.path or '.'

recursive = args.recursive or True

includePattern = args.includePattern or '*'

ignorePattern = args.ignorePattern or ''

ignoreDirectories = True

caseSensitive = False

bucket = args.bucket
bucket = bucket.replace('gs://', '')

destination = args.destination or '/'


# === Functions ================================================================

def upload(filePath):
    try:
        global path
        global destination
        fileObject = open(filePath, 'rb')

        filePath = filePath.replace(path, '')    
        if (destination.endswith('/')): 
            destination = (destination + filePath).replace('//', '/')
        else: 
            destination = destination.replace('//', '/')
        if (destination.startswith('/')):
            destination = destination[1:]
        blob = bucket.blob(destination)
        blob.upload_from_file(fileObject)
        blob.make_public()
        console.log("Uploaded to: " + str(blob.public_url))
    except Exception as ex:
        console.error("Unable to upload file: " + destination + '\n ' + str(ex))
        pass

# ------------------------------------------------------------------------------

def onCreated(event):
    console.info(str(event.src_path) + " created")
    upload(filePath=event.src_path)

# ------------------------------------------------------------------------------

def onDeleted(event):
    console.info(str(event.src_path) + " deleted")     

# ------------------------------------------------------------------------------

def onModified(event):
    global fileTime
    newFileTime = os.stat(event.src_path).st_mtime
    if (newFileTime - fileTime) > 0.5:
        console.info(str(event.src_path) + " modified")
        upload(filePath=event.src_path)
    fileTime = newFileTime

# ------------------------------------------------------------------------------

def onMoved(event):
    console.info(str(event.src_path) + " moved")


# === Event Handler ============================================================

eventHandler = PatternMatchingEventHandler(includePattern, ignorePattern, ignoreDirectories, caseSensitive)
eventHandler.on_created = onCreated
eventHandler.on_deleted = onDeleted
eventHandler.on_modified = onModified
eventHandler.on_moved = onMoved

# === Observer =================================================================

try:
    os.makedirs(path, exist_ok = True)
except Exception as ex:
    console.critical("Unable to find watched path: " + path + '\n ' + str(ex))
    echo.on()
    sys.exit()
observer = Observer()
observer.schedule(eventHandler, path, recursive=recursive)
observer.start()

# === Watch and Set Fire =======================================================

try:
    echo.off()
    echo.clear()
    try:
        os.chdir(home) 
    except:
        pass

    
    try:
        firebaseCredentials = credentials.Certificate("firebase-key.json")
        initialize_app(firebaseCredentials, {'storageBucket': bucket})
        bucket = storage.bucket()
    except Exception as ex:
        console.critical('Unable to initialize Firebase connection.   Please check your firebase-kay.json file and the specified destination bucket!')
        echo.on()
        sys.exit()

    console.log('Watching for file changes...')
    while True:
        time.sleep(100)

except KeyboardInterrupt:
    observer.stop()
    observer.join()        
    echo.on()
    sys.exit(1)

except Exception as ex:
	console.error(ex)
	echo.on()

else:
	echo.on()
	sys.exit(0)