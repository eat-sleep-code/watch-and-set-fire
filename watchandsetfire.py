from firebase_admin import credentials, initialize_app, storage
from datetime import datetime, timedelta
from functions import Paths, Echo, Console
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import argparse
import os
import shutil
import sys
import time


version = '2020.10.05'

os.environ['TERM'] = 'xterm-256color'


console = Console()
echo = Echo()
paths = Paths()
fileTime = 0
errorCount = 0
maxErrorsPerDay = 10

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

def getContentType(filePath):
	fileName, fileExtension = os.path.splitext(filePath)
	switch = {
		'.jpg': 'image/jpeg',
		'.jpeg': 'image/jpeg',
		'.gif': 'image/gif',
		'.png': 'image/png',
		'.tif': 'image/tiff',
		'.tiff': 'image/tiff',
		'.dng': 'image/x-adobe-dng', #image/dng
		'.crw': 'image/x-canon-crw',
		'.cr2': 'image/x-canon-cr2',
		'.cr3': 'image/x-canon-cr3',
		'.mp4': 'video/mp4',
		'.mpeg': 'video/mpeg',
		'.mov': 'video/quicktime',
		'.mp3': 'audio/mpeg',
		'.ogg': 'audio/ogg',
		'.wav': 'audio/wav',
		'.txt': 'text/plain',
		'.html': 'text/html',
		'.json': 'application/json',
		'.csv': 'text/csv',
		'.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		'.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		'.pdf': 'application/pdf'
	}
	contentType = switch.get(fileExtension, 'application/octet-stream')
	return contentType


def upload(filePath):
	try:
		global path
		global destination
		time.sleep(1)
		fileObject = open(filePath, 'rb')

		filePath = filePath.replace(path, '')
		contentType = getContentType(filePath)

		if (destination.endswith('/')):
			finalDestination = (destination + filePath).replace('//', '/')
		else:
			finalDestination = destination.replace('//', '/')

		if (finalDestination.startswith('/')):
			finalDestination = finalDestination[1:]
		
		blob = bucket.blob(finalDestination)
		blob.upload_from_file(fileObject, content_type = contentType)
		blob.make_public()
		console.info('Uploaded to: ' + str(blob.public_url), ' ', '\n')
	except Exception as ex:
		console.error('Unable to upload file: ' + finalDestination + '\n ' + str(ex))
		errorCount = errorCount + 1
		if errorCount >= maxErrorsPerDay:
			tomorrow = datetime.now() + timedelta(1)
			midnight = datetime(year=tomorrow.year, month=tomrrow.month, day=tomorrow.day, hour=0, minute=0, second=0)
			secondsUntilMidnight = (midnight - datetime.now()).seconds
			console.warn('Maximum errors (' + str(maxErrorsPerDay) + ') per day exceeded.   Sleeping until midnight...')
			time.sleep(secondsUntilMidnight)
			errorCount = 0
		pass

# ------------------------------------------------------------------------------

def onCreated(event):
	filePath = event.src_path
	console.info(filePath + ' created')
	upload(filePath)

# ------------------------------------------------------------------------------

def onDeleted(event):
	filePath = event.src_path
	console.info(filePath + ' deleted')

# ------------------------------------------------------------------------------

def onModified(event):
	global fileTime
	filePath = event.src_path
	newFileCreatedTime = os.stat(filePath).st_ctime
	newFileModifiedTime = os.stat(filePath).st_mtime
	if (newFileModifiedTime - newFileCreatedTime) > 0.5:
		if (newFileModifiedTime - fileTime) > 0.5:
			console.info(filePath + ' modified')
			upload(filePath)
	fileTime = newFileModifiedTime

# ------------------------------------------------------------------------------

def onMoved(event):
	filePath = event.src_path
	console.info(filePath + ' moved')


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
	console.critical('Unable to find watched path: ' + path + '\n ' + str(ex))
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
		os.chdir(paths.home())
	except Exception as ex:
		console.warn('Could not change to home directory. ' + str(ex))
		pass

	
	try:
		keyFilePath = 'watchandsetfire/firebase-key.json'
		if os.path.exists(keyFilePath) == False:
			console.critical('Could not locate file: ' + keyFilePath)
			echo.on()
			sys.exit()
		else:
			firebaseCredentials = credentials.Certificate(keyFilePath)
			initialize_app(firebaseCredentials, {'storageBucket': bucket})
			bucket = storage.bucket()
	except Exception as ex:
		console.critical('Unable to initialize Firebase connection.   Please check your ' + keyFilePath + ' file and the specified destination bucket!')
		echo.on()
		sys.exit()


	console.log('Watching for file changes...', '\n ', '\n ')
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