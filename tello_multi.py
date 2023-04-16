import keyModule as km
import time
import numpy as np
import cv2
import math
import swarm as s
import threading
import queue

# Tello video url
URL1 = "udp://0.0.0.0:11111"
URL2 = "udp://0.0.0.0:21111"

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

coordinates = [[(x[0], y[0])], [(x[1], y[1])]] # drones' past coordinates in the map
inputs = []
yaws = [[0], [0]]
alist = [[0], [0]]

drone_number = 0 # currently controlled drone, 9=all drones
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]

drones = []
objects = []
follow_object = False

km.init()

# bind drones to different network interfaces
drone1 = s.bindSocket('192.168.10.3', 56815)
drones.append(drone1)
drone2 = s.bindSocket('192.168.10.2', 56815)
drones.append(drone2)

# listen to drone responses in threads
recvThread1 = threading.Thread(target=s.recv, args=('drone-1', drone1), daemon=True)
recvThread1.start()
recvThread2 = threading.Thread(target=s.recv, args=('drone-2', drone2), daemon=True)
recvThread2.start()

# set drones to sdk mode
s.sendCommandAll(drones, "command")

time.sleep(1)

# change drone video stream ports
s.sendCommand(drone1, "port 8890 11111")
s.sendCommand(drone2, "port 8890 21111")

#time.sleep(1)

#s.sendCommand(drone1, "wifi 1 tellote1234")
#s.sendCommand(drone2, "wifi 2 tellote1234")

time.sleep(1)

# check battery percentage
s.sendCommandAll(drones, "battery?")

time.sleep(1)

# turn video stream off and on just in case
s.sendCommandAll(drones, "streamoff")
time.sleep(1)
s.sendCommandAll(drones, "streamon")
time.sleep(1)

# open video streams and display them in threads
print(f"trying to open {URL1}")
stream1 = cv2.VideoCapture(URL1)
stream1.set(cv2.CAP_PROP_BUFFERSIZE, 20)
if stream1.isOpened() == False:
    print(f'[!] error opening {URL1}')

q = queue.Queue(maxsize = 1)
streamThread1 = threading.Thread(target=s.displayStream, args=("stream-1", stream1, q, True), daemon=True)
streamThread1.start()  

print(f"trying to open {URL2}")
stream2 = cv2.VideoCapture(URL2)
stream2.set(cv2.CAP_PROP_BUFFERSIZE, 20)
if stream2.isOpened() == False:
    print(f'[!] error opening {URL2}')

streamThread2 = threading.Thread(target=s.displayStream, args=("stream-2", stream2, q, False), daemon=True)
streamThread2.start()  

def getKeyBoardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 30
    aspeed = 50
    global yaw, x, y, a, drone_number, follow_object
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
        backwards()

    elif km.getkey("f"):
        follow_object = not follow_object

    if km.getkey("q"):
        if(drone_number == 9):
            s.sendCommandAll(drones, "land")
        else:
            s.sendCommand(drones[drone_number], "land")
    if km.getkey("e"):
        if(drone_number == 9):
            s.sendCommandAll(drones, "takeoff")
        else:
            s.sendCommand(drones[drone_number], "takeoff")
    if km.getkey("0"):
        drone_number = 0
    elif km.getkey("1"):
        drone_number = 1
    elif km.getkey("9"):
        drone_number = 9

    time.sleep(interval)

    # calculate coordinates
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

