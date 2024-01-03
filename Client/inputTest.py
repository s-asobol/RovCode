import pygame
import sys
pygame.init()
screen = pygame.display.set_mode((800, 500))
screen.fill(pygame.Color("blue"))

x = 350 
y = 200
player = pygame.Rect(x,y,100,100)

run = True

font_size = 30
font = pygame.font.SysFont("Futura" , font_size)

def draw_text(text, font, text_col, x, y):
    img =font.render(text, True, text_col)
    screen.blit(img, (x, y))

clock = pygame.time.Clock()
FPS = 60

pygame.joystick.init()
joysticks = []

while run:
    clock.tick(FPS)
    screen.fill(pygame.Color("midnightblue"))

    for joystick in joysticks:
        draw_text(str(joystick.get_name()), font, pygame.Color("white"), 10, 10)

        horiz_move = joystick.get_axis(2)
        vert_move = joystick.get_axis(3)
        if (abs(horiz_move) > 0.05):
            x += horiz_move * 5
        if (abs(vert_move) > 0.05):
            y += vert_move * 5


    player.topleft = (x, y)
    pygame.draw.rect(screen, pygame.Color("green"), player)

    for event in pygame.event.get():

        if event.type == pygame.JOYDEVICEADDED:
            print(event)
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joy)


        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()