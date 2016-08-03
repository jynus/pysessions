import sys
import json
import urllib3
import random
import threading

NUM_THREADS = 1
REQUESTS_PER_THREAD = 10000

def requests():
    for i in range(REQUESTS_PER_THREAD):
        key = str(random.randint(1, 1000))
        value = hash(key)
        data = { 'key': key, 'value': value }
        r = conn.urlopen('POST', path, headers={'Content-Type': 'application/json'}, body=json.dumps(data))

if len(sys.argv) <= 2 or int(sys.argv[2]) == 0:
    exit('test.py needs at least two arguments (server and port to connect to)')
server = sys.argv[1]
port = int(sys.argv[2])
path = '/api/v1.0/sessions'

thread_list = []
conn = urllib3.connection_from_url('http://' + server + ':' + str(port))

for i in range(NUM_THREADS):
    t = threading.Thread(target=requests)
    t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
    thread_list.append(t)

for thread in thread_list:
    thread.start()

for thread in thread_list:
    thread.join()
    
    
