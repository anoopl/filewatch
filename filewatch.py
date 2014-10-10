#!/usr/bin/env python
import pyinotify
import datetime
from bottle import route, run, response, debug
import json
import os
import sys


#Handles write log file on new file creation
class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
        	if event.name.startswith("_") and  os.path.isfile(event.pathname):
        		#log.info('Creating: %s' % (event.pathname))
                	log_file=open('/var/log/newfiles.log', 'a')
                	log_file.write('%s New file created: %s \n' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event.pathname))
			log_file.close

#Function to calucalte median of file name length 
def median_of_file_length(filelength_list):
	if not filelength_list:
		return 0
	filelength_list = sorted(filelength_list)
	length = len(filelength_list)
	if not length % 2:
		return (filelength_list[length / 2] + filelength_list[length / 2 - 1]) / 2.0
	return filelength_list[length / 2]

#Bottle.py route to function
@route('/:time_seconds', method='GET')
#Function to read log file and rreturns file names and median of length as json
def log_reader(time_seconds):

        now = datetime.datetime.now()
        time_diff = now - datetime.timedelta(seconds=int(time_seconds))
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fullPaths = []
        fileLengths = []
        with open("/var/log/newfiles.log") as log_file:
                for line in log_file:
                        word = line.split()
                        time_stamp = word[0]+" "+word[1]
                        time_stamp = datetime.datetime.strptime(time_stamp, "%Y-%m-%d %H:%M:%S")
                        if time_stamp > time_diff:
                                fullPaths.append(word[5])
                                fileLengths.append(len(os.path.basename(word[5])))
	response.content_type = 'application/json'
        return json.dumps({"files": fullPaths, "median_length": median_of_file_length(fileLengths)}, sort_keys=True)
def main():
	wm = pyinotify.WatchManager() # Watch Manager
	mask = pyinotify.IN_CREATE # watched events
	notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
	wdd = wm.add_watch('/home', mask, rec=True)
	notifier.start()
        run(host='localhost', port=8888)
	notifier.stop()



if __name__ == '__main__':
	main()

