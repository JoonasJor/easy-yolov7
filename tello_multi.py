import keyModule as km
import time
import numpy as np
import cv2
import math
import swarm as stream
import threading

# Tello video url
URL1 = "udp://0.0.0.0:11112"
URL2 = "udp://0.0.0.0:11111"

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

drone_number = 0
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]

drones = []

km.init()

drone1 = stream.bindSocket('192.168.10.3', 56815)
drones.append(drone1)
drone2 = stream.bindSocket('192.168.10.2', 56814)
drones.append(drone2)

recvThread1 = threading.Thread(target=stream.recv, args=('drone-1', drone1), daemon=True)
recvThread1.start()
recvThread2 = threading.Thread(target=stream.recv, args=('drone-2', drone2), daemon=True)
recvThread2.start()

#sendCommand(drone1, "command")
#sendCommand(drone2, "command")
stream.sendCommandAll(drones, "command")

time.sleep(1)

stream.sendCommand(drone1, "port 8890 11112")
stream.sendCommand(drone2, "port 8890 11111")

#time.sleep(1)

#s.sendCommand(drone1, "wifi 1 tellote1234")
#s.sendCommand(drone2, "wifi 2 tellote1234")

time.sleep(1)

stream.sendCommandAll(drones, "battery?")

time.sleep(1)

stream.sendCommand(drone1, "streamoff")
stream.sendCommand(drone2, "streamoff")

time.sleep(1)

stream.sendCommand(drone1, "streamon")
stream.sendCommand(drone2, "streamon")

print(f"trying to open {URL1}")
stream1 = cv2.VideoCapture(URL1)
stream1.set(cv2.CAP_PROP_BUFFERSIZE, 20)
if stream1.isOpened() == False:
    print(f'[!] error opening {URL1}')

streamThread1 = threading.Thread(target=stream.displayStream, args=("stream-1", stream1), daemon=True)
streamThread1.start()  

print(f"trying to open {URL2}")
stream2 = cv2.VideoCapture(URL2)
stream2.set(cv2.CAP_PROP_BUFFERSIZE, 20)
if stream2.isOpened() == False:
    print(f'[!] error opening {URL2}')

streamThread2 = threading.Thread(target=stream.displayStream, args=("stream-2", stream2), daemon=True)
streamThread2.start()  

def getKeyBoardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 30
    aspeed = 50
    global yaw, x, y, a, drone_number
    d = 0
    if km.getkey("LEFT"):
        lr = -speed
        d = dInterval
        if (drone_number == 9):
            for i in range(len(drones)):
                a[i] = -180
        else:
            a[drone_number] = -180

    elif km.getkey("RIGHT"):
        lr = speed
        d = -dInterval
        if (drone_number == 9):
            for i in range(len(drones)):
                a[i] = 180
        else:
            a[drone_number] = 180

    if km.getkey("UP"):
        fb = speed
        d = dInterval
        if (drone_number == 9):
            for i in range(len(drones)):
                a[i] = 270
        else:
            a[drone_number] = 270

    elif km.getkey("DOWN"):
        fb = -speed
        d = -dInterval
        if (drone_number == 9):
            for i in range(len(drones)):
                a[i] = -90
        else:
            a[drone_number] = -90

    if km.getkey("w"):
        ud = speed

    elif km.getkey("s"):
        ud = -speed

    if km.getkey("a"):
        yv = -aspeed
        if (drone_number == 9):
            for i in range(len(drones)):
                yaw[i] -= aInterval
        else:
            yaw[drone_number] -= aInterval

    elif km.getkey("d"):
        yv = aspeed
        if (drone_number == 9):
            for i in range(len(drones)):
                yaw[i] += aInterval
        else:
            yaw[drone_number] += aInterval

    elif km.getkey("b"):
        backWards()

    if km.getkey("q"):
        stream.sendCommandAll(drones, "land")
    if km.getkey("e"):
        stream.sendCommandAll(drones, "takeoff")
    if km.getkey("0"):
        drone_number = 0
    elif km.getkey("1"):
        drone_number = 1
    elif km.getkey("9"):
        drone_number = 9

    time.sleep(interval)

    if (drone_number == 9):
        for i in range(len(drones)):
            a[i] += yaw[i]
            x[i] += int(d * math.cos(math.radians(a[i])))
            y[i] += int(d * math.sin(math.radians(a[i])))
    else:
        a[drone_number] += yaw[drone_number]
        x[drone_number] += int(d * math.cos(math.radians(a[drone_number])))
        y[drone_number] += int(d * math.sin(math.radians(a[drone_number])))
    return [lr, fb, ud, yv]

