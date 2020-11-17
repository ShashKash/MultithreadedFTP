import socket
import threading
from struct import unpack
import io
import time
import PIL.Image as Image

def merge_img(file_pieces):
    while True:
        time.sleep(5)
        final_file = b''
        keys = list(file_pieces.keys())
        keys.sort()
        for key in keys:
            v = file_pieces[key]
            print(f"key = {key} data = {len(v)}")
            final_file += v
        print(len(final_file))
        image = Image.open(io.BytesIO(final_file))
        image.save('recieved.jpg')
        exit()
        # if len(file_pieces) == NUM_THREADS:
        #     final_file = b''
        #     for k, v in file_pieces.items():
        #         final_file += v
        #     print(len(final_file))
        #     image = Image.open(io.BytesIO(final_file))
        #     image.save('recieved.JPG')
        #     exit()

class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("New connection added: ", clientAddress)
    def run(self):
        print ("Connection from : ", clientAddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            bdata_id = self.csocket.recv(16)
            data_id = int.from_bytes(bdata_id, 'big')
            
            chunk_size = self.csocket.recv(16)
            print(chunk_size)
            length = int.from_bytes(chunk_size, 'big')
            print(f"Chunk of size {length} bytes to be recieved")
            
            data = b''
            while len(data) < length:
                # doing it in batches is generally better than trying
                # to do it all in one go, so I believe.
                to_read = length - len(data)
                data += self.csocket.recv(4096 if to_read > 4096 else to_read)

            # send our "done" ack
            print(f"Chunk number {data_id} of size {len(data)} bytes recieved")
            recieved_file_pieces[data_id] = data
            # print(len(recieved_file_pieces))

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

recieved_file_pieces = {}

t1 = threading.Thread(target=merge_img, args=[recieved_file_pieces])
t1.start()

while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()
