import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
import boto3
import os
import threading
import random


s3_bucket = "aissam96"
s3_key = "exported_logs/"
src_files_dir = "/root/kubetos3/logs_to_s3/logs/"
dst_files_dir = "/root/kubetos3/logs_to_s3/exports/"
src_file = "source.log"

dst_file = str(random.random()*10**9).split(".")[0]+".log"

counter = 0


class GlobalFunctions:
    global every_one_sec
    def every_one_sec():
        threading.Timer(1.0, every_one_sec).start()
        global counter
        global s3_bucket
        global s3_key
        global dst_files_dir
        counter += 1
        if os.path.exists(dst_files_dir + dst_file):
            size = os.stat(dst_files_dir + dst_file).st_size
            if size > 4999999 or counter >= 10:
                global dst_file
                print(str(counter) + " " + dst_file)
                s3 = boto3.resource('s3')
                try:
                    s3.Object(s3_bucket, s3_key+dst_file).upload_file(dst_files_dir+dst_file)
                    print("Upload Successful") 
                except FileNotFoundError:
                    print("The file was not found")
                except NoCredentialsError:
                    print("Credentials not available")
                dst_file = str(random.random()*10**9).split(".")[0]+".log"
                counter = 0
 
    global send_to_s3
    def send_to_s3(bucket,s3_file,local_file):
        print(bucket+" "+ s3_file+" "+ local_file)
        s3 = boto3.resource('s3')
        try:
            s3.Object(bucket, s3_file).upload_file(local_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False
  #  global remove_file
  #  def remove_file(local_file):
     #   os.remove(local_file)

# watching the access log every time it is modified
class Watcher:
    DIRECTORY_TO_WATCH = src_files_dir

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
        global src_files_dir
        global dst_files_dir
        global src_file
        global dst_file
        if event.is_directory:
            return None

        elif event.event_type == 'modified':
            r_file=open(src_files_dir + src_file,"r")
            last_log=r_file.readlines()[-1]
            r_file.close()
            w_file=open(dst_files_dir + dst_file,"a")
            w_file.write(last_log)
            w_file.close()


    
    
    
# running the script
if __name__ == '__main__':
    every_one_sec()
    w = Watcher()
    w.run()
