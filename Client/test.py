import pygame
import sys
import socket 
import time
import numpy as np



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
PROPORTIONAL_MATRIX = np.array(  [[0.866025, 0.866025, 0, 0.866025, 0.866025, 0],
                                    [0, 0, 0.5, 0, 0, 0.5],
                                    [0, 0, 0, 0, 1, 0],
                                    [0, -0.3048, 0, 0, -0.1778, 0],
                                    [-0.29368, 0., 0.293679, 0.293679, 0, -0.29368]])
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

# Take the input from the controller and output throttle and sign for each motor
# LeftY controls forward/backward movement
# LeftX controls yaw
# RightY controls up/down movement
def pufferfishControl(LeftX, LeftY, RightY):
    # Declaring the numpy array that will be used for the thrust vectors applied to the motors
    thrustMatrix = np.array([0,0,0])

    # Using list comprehension, multiply selected rows in the proportional matrix by the controller input and sum the vectors togethor
    thrustMatrix = thrustMatrix + [x * LeftY for x in PROPORTIONAL_MATRIX[0]]       # Forward/backwards
    thrustMatrix = thrustMatrix + [x * RightY for x in PROPORTIONAL_MATRIX[2]]      # Up/down
    thrustMatrix = thrustMatrix + [x * LeftX for x in PROPORTIONAL_MATRIX[5]]       # Yaw

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
        valueArray.append(abs(elem) *2 - 1)

    # Pad the arrays with 0 if there are fewer than 8 motors
    signArray = np.pad(signArray, (0, 8 - len(signArray)), constant_values = 0)
    valueArray = np.pad(valueArray, (0, 8 - len(valueArray)), constant_values = 0)

    # Concatenate the sign and value arrays into a string for transmission
    sendString = ','.join([str(elem) for elem in (signArray.tolist() + valueArray.tolist())])
    return sendString


def competitionControl(LeftX, LeftY, RightX, RightY,Triggers, LeftBumper, RightBumper):
    print("\nM:\n", PROPORTIONAL_MATRIX)

    # Calculate the transpose of M, only needed when DoF != num motors
    MT = np.transpose(PROPORTIONAL_MATRIX)
    print("\nMT:\n", MT)

    # Calculate M5 = MT * M
    M5 = np.matmul(PROPORTIONAL_MATRIX, MT)
    print("\nM5:\n", M5)

    # Define pilot inputs (assuming)
    # pilot_inputs = np.array([LeftY, RightY, LeftX])
    pilot_inputs = np.array([   [LeftY, 0, 0, 0, 0],
                                [0, RightY, 0, 0, 0],
                                [0, 0, LeftY, 0, 0],
                                [0, 0, 0, RightX, 0],
                                [0, 0, 0, 0, Triggers]])

    # Calculate Pilot Equivalent (PE5)
    PE5 = np.matmul(np.sum(np.abs(PROPORTIONAL_MATRIX), axis=1), pilot_inputs)
    print("\nPE5:\n", PE5)

    # Solve for R5 using M5 * R5 = PE5
    R5 = np.linalg.solve(M5, PE5)
    print("\nR5:\n", R5)

    # Map R5 to thrusters (R6 = MT * R5)
    R6 = np.dot(MT, R5)

    # Normalize R6
    thrustMatrix = normalizeMatrix(R6)

    print("Resulting thruster values (unnormalized):", R6)
    print("Resulting thruster values (normalized):", thrustMatrix)

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
        print("sendString ", sendString)

    # Sleep for a bit to not overwhelm Raspberry Pi
    time.sleep(5)