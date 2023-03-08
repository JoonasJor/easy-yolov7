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
x, y = [500, 500], [550, 500]
a = [0, 0]
yaw = [0, 0]
coordinates = [x, y]

drone = 0

km.init()

swarm = TelloSwarm.fromIps([
    "192.168.73.110",
    "192.168.73.165"
])
# me = tello.Tello()
swarm.connect()

for tello in swarm:
    print(tello.get_battery())


# print(me.get_battery())


# cv2.imshow("Output", img)
# cv2.waitKey(1)

def getKeyBoardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 30
    aspeed = 50
    global yaw, x, y, x2, y2, a, drone
    d = 0
    if km.getkey("LEFT"):
        lr = -speed
        d = dInterval
        if(drone == 9):
            for i in range(len(a)):
                a[i] = -180
        else:
            a[drone] = -180

    elif km.getkey("RIGHT"):
        lr = speed
        d = -dInterval
        if(drone == 9):
            for i in range(len(a)):
                a[i] = 180
        else:
            a[drone] = 180

    if km.getkey("UP"):
        fb = speed
        d = dInterval
        if(drone == 9):
            for i in range(len(a)):
                a[i] = 270
        else:
            a[drone] = 270
            
    elif km.getkey("DOWN"):
        fb = -speed
        d = -dInterval
        if(drone == 9):
            for i in range(len(a)):
                a[i] = -90
        else:
            a[drone] = -90

    if km.getkey("w"):
        ud = speed

    elif km.getkey("s"):
        ud = -speed

    if km.getkey("a"):
        yv = -aspeed
        if(drone == 9):
            for i in range(len(yaw)):
                yaw[i] -= aInterval
        else:
            yaw[drone] -= aInterval      
        print(yv)
        print(yaw)

    elif km.getkey("d"):
        yv = aspeed
        if(drone == 9):
            for i in range(len(yaw)):
                yaw[i] += aInterval
        else:
            yaw[drone] += aInterval    
        print(yv)
        print(yaw)

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

    if(drone == 9):
        for i in range(len(a)):
            a[i] += yaw
        for i in range(len(x)):
            x[i] += int(d * math.cos(math.radians(a[i])))
        for i in range(len(y)):
            y[i] += int(d * math.cos(math.radians(a[i])))
    else:
        a[drone] += yaw  
        x[drone] += int(d * math.cos(math.radians(a[drone])))
        y[drone] += int(d * math.cos(math.radians(a[drone])))   
    return [lr, fb, ud, yv]


def drawPoints():
    for coords in coordinates:
        cv2.circle(img, coords, 2, (0, 0, 255), cv2.FILLED)
    for coords2 in coordinates2:
        cv2.circle(img, coords2, 2, (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'({(coords[0] - 500) / 100}, {(coords[1] - 500) / 100})m', (coords[0] + 10, coords[1] + 30),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)
    cv2.putText(img, f'({(coords2[0] - 500) / 100}, {(coords[1] - 500) / 100})m', (coords2[0] + 10, coords[1] + 30),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)


while True:
    vals = getKeyBoardInput()

    if (drone == 9):
        swarm.send_rc_control(vals[0], vals[1], vals[2], vals[3])
        for i in range(len(coordinates)):
            coordinates[i].append((x[i], y[i]))
    else:
        swarm.send_rc_control(0, 0, 0, 0)
        if(drone == 0):
            swarm.tellos[0].send_rc_control(vals[0], vals[1], vals[2], vals[3])
            coordinates.append((x, y))
        elif(drone == 1):
            swarm.tellos[1].send_rc_control(vals[0], vals[1], vals[2], vals[3])
            coordinates2.append((x2, y2))           

    img = np.zeros((1000, 1000, 3), np.uint8)
    drawPoints()
    cv2.imshow("Output", img)
    cv2.waitKey(1)
