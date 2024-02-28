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

PROPORTIONAL_MATRIX =  [[1, 1, 0],
                        [0, 0, 0],
                        [0, 0, 1],
                        [0, 0, 0],
                        [0, 0, 0],
                        [1, -1, 0]]

# Pre-process the joystick input to apply a deadzone, as well as determine the direction
def preProcessJoystick(axis):
    # Cube the analog axis value, this should allow for better fine motor control
    axis = axis**3

    # Apply deadzone
    if abs(axis) < DEADZONE:
        axis = 0

    return axis

# Pre-process trigger to apply a deadzone, as well as map from range [-1,1] to range [0,1]
def preProcessTrigger(axis):
    axis = axis + 1
    axis = axis / 2

    # Apply deadzone
    if axis < DEADZONE:
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

# Take the input from the controller and output throttle and sign for each motor
# LeftY controls forward/backward movement
# LeftX controls yaw
# RightY controls up/down movement
def pufferfishControl(LeftX, LeftY, RightY):
    # Declaring the numpy array that will be used for the thrust vectors applied to the motors
    thrustMatrix = np.array(len(PROPORTIONAL_MATRIX[0]))

    # Using list comprehension, multiply selected rows in the proportional matrix by the controller input and sum the vectors togethor
    thrustMatrix = thrustMatrix + [x * LeftX for x in PROPORTIONAL_MATRIX[5]]       # Yaw
    thrustMatrix = thrustMatrix + [x * LeftY for x in PROPORTIONAL_MATRIX[0]]       # Forward/backwards
    thrustMatrix = thrustMatrix + [x * RightY for x in PROPORTIONAL_MATRIX[2]]      # Up/down

    # Normalize the vector
    thrustMatrix = normalizeMatrix(thrustMatrix)

    # Declare the arrays for extracting the sign and value
    signArray = []
    valueArray = []

    # Pull the sign out from the matrix to make the sign array for the motor controller
    for elem in thrustMatrix:
        if elem < 0:
            signArray.append(1)
        else:
            signArray.append(0)

    # Take the absolute value of each element to make the value array for the motor controller
    for elem in thrustMatrix:
        valueArray.append(abs(elem))

    # Pad the arrays with 0 if there are fewer than 8 motors
    signArray = np.pad(signArray, (0, 8 - len(signArray)), constant_values = 0)
    valueArray = np.pad(valueArray, (0, 8 - len(valueArray)), constant_values = 0)

    # Concatenate the sign and value arrays into a string for transmission
    sendString = ','.join([str(elem) for elem in (signArray.tolist() + valueArray.tolist())])
    print(sendString)
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
        LeftY = preProcessJoystick(joystick.get_axis(1))        # Left joystick Y
        RightX = preProcessJoystick(joystick.get_axis(2))       # Right joystick X
        RightY = preProcessJoystick(joystick.get_axis(3))       # Right joystick Y
        LeftTrigger = preProcessTrigger(joystick.get_axis(4))
        RightTrigger = preProcessTrigger(joystick.get_axis(5))

        # Process the inputs for proportional control
        sendString = pufferfishControl(LeftX, LeftY, RightY)
    # Make sure the string is not null, this can happen on startup
    if sendString:
        clientSocket.sendall(sendString.encode())

    # Sleep for a bit to not overwhelm Raspberry Pi
    time.sleep(.1)