def drawPoints():
    for d in range(2):      
        for i in range(len(coordinates[d])):
            cv2.circle(img, coordinates[d][i], 2, (colors[d][0] * 0.5, colors[d][1] * 0.5, colors[d][2] * 0.5) , cv2.FILLED)
        cv2.circle(img, (x[d], y[d]), 2, colors[d], cv2.FILLED)   
        cv2.putText(img, f'({x[d]}, {y[d]})', (x[d] + 10, y[d] + 30), cv2.FONT_HERSHEY_PLAIN, 1, colors[d], 1)
        #cv2.putText(img, f'({(x[d] - 500) / 50}, {(y[d] - 500) / 50})m', (x[d] + 10, y[d] + 30), cv2.FONT_HERSHEY_PLAIN, 1, colors[d], 1)

def saveValues():
    global inputs, yaw, yaws, drone_number
    if vals[0] != 0 or vals[1] != 0 or vals[2] != 0 or vals[3] != 0:
        inputs.append(vals)    
    if len(inputs) == 10:
        inputs.pop(0)
    
    if(drone_number == 9):
        for i in range(len(drones)):
            yaws[i].append(yaw[i])
            alist[i].append(alist[i])
    else:
        yaws[drone_number].append(yaw[drone_number])
        alist[drone_number].append(alist[drone_number])

def backWards():
    global inputs, yaw, yaws, drone_number
    stream.sendCommand(drones[drone_number], "rc 0 0 0 0")
    for input in inputs:
        neginputs = [-c for c in input]
        print(neginputs)
        stream.sendCommand(drones[drone_number], f"rc {neginputs[0]} {neginputs[1]} {neginputs[2]} {neginputs[3]}")
        time.sleep(interval)
    yaw[drone_number] = yaws[drone_number][-10]
    alist[drone_number] = alist[drone_number][-10]

try:
    while True:
        vals = getKeyBoardInput()
        saveValues()

        if (drone_number == 9):
            stream.sendCommandAll(drones, f"rc {vals[0]} {vals[1]} {vals[2]} {vals[3]}")
            for d in range(len(drones)):
                coordinates[d].append((x[d], y[d]))
        else:
            for i in range(len(drones)):
                if (i != drone_number):
                    stream.sendCommandAll(drones, "rc 0 0 0 0")
                    if (abs(x[drone_number] - x[i]) < 25 and abs(y[drone_number] - y[i]) < 25):
                        x[drone_number] = coordinates[drone_number][-10][0]
                        y[drone_number] = coordinates[drone_number][-10][1]
                        backWards()
                    else:
                        coordinates[drone_number].append((x[drone_number], y[drone_number]))
                        stream.sendCommand(drones[drone_number], f"rc {vals[0]} {vals[1]} {vals[2]} {vals[3]}")

        img = np.zeros((1000, 1000, 3), np.uint8)
        drawPoints()
        cv2.imshow("Output", img)
        cv2.waitKey(1)
except KeyboardInterrupt:
    stream.sendCommandAll(drones, "reboot")
    stream1.release()
    stream2.release()
    drone1.shutdown(1)
    drone1.close()
    drone2.shutdown(1)
    drone2.close()
    pass

cv2.destroyAllWindows()