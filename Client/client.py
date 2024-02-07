import pygame
import sys
pygame.init()
import socket 
import time


HOST = "192.168.1.11"
PORT = 5000

BUFFER_SIZE = 1024

clientSocket = socket.socket()
clientSocket.connect((HOST, PORT))

#placeholder for deadzone
def preProcessJoy(axis):
    if (abs(axis) <= .01):
        axis = 0
    axis = axis**3
    axis = abs(axis)
    OldRange = (1 - 0)  
    NewRange = (2)  
    NewValue = (((axis) * NewRange) / OldRange) + (-1)
    return NewValue

# controller inpuut stuff

run = True
pygame.joystick.init()
joysticks = []

# waits until joystick is added
# adds joystic to joystic array when plugged in 
#
    
while run:
    sendString = None
    for joystick in joysticks:
    #read input from controller
        LeftX = preProcessJoy(joystick.get_axis(0))
        LeftY = preProcessJoy(joystick.get_axis(1))
        RightX = preProcessJoy(joystick.get_axis(2))
        RightY = preProcessJoy(joystick.get_axis(3))
        LeftTrigger = preProcessJoy(joystick.get_axis(4))
        RightTrigger = preProcessJoy(joystick.get_axis(5))
        sendString = f"{LeftX},{LeftY},{RightX},{RightY},{LeftTrigger},{RightTrigger}"
    #makes sure the string is not null. Can happen on startup
    if sendString:
        clientSocket.sendall(sendString.encode())
    time.sleep(.1)

    for event in pygame.event.get():

        if event.type == pygame.JOYDEVICEADDED:
            print(event)
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joy)


        if event.type == pygame.QUIT:
            run = False




    