import pygame
import sys
pygame.init()
import socket 

HOST = "localhost"
PORT = 5000

BUFFER_SIZE = 1024

clientSocket = socket.socket()
clientSocket.connect((HOST, PORT))


# controller inpuut stuff
run = True
pygame.joystick.init()
joysticks = []

while run:

    for joystick in joysticks:
        #print(str(joystick.get_name()))

        horiz_move = joystick.get_axis(2)
        vert_move = joystick.get_axis(3)
        if (abs(horiz_move) > 0.05):
            clientSocket.sendall(f"Horiz: {horiz_move}".encode())
        if (abs(vert_move) > 0.05):
            clientSocket.sendall(f"Vert: {vert_move}".encode())
    
    for event in pygame.event.get():

        if event.type == pygame.JOYDEVICEADDED:
            print(event)
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joy)


        if event.type == pygame.QUIT:
            run = False