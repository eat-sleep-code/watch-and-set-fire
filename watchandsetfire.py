from firebase_admin import credentials, initalize_app, storage
from functions import Echo, Console
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import argparse
import os
import shutil
import time

version = '2020.10.03'

os.environ['TERM'] = 'xterm-256color'
fileTime = 0

# === Argument Handling ========================================================

parser = argparse.ArgumentParser()
parser.add_argument('--path', dest='path', help='Set the path that will be watched for changes', required=True, type=str)
parser.add_argument('--recursive', dest='recursive', help='Set whether sub directories will also be watched', type=bool)
parser.add_argument('--includePattern', dest='includePattern', help='Set the pattern of files to watch', type=str)
parser.add_argument('--ignorePattern', dest='ignorePattern', help='Set the pattern of files to be ignored', type=str)
parser.add_argument('--bucket', dest='bucket', help='Set the firebase bucket URI', required=True, type=str)
args = parser.parse_args()

path = args.path or '.'

recursive = args.recursive or True

includePattern = args.includePattern or '*'

ignorePattern = args.ignorePattern or ''

ignoreDirectories = True

caseSensitive = False

bucket = args.bucket
bucket = bucket.replace('gs://', '')

# === Functions ================================================================

def upload(self, filePath, destinationName = {}):
    try:
        if (destinationName != {}):
            os.makedirs('~/watchandsetfire/temp', exist_ok = True)
            destination = '~/watchandsetfire/temp/' + destinationName
            shutil.copy(filePath, destination)
            filePath = destination
    except Exception as ex:
        console.warn("Unable to create temporary file: " + destination + '\n ' + str(ex))
        pass

    try:
        blob = bucket.blob(filePath)
        blob.upload_from_filename(filePath)
        blob.make_public()
        console.log("Uploaded to: " + str(blob.public_url))
    except Exception as ex:
        console.error("Unable to upload file: " + destination + '\n ' + str(ex))
        pass

    try:
        if (destinationName != {}):
            os.remove(destination)
    except Exception as ex:
        console.warn("Unable to remove temporary file: " + destination + '\n ' + str(ex))
        pass

# ------------------------------------------------------------------------------

def onCreated(event):
    console.debug(str(event.src_path) + " created")
    upload(filePath=event.src_path)

# ------------------------------------------------------------------------------

def onDeleted(event):
    console.debug(str(event.src_path) + " deleted")     

# ------------------------------------------------------------------------------

def onModified(event):
    global fileTime
    newFileTime = os.stat(event.src_path).st_mtime
    if (newFileTime - fileTime) > 0.5:
        console.debug(str(event.src_path) + " modified")
    fileTime = newFileTime

# ------------------------------------------------------------------------------

def onMoved(event):
    console.debug(str(event.src_path) + " moved")


# === Event Handler ============================================================

eventHandler = PatternMatchingEventHandler(includePattern, ignorePattern, ignoreDirectories, caseSensitive)
eventHandler.on_created = onCreated
eventHandler.on_deleted = onDeleted
eventHandler.on_modified = onModified
eventHandler.on_moved = onMoved

# === Observer =================================================================

observer = Observer()
observer.schedule(eventHandler, path, recursive=recursive)
observer.start()

# === Watch and Set Fire =======================================================

try:
    echo.off()
    echo.clear()
    try:
        os.chdir('/home/pi') 
    except:
        pass

    
    try:
        firebaseCredentials = credentials.Certificate("firebase-key.json")
        initalize_app(firebaseCredentials, 'storageBucket': bucket)
        bucket = storage.bucket()
    except Exception as ex:
        console.critical('Unable to initialize Firebase connection.   Please check your firebase-kay.json file and the specified destination bucket!')
        echo.on()
        sys.exit()

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