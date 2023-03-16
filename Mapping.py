import keyModule as km
from djitellopy import tello, TelloSwarm
from time import sleep
import numpy as np
import cv2
import math

# PARAMETERS
fSpeed = 117 / 10  # Forward speed in cm/s (15cm/s)
aSpeed = 360 / 10  # Angular speed  degrees/s (50d/s)
interval = 0.25  # Defines often distance is being printed

dInterval = fSpeed * interval
aInterval = aSpeed * interval
x = [500, 550]
y = [500, 500]
a = [0, 0]
yaw = [0, 0]

coordinates = [[(x[0], y[0])], [(x[1], y[1])]]
inputs = []
yaws = [[0], [0]]
alist = [[0], [0]]

drone = 0
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]

km.init()
swarm = TelloSwarm.fromIps([
    "192.168.243.110",
    "192.168.243.165"
])

swarm.connect()

for tello in swarm:
    print(tello.get_battery())

def getKeyBoardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 30
    aspeed = 50
    global yaw, x, y, a, drone
    d = 0
    if km.getkey("LEFT"):
        lr = -speed
        d = dInterval
        if (drone == 9):
            for i in range(len(swarm.tellos)):
                a[i] = -180
        else:
            a[drone] = -180

    elif km.getkey("RIGHT"):
        lr = speed
        d = -dInterval
        if (drone == 9):
            for i in range(len(swarm.tellos)):
                a[i] = 180
        else:
            a[drone] = 180

    if km.getkey("UP"):
        fb = speed
        d = dInterval
        if (drone == 9):
            for i in range(len(swarm.tellos)):
                a[i] = 270
        else:
            a[drone] = 270

    elif km.getkey("DOWN"):
        fb = -speed
        d = -dInterval
        if (drone == 9):
            for i in range(len(swarm.tellos)):
                a[i] = -90
        else:
            a[drone] = -90

    if km.getkey("w"):
        ud = speed

    elif km.getkey("s"):
        ud = -speed

    if km.getkey("a"):
        yv = -aspeed
        if (drone == 9):
            for i in range(len(swarm.tellos)):
                yaw[i] -= aInterval
        else:
            yaw[drone] -= aInterval

    elif km.getkey("d"):
        yv = aspeed
        if (drone == 9):
            for i in range(len(swarm.tellos)):
                yaw[i] += aInterval
        else:
            yaw[drone] += aInterval

    elif km.getkey("b"):
        backWards()

    if km.getkey("q"):
        swarm.land()
    if km.getkey("e"):
        swarm.takeoff()
    if km.getkey("0"):
        drone = 0
    elif km.getkey("1"):
        drone = 1
    elif km.getkey("9"):
        drone = 9

    sleep(interval)

    if (drone == 9):
        for i in range(len(swarm.tellos)):
            a[i] += yaw[i]
            x[i] += int(d * math.cos(math.radians(a[i])))
            y[i] += int(d * math.sin(math.radians(a[i])))
    else:
        a[drone] += yaw[drone]
        x[drone] += int(d * math.cos(math.radians(a[drone])))
        y[drone] += int(d * math.sin(math.radians(a[drone])))
    return [lr, fb, ud, yv]

def drawPoints():
    for d in range(2):      
        for i in range(len(coordinates[d])):
            cv2.circle(img, coordinates[d][i], 2, (colors[d][0] * 0.5, colors[d][1] * 0.5, colors[d][2] * 0.5) , cv2.FILLED)
        cv2.circle(img, (x[d], y[d]), 2, colors[d], cv2.FILLED)   
        cv2.putText(img, f'({x[d]}, {y[d]})', (x[d] + 10, y[d] + 30), cv2.FONT_HERSHEY_PLAIN, 1, colors[d], 1)
        #cv2.putText(img, f'({(x[d] - 500) / 50}, {(y[d] - 500) / 50})m', (x[d] + 10, y[d] + 30), cv2.FONT_HERSHEY_PLAIN, 1, colors[d], 1)

def saveValues():
    global inputs, yaw, yaws, drone
    if vals[0] != 0 or vals[1] != 0 or vals[2] != 0 or vals[3] != 0:
        inputs.append(vals)    
    if len(inputs) == 10:
        inputs.pop(0)
    
    if(drone == 9):
        for i in range(len(swarm.tellos)):
            yaws[i].append(yaw[i])
            alist[i].append(alist[i])
    else:
        yaws[drone].append(yaw[drone])
        alist[drone].append(alist[drone])

def backWards():
    global inputs, yaw, yaws, drone
    swarm.tellos[drone].send_rc_control(0, 0, 0, 0)
    for input in inputs:
        neginputs = [-c for c in input]
        print(neginputs)
        swarm.tellos[drone].send_rc_control(neginputs[0], neginputs[1], neginputs[2], neginputs[3])
        sleep(interval)
    yaw[drone] = yaws[drone][-10]
    alist[drone] = alist[drone][-10]

while True:
    vals = getKeyBoardInput()
    saveValues()

    if (drone == 9):
        swarm.send_rc_control(vals[0], vals[1], vals[2], vals[3])
        for d in range(len(swarm.tellos)):
            coordinates[d].append((x[d], y[d]))
    else:
        for i in range(len(swarm.tellos)):
            if (i != drone):
                swarm.tellos[i].send_rc_control(0, 0, 0, 0)
                if (abs(x[drone] - x[i]) < 25 and abs(y[drone] - y[i]) < 25):
                    x[drone] = coordinates[drone][-10][0]
                    y[drone] = coordinates[drone][-10][1]
                    backWards()
                else:
                    coordinates[drone].append((x[drone], y[drone]))
                    swarm.tellos[drone].send_rc_control(vals[0], vals[1], vals[2], vals[3])

    img = np.zeros((1000, 1000, 3), np.uint8)
    drawPoints()
    cv2.imshow("Output", img)
    cv2.waitKey(1)