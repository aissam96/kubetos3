import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
import boto3
import os
import threading
import random

s3 = boto3.resource('s3')

s3_bucket = "aissam96"
s3_key = "experted_logs"
files_dir = "/Users/aissam.erradouane/Desktop/AIRBUS/kubetos3/logs_to_s3/"
src_file = "source.log"

dst_file = str(random.random()*10**9).split(".")[0]+"log"

counter = 0


class GlobalFunctions:

    def every_one_sec():
        threading.Timer(1.0, everyevery_one_sec).start()
        counter += 1
        size = os.stat(local_file).st_size
        if size > 0 :
            if size > 4999999 or counter >= 120:
                global dst_file
                dst_file = str(random.random()*10**9).split(".")[0]+"log"
                send_to_s3(s3_bucket, s3_key + dst_file, files_dir + dst_file)
                counter = 0
 

    def send_to_s3(bucket,s3_file,local_file):
        
        try:
            s3.upload_file(local_file, bucket, s3_file, Callback=remove_file(local_file))
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def remove_file(local_file):
        os.remove(local_file)

# watching the access log every time it is modified
class Watcher:
    DIRECTORY_TO_WATCH = files_dir

    def __init__(self):
        self.observer = PollingObserver()

    def run(self):
        event_handler = File_handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print "Error"

        self.observer.join()

# collecting and saving the access logs
class File_handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'modified':
            r_file=open(files_dir + src_file,"r")
            last_log=r_file.readlines()[-1]
            r_file.close()
            w_file=open(files_dir + dst_file,"a")
            w_file.write(last_log + "\n")
            w_file.close()


    
    
    
# running the script
if __name__ == '__main__':
    GlobalFunctions().every_one_sec()
    w = Watcher()
    w.run()