import socket
import time
import os 
from adafruit_servokit import ServoKit

#Constants
nbPCAServo=16 
#Parameters
MIN_IMP  =[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
MAX_IMP  =[0,0,0,0,0,0,0,0,6500,6500,0,0,0,0,0,0]
MIN_ANG  =[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MAX_ANG  =[180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180]
#Objects
pca = ServoKit(channels=16)
# function init 
def init():
    i = 8
    print("survo inittialized!")
    pca.continuous_servo[i].set_pulse_width_range(MIN_IMP[i] , MAX_IMP[i])

HOST = "192.168.1.11"
PORT = 5000

BUFFER_SIZE = 1024

listenSocket = socket.socket()
listenSocket.bind((HOST, PORT))

listenSocket.listen()
print(f"server is listening on port {HOST}:{PORT}")

serverSocket, clientAdress = listenSocket.accept()

print(f"server accepted connection from {clientAdress}")



def pcaScenario():
    """Scenario to test servo"""
    for i in range(nbPCAServo):
        for j in range(MIN_ANG[i],MAX_ANG[i],1):
            print("Send angle {} to Servo {}".format(j,i))
            pca.continuous_servo[i].angle = j
            time.sleep(0.01)
        for j in range(MAX_ANG[i],MIN_ANG[i],-1):
            print("Send angle {} to Servo {}".format(j,i))
            pca.continuous_servo[i].angle = j
            time.sleep(0.01)
        pca.servo[i].angle=None #disable channel
        time.sleep(0.5)

def preProcessJoy(axis):
    sign = 0
    if axis < 0:
        sign = 1

    print("axs = " + str(axis))
    axis = axis**3
    axis = abs(axis)
    print("axs = " + str(axis))
    OldRange = (1 - 0)  
    NewRange = (2)  
    NewValue = (((axis) * NewRange) / OldRange) + (-1)
    return sign, NewValue

#setup
init()


while True:
    data = serverSocket.recv(BUFFER_SIZE).decode()
    testArr = data.split(",")
    if (len(testArr) >= 6):
        data = f"LeftX: {testArr[0]}, LeftY: {testArr[1]}, RightX: {testArr[2]}, RightY: {testArr[3]}, leftTrigger: {testArr[4]}, RightTrigger: {testArr[5]}"
    os.system("clear")
    #cast array vals to float
    for i in range(len(testArr)):
        testArr[i] = float(testArr[i])
        
    print(type(testArr[0]))
    print(testArr[0])
    print(data)
    #pcaScenario()
    

    # set direction
    
    if(float(testArr[0]) <= 0):
        pca.continuous_servo[9].throttle = 1
        print("Right")
    else:
        pca.continuous_servo[9].throttle = -1
        print("left")
    
    if (testArr[0] < float(0.01)):
        testArr[0] = -1
    
    throttle = preProcessJoy(testArr[0])
    print(throttle)


    pca.continuous_servo[8].throttle = throttle
    