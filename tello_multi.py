import keyModule as km
from djitellopy import tello, TelloSwarm
from time import sleep
import numpy as np
import cv2
import math
import multi_stream

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

multi = multi_stream

drones = []
drone1 = multi.bindSocket('192.168.10.3', 56815)
drones.append(drone1)
drone2 = multi.bindSocket('192.168.10.2', 56815)
drones.append(drone2)

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

while True:
    vals = getKeyBoardInput()
    saveValues()
    multi.sendCommand(drones[drone], f"rc {neginputs[0]} {neginputs[1]} {neginputs[2]} {neginputs[3]}")

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