
import socket
import time
import os 
from adafruit_servokit import ServoKit

NUM_MOTORS=16 

# PWM ranges for each motor
MIN_IMP  =[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
MAX_IMP  =[6500,6500,6500,6500,6500,6500,6500,6500,6500,6500,6500,6500,6500,6500,6500,6500]

HOST = "192.168.1.11"
PORT = 5000
BUFFER_SIZE = 1024

# The index of each motor that gets a PWM signal
MOTOR_MAPPING   = [0, 2, 4, 6, 8, 10, 12, 14]

# The index of each control bit that gets set high or low
SIGN_MAPPING    = [1, 3, 5, 7, 9, 11, 13, 15]

pca = ServoKit(channels=16)

# Create a socket and listen for connections
listenSocket = socket.socket()
listenSocket.bind((HOST, PORT))
listenSocket.listen()
print(f"server is listening on {HOST}:{PORT}")

# Accept a connection
serverSocket, clientAdress = listenSocket.accept()
print(f"server accepted connection from {clientAdress}")

# Initializes the PWM range for each motor
def init():
    i = 8
    pca.continuous_servo[i].set_pulse_width_range(MIN_IMP[i] , MAX_IMP[i])

init()

print("before loop")
# Main loop
while True:
    print("in loop")
    # Receive a packet of data and decode it to a string
    data = serverSocket.recv(BUFFER_SIZE).decode()
    print("recieved")
    # Split the string
    testArr = data.split(",")

    # Slice the array into sign and value
    signArray = testArr[:8]
    valueArray = testArr[-8:]

    # Commented this out/didn't implement since printing tends to use a lot of CPU
    # Print the received values to the screen
    # os.system("clear")
    # print(data)

    # Cast signArray values to int
    for i in range(len(signArray)):
        signArray[i] = int(signArray[i])

    # Cast valueArray values to float
    for i in range(len(valueArray)):
        valueArray[i] = float(valueArray[i])

    os.system("clear")
    print(valueArray)
    print(signArray)

    # Loop through the array and apply the input to the motor
    for i in range(8):
        # Set the motor's throttle
        pca.continuous_servo[MOTOR_MAPPING[i]].throttle = valueArray[i]

        # Set the motor's direction bit based off the sign
        if(signArray[i] <= 0):
            pca.continuous_servo[SIGN_MAPPING[i]].throttle = 1
        else:
            pca.continuous_servo[SIGN_MAPPING[i]].throttle = -1