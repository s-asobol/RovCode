import pygame

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
        LeftTrigger = joystick.get_axis(4)
        RightTrigger = joystick.get_axis(5)
        LeftBumper = joystick.get_button(4)
        RightBumper = joystick.get_button(5)

        print("inputs", LeftBumper)
        print("inputs jefoiwejfw", RightBumper)
        #Porcess Triggers 
        # Process the inputs for proportional control