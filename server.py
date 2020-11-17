import socket
import threading
from struct import unpack
import io
import time
import PIL.Image as Image

NUM_THREADS = 8
def merge_img():
    global received
    n = 0
    while True:
        if len(received.file_pieces)==NUM_THREADS:
            n += 1
            final_file = b''
            for key in sorted(received.file_pieces.keys()):
                v = received.file_pieces[key]
                print(f"key = {key} data = {len(v)}")
                final_file += v
            print(len(final_file))

            if received.file_type==0:
                image = Image.open(io.BytesIO(final_file))
                image.save(f'received_{n}.jpg')
            else:
                with open(f'received_{n}.mp4', 'wb') as video:
                    video.write(final_file)
            received.file_pieces = {}

class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("New connection added: ", clientAddress)
    def run(self):
        print ("Connection from : ", clientAddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        
        bdata_id = self.csocket.recv(16)
        data_id = int.from_bytes(bdata_id, 'big')

        bfile_type = self.csocket.recv(16)
        file_type = int.from_bytes(bfile_type, 'big')

        chunk_size = self.csocket.recv(16)
        length = int.from_bytes(chunk_size, 'big')
        print(chunk_size)
        print(f"Chunk of size {length} bytes to be recieved")
        
        data = b''
        while len(data) < length:
            # doing it in batches is generally better than trying
            # to do it all in one go, so I believe.
            to_read = length - len(data)
            data += self.csocket.recv(4096 if to_read > 4096 else to_read)

        # send our "done" ack
        print(f"Chunk number {data_id} of size {len(data)} bytes recieved")
        received.file_pieces[data_id] = data
        received.file_type = file_type

        msg = "transmission done"
        self.csocket.send(msg.encode('utf-8'))
            

        print ("Client at ", clientAddress , " disconnected...")

LOCALHOST = "127.0.0.1"
PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
print("Server started")
print("Waiting for client request..")

class Received:
    def __init__(self):
        self.file_pieces = {}
        self.file_type = None
received = Received()
t1 = threading.Thread(target=merge_img, args=[])
t1.start()

while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()
