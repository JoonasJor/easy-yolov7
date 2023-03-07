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
x, y = 500, 500
a = 0
yaw = 0
coordinates = []

km.init()

swarm = TelloSwarm.fromIps([
    "192.168.73.110",
    "192.168.73.165"
])
#me = tello.Tello()
swarm.connect()


# print(me.get_battery())


#cv2.imshow("Output", img)
#cv2.waitKey(1)

def getKeyBoardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50
    aspeed = 50
    global yaw, x, y, a
    d = 0
    if km.getkey("LEFT"):
        lr = -speed
        d = dInterval
        a = -180
        print(d)
    elif km.getkey("RIGHT"):
        lr = speed
        d = -dInterval
        a = 180
        print(d)

    if km.getkey("UP"):
        fb = speed
        d = dInterval
        a = 270
        print(d)
    elif km.getkey("DOWN"):
        fb = -speed
        d = -dInterval
        a = -90
        print(d)

    if km.getkey("w"):
        ud = speed
    elif km.getkey("s"):
        ud = -speed

    if km.getkey("a"):
        yv = -aspeed
        yaw -= aInterval
        print(yv)
        print(yaw)
    elif km.getkey("d"):
        yv = aspeed
        yaw += aInterval
        print(yv)
        print(yaw)

    if km.getkey("q"):
        swarm.land()
    if km.getkey("e"):
        swarm.takeoff()
    sleep(interval)
    a += yaw
    x += int(d * math.cos(math.radians(a)))
    y += int(d * math.sin(math.radians(a)))
    return [lr, fb, ud, yv]


def drawPoints():
    for coords in coordinates:
        cv2.circle(img, coords, 5, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (coords[0] + 50, coords[1]), 5, (0, 0, 255), cv2.FILLED)
    cv2.putText(img, f'({(coords[0] - 500) / 100}, {(coords[1] - 500) / 100})m', (coords[0] + 10, coords[1] + 30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)    
    cv2.putText(img, f'({(coords[0] - 450) / 100}, {(coords[1] - 500) / 100})m', (coords[0] + 60, coords[1] + 30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1) 

while True:
    vals = getKeyBoardInput()
    swarm.send_rc_control(vals[0], vals[1], vals[2], vals[3])

    coordinates.append((x,y))
    img = np.zeros((1000, 1000, 3), np.uint8)
    drawPoints()
    cv2.imshow("Output", img)
    cv2.waitKey(1)