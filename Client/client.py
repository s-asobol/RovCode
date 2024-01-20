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

#takse input value from -1 to 1 and converts it to 0 to 255
def joystickToInt(axis):
    axis += 1.0
    axis *= 128
    if (axis > 255):
        axis = 255 
    return int (axis)

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
        LeftX = joystickToInt(joystick.get_axis(0))
        LeftY = joystickToInt(joystick.get_axis(1))
        RightX = joystickToInt(joystick.get_axis(2))
        RightY = joystickToInt(joystick.get_axis(3))
        LeftTrigger = joystickToInt(joystick.get_axis(4))
        RightTrigger = joystickToInt(joystick.get_axis(5))
        sendString = f"{LeftX},{LeftY},{RightX},{RightY},{LeftTrigger},{RightTrigger}"
    #makes sure the string is not null. Can happen on startup
    if sendString:
        clientSocket.sendall(sendString.encode())
    clientSocket.sendall("poop".encode())
    time.sleep(1)

    for event in pygame.event.get():

        if event.type == pygame.JOYDEVICEADDED:
            print(event)
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joy)


        if event.type == pygame.QUIT:
            run = False




    