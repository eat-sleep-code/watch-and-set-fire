from pathlib import Path
import logging
import os
import subprocess


class Paths:
	def home(self):
		return '/home/pi/'
	def logs(self):
		logsPath = Paths().home() + 'logs/'
		os.makedirs(logsPath, exist_ok = True)
		return logsPath


# === Echo Control =============================================================

class Echo:
	def off(self):
		try:
			subprocess.run(['stty', '-echo'], check=True, stderr=subprocess.STDOUT)
		except:
			pass
	def on(self):
		try:
			subprocess.run(['stty', 'echo'], check=True, stderr=subprocess.STDOUT)
		except:
			pass
	def clear(self):
		try:
			subprocess.call('clear' if os.name == 'posix' else 'cls', stderr=subprocess.STDOUT)
		except:
			pass


# === Printing & Logging ======================================================

logPath = Paths().logs() + 'watchandsetfire.log'
try:
	logFile = open(logPath, 'a')
	logFile.write('\n Watch and Set Fire \n ============================================================================== \n')
	logFile.close()
except:
	pass
logging.basicConfig(filename=logPath, level=logging.WARNING, format='%(asctime)s: %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

class Console:
	def print(self, message, prefix = ' ', suffix = ' '):
		print(str(prefix) + str(message) + str(suffix))
	def log(self, message, prefix = ' ', suffix = ' '):
		print('\033[94m' + str(prefix) + str(message) + str(suffix)+ '\033[0m')
		logging.info(str(message))
	def debug(self, message, prefix = ' ', suffix = ' '):
		print(str(prefix) + 'DEBUG: ' + str(message) + str(suffix))
		logging.debug(str(message))
	def info(self, message, prefix = ' ', suffix = ' '):
		print(str(prefix) + 'INFO: ' + str(message) + str(suffix))
		logging.info(str(message))
	def warn(self, message, prefix = '\n ', suffix = ' '):
		print('\033[93m' + str(prefix) + 'WARNING: ' + str(message) + str(suffix) + '\033[0m')
		logging.warning(str(message))
	def error(self, message, prefix = '\n ', suffix = ' '):
		print('\033[91m' + str(prefix) + 'ERROR: ' + str(message) + str(suffix) + '\033[0m')
		logging.error(str(message))
	def critical(self, message, prefix = '\n ', suffix = '\n '):
		print('\033[91m' + str(prefix) + 'CRITICAL: ' + str(message) + str(suffix) + '\033[0m')
		logging.critical(str(message))