# draw drone and object coordinates on the map
def drawPoints():
    for d in range(2):      
        for i in range(len(coordinates[d])):
            cv2.circle(img, coordinates[d][i], 2, (colors[d][0] * 0.5, colors[d][1] * 0.5, colors[d][2] * 0.5) , cv2.FILLED)
        cv2.circle(img, (x[d], y[d]), 2, colors[d], cv2.FILLED)   
        cv2.putText(img, f'({x[d]}, {y[d]})', (x[d] + 10, y[d] + 30), cv2.FONT_HERSHEY_PLAIN, 1, colors[d], 1)
    if(objects):
        for object in objects:
            cv2.circle(img, object, 6, (100, 100, 100) , cv2.FILLED)
        cv2.putText(img, f'({objects[-1][0]}, {objects[-1][1]})', (objects[-1][0] + 10, objects[-1][1] + 30), cv2.FONT_HERSHEY_PLAIN, 1, (100, 100, 100), 1)
        cv2.circle(img, objects[-1], 6, (150, 100, 100) , cv2.FILLED)

# save 10 last inputs for the backwards function
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

# repeat 10 last inputs in reverse order
def backwards():
    global inputs, yaw, yaws, drone_number
    s.sendCommand(drones[drone_number], "rc 0 0 0 0")
    for input in inputs:
        neginputs = [-c for c in input]
        print(neginputs)
        s.sendCommand(drones[drone_number], f"rc {neginputs[0]} {neginputs[1]} {neginputs[2]} {neginputs[3]}")
        time.sleep(interval)
    yaw[drone_number] = yaws[drone_number][-10]
    alist[drone_number] = alist[drone_number][-10]

# calculate detected object coordinates based on its size
def calculateObjectCoords(detection):
    global x, y, objects

    a = list(range(720))
    height = detection["height"]
    offset = a[-int(height)]
    object = (x[0], y[0] - int(offset * 0.1))
    objects.append(object)

# fly to object coordinates
def goToObject():
    global x, y, objects
    going = False
    #for i in range(len(drones)):
        #if (i != drone_number):
    if(not going):
        going = True
        s.sendCommand(drones[1], f"go {(x[1] - objects[-1][0]) * 2} {(y[1] - objects[-1][1] + 20) * 2} 0 60")
        #s.sendCommand(drones[1], f"go {y[1] - object[1]} 0 0 60")
        #s.sendCommand(drones[1], f"go {object[0] - x[1] + 20} 0 0 {fSpeed}")
        x[1] = objects[-1][0]
        y[1] = objects[-1][1] + 30
        time.sleep(1)
        going = False

try:
    while True:
        vals = getKeyBoardInput()
        saveValues()

        # send inputs to all drones
        if (drone_number == 9):
            s.sendCommandAll(drones, f"rc {vals[0]} {vals[1]} {vals[2]} {vals[3]}")
            for d in range(len(drones)):
                coordinates[d].append((x[d], y[d]))
        # send inputs to one drone
        else:
            for i in range(len(drones)):
                if (i != drone_number):
                    s.sendCommandAll(drones, "rc 0 0 0 0") # to keep other drones' connection alive
                    if (abs(x[drone_number] - x[i]) < 25 and abs(y[drone_number] - y[i]) < 25): # if drone is near other drones
                        x[drone_number] = coordinates[drone_number][-10][0]
                        y[drone_number] = coordinates[drone_number][-10][1]
                        backwards()
                    else:
                        coordinates[drone_number].append((x[drone_number], y[drone_number]))
                        s.sendCommand(drones[drone_number], f"rc {vals[0]} {vals[1]} {vals[2]} {vals[3]}")
        if(objects and follow_object):
            if (abs(x[1] - objects[-1][0]) > 35 or abs(y[1] - objects[-1][1]) > 35): # if drone is not near the detected object
                goToObject()

        img = np.zeros((1000, 1000, 3), np.uint8) # initialize empty map
        
        if(not q.empty()):
            detection = q.get_nowait() # yolo object detection
            calculateObjectCoords(detection)

        drawPoints()

        cv2.imshow("Output", img) # display map
        cv2.waitKey(1)
except KeyboardInterrupt:
    s.sendCommandAll(drones, "reboot")
    time.sleep(1)
    stream1.release()
    stream2.release()
    drone1.shutdown(1)
    drone1.close()
    drone2.shutdown(1)
    drone2.close()
    pass

cv2.destroyAllWindows()