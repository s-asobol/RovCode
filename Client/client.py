import pygame
import sys
import socket 
import time
import numpy as np

# IP Address and port on Raspberry Pi
HOST = "192.168.1.11"
PORT = 5000

DEADZONE = 0.01

# Column 1: Motor 1 - facing back on the right
# Column 2: Motor 2 - facing back on the left
# Column 3: Motor 3 - facing down in the center

# Row 1: X vector (forwards and back)
# Row 2: Y vector (left and right)
# Row 3: Z vector (up and down)  

# Row 4: X rotation (roll)
# Row 5: Y rotation (pitch)
# Row 6: Z rotation (yaw)

import numpy as np

PROPORTIONAL_MATRIX = np.array(  [[0.866025, 0, 0.866025, 0.866025, 0, 0.866025],
                                    [0.5, 0, -0.5, 0.5, 0, -0.5],
                                    [0, 0, 0, 0, 1, 0],
                                    [0, -0.3048, 0, 0, -0.1778, 0],
                                    [-0.29368, 0., 0.293679, 0.293679, 0, -0.29368]])
'''
PROPORTIONAL_MATRIX = np.array(  [[1, 0, 0, 0, 0, 0],
                                    [1, 0, 0, 0, 1, 1],
                                    [1, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0]])
'''
# Pre-process the joystick input to apply a deadzone, as well as determine the direction
def preProcessJoystick(axis):
    # Cube the analog axis value, this should allow for better fine motor control
    axis = axis**3

    # Apply deadzone
    if abs(axis) < DEADZONE:
        axis = 0

    return axis

# Pre-process both triggers to affect one axis. LeftTrigger: negative, RightTrigger: Positive
def preProcessTriggers(LeftTrigger, RightTrigger):
    LeftTrigger = LeftTrigger + 1
    LeftTrigger = LeftTrigger / 2

    RightTrigger = RightTrigger + 1
    RightTrigger = RightTrigger / 2

    axis = RightTrigger - LeftTrigger

    # Apply deadzone
    if abs(axis) < DEADZONE:
        axis = 0
    
    return axis                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      

# Returns a matrix normalized so the maximum value in the matrix is 1
def normalizeMatrix(ary):
    max = 1
    
    # Get maximum magnitude in matrix
    for elem in ary:
        if abs(elem) > max:
            max = abs(elem)
    
    # Divide each element by the max value
    return [x / max for x in ary]

def sumOfRows(matrix):
    returnArr = np.array([[0.0,0,0,0,0],
                        [0,0,0,0,0],
                        [0,0,0,0,0],
                        [0,0,0,0,0],
                        [0,0,0,0,0]])

    i = 0
    for elem in matrix:
        sum = 0
        for number in elem:
            sum += abs(number)
        returnArr[i][i] = float(sum)
        i += 1
    return returnArr

def competitionControl(LeftX, LeftY, RightX, RightY,Triggers, LeftBumper, RightBumper):
    print("\nM:\n", PROPORTIONAL_MATRIX)

    # Calculate the transpose of M, only needed when DoF != num motors
    MT = np.transpose(PROPORTIONAL_MATRIX)
    print("\nMT:\n", MT)

    # Calculate M5 = M * MT
    MS = np.matmul(PROPORTIONAL_MATRIX, MT)
    MS = MS.round(decimals= 5, out= None)
    print("\nM5:\n", MS)

    MSI = np.linalg.inv(MS)
    print("\nMSI:\n", MSI)

    rov_A = sumOfRows(PROPORTIONAL_MATRIX)
    print("\nrov_A:\n", rov_A)

    PI5 = np.array([[LeftY], 
                   [LeftX],
                    [Triggers],
                    [RightY],
                    [RightX]])
    
    print("\nPI5:\n", PI5)

    rov_s = np.matmul(rov_A, PI5)

    
    print("rov_s", rov_s)

    R5 = np.matmul(MSI, rov_s)
    print("\nR5:\n", R5)
    R6 = np.matmul(MT, R5)
    print("\nR6:\n", R6)

    R6 = np.transpose(R6)
    R6= R6.round(decimals= 5, out= None)
    print("\nR6:\n", R6)
    # Normalize R6
    #thrustMatrix = normalizeMatrix(R6)
    thrustMatrix = R6[0]
    print("\nthruster:\n", thrustMatrix)
    thrustMatrix = normalizeMatrix(thrustMatrix)
    print("Resulting thruster values (normalized):", thrustMatrix)

    # Declare the arrays for extracting the sign and value
    signArray = []
    valueArray = []

    # Pull the sign out from the matrix to make the sign array for the motor controller
    for elem in thrustMatrix:
        if elem.any() < 0:
            signArray.append(1)
        else:
            signArray.append(0)

    # Take the absolute value of each element to make the value array for the motor controller
    for elem in thrustMatrix:
        valueArray.append(abs(elem) *2 - 1)


    #add sign and value of the bumpers to the sign and value arrays to control the claw.
    if(RightBumper == 1 and LeftBumper == 0):
        signArray.append(1)
        valueArray.append(2)
    elif(RightBumper == 1 and LeftBumper == 0):
        signArray.append(0)
        valueArray.append(2)
    else:
        valueArray.append(0)

    # Pad the arrays with 0 if there are fewer than 8 motors
    signArray = np.pad(signArray, (0, 8 - len(signArray)), constant_values = 0)
    valueArray = np.pad(valueArray, (0, 8 - len(valueArray)), constant_values = 0)

    # Concatenate the sign and value arrays into a string for transmission
    sendString = ','.join([str(elem) for elem in (signArray.tolist() + valueArray.tolist())])
    return sendString

# Create a socket and connect to the Raspberry Pi
clientSocket = socket.socket()
clientSocket.connect((HOST, PORT))

# Initialize pygame and the joysticks array
pygame.init()
pygame.joystick.init()
joysticks = []

# Main loop
run = True
while run:
    # Initialize the string that will be sent to the Raspberry Pi
    sendString = None

    # Add joysticks
    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            print(event)
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joy)
        if event.type == pygame.QUIT:
            run = False    

    # For each available joystick (controller)
    for joystick in joysticks:
        # Read input from controller
        LeftX = preProcessJoystick(joystick.get_axis(0))        # Left joystick X
        LeftY = -1 * preProcessJoystick(joystick.get_axis(1))        # Left joystick Y
        RightX = preProcessJoystick(joystick.get_axis(2))       # Right joystick X
        RightY = preProcessJoystick(joystick.get_axis(3))       # Right joystick Y
        LeftTrigger = joystick.get_axis(4)
        RightTrigger = joystick.get_axis(5)
        LeftBumper = joystick.get_button(4)
        RightBumper = joystick.get_button(5)

        #Porcess Triggers 
        Triggers = preProcessTriggers(LeftTrigger, RightTrigger)
        # Process the inputs for proportional control
        sendString = competitionControl(LeftX, LeftY, RightX, RightY, Triggers, LeftBumper, RightBumper)

    # Make sure the string is not null, this can happen on startup
    if sendString:
        clientSocket.sendall(sendString.encode())

    # Sleep for a bit to not overwhelm Raspberry Pi
    time.sleep(.1)