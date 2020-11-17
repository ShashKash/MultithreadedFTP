import socket
import threading
import time
from struct import pack

SERVER = "127.0.0.1"
PORT = 8080

class ServerThread(threading.Thread):
    def __init__(self, data_id, message, file_type):
        threading.Thread.__init__(self)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER, PORT))
        self.message = message
        self.data_id = data_id
        self.file_type = file_type
        print("Created a new client and connected to server")

    def run(self):
        bdata_id = self.data_id.to_bytes(16, 'big')
        self.client.sendall(bdata_id)

        bfile_type = self.file_type.to_bytes(16, 'big')
        self.client.sendall(bfile_type)

        length = len(self.message).to_bytes(16, 'big')
        print(length)
        print(f"Chunk of size {int.from_bytes(length, 'big')} bytes to be sent")
        self.client.sendall(length)

        self.client.sendall(self.message)
        print(f"Chunk sent")

        while True:
            in_data =  self.client.recv(1024)
            print("From Server :" ,in_data.decode())
            if in_data.decode('utf-8')=='transmission done':
                break
        self.client.close()

file_to_send = 'big.jpg'
file_type = 1 if file_to_send.split('.')[1]=='mp4' else 0
with open(file_to_send, "rb") as media:
  f = media.read()

total_data = bytearray(f)
total_file_size = len(total_data)
print(f"Total filesize is {total_file_size}")

NUM_THREADS = 8
THREADS = []

start = time.time()

for thr_id in range(NUM_THREADS):
    if thr_id==NUM_THREADS-1:
        thr_data = total_data[thr_id*int(total_file_size/NUM_THREADS):total_file_size]
    else:
        thr_data = total_data[thr_id*int(total_file_size/NUM_THREADS):(thr_id+1)*int(total_file_size/NUM_THREADS)]
    thread = ServerThread(message=thr_data, data_id=thr_id+1, file_type=file_type)
    THREADS.append(thread)
    thread.start()

for thr_id in THREADS:
    thr_id.join()

end = time.time()

print(f"File transfer done in {end-start} seconds")
