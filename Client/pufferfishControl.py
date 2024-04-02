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