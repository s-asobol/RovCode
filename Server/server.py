import socket
import time
import os 

HOST = "192.168.1.11"
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
    testArr = data.split(",")
    if (len(testArr) >= 6):
        data = f"LeftX: {testArr[0]}, LeftY: {testArr[1]}, RightX: {testArr[2]}, RightY: {testArr[3]}, leftTrigger: {testArr[4]}, RightTrigger: {testArr[5]}"
    os.system("cls")
    print(data)
    
    #for s in testArr:
        
    time.sleep(1)
    
