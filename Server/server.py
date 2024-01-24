import socket
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5000

BUFFER_SIZE = 1024

listenSocket = socket.socket()
listenSocket.bind((HOST, PORT))

listenSocket.listen()
print(f"server is listening on port {HOST}:{PORT}")

serverSocket, clientAdress = listenSocket.accept()

print(f"server accepted connection from {clientAdress}")

while True:
    data = serverSocket.recv(BUFFER_SIZE).decode()
    print(data)
    testArr = data.split(",")
    #for s in testArr:
        
    time.sleep(1)
    
