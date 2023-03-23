import socket
import cv2
from algorithm.object_detector import YOLOv7
from utils.detections import draw
import queue
import threading
import json
import time

# Yolo settings
WEIGHTS = 'coco.weights'
CLASSES = 'coco.yaml'
DEVICE  = 'cpu'

# Tello video url
URL1 = "udp://0.0.0.0:11111"
URL2 = "udp://0.0.0.0:11112"


def stream(stream_name, s):
    q = queue.Queue()

    receiveThread = threading.Thread(target=receiveStream, args=(stream_name, s, q), daemon=True)
    receiveThread.start()  

    #displayThread = threading.Thread(target=displayStream, args=(stream_name, s, q), daemon=True)
    #displayThread.start()

def receiveStream(stream_name, s, q):
    # Init yolo
    yolov7 = YOLOv7()
    yolov7.load(WEIGHTS, classes=CLASSES, device=DEVICE) 
    detections = []
    counter = 20
    
    while True:
        try:
            ret, frame = s.read()
            if ret == True:
                # run detection every 20th frame
                counter += 1
                if(counter >= 20):
                    counter = 0                                    
                    detections = yolov7.detect(frame)
                    if len(detections) != 0:
                        print(f'\n{stream_name}:\n', json.dumps(detections, indent=4)) 
                frame = draw(frame, detections)
                cv2.imshow(stream_name, frame)
                cv2.waitKey(1)
        except Exception as e:   
            print (f"receive tread {stream_name} exited: {e}")        
            break  

def displayStream(stream_name, s, q):
    while True:
        try:           
            if(not q.empty()):
                frame = q.get()
                cv2.imshow(stream_name, frame)
                cv2.waitKey(1)
        except Exception as e:   
            print (f"receive tread {stream_name} exited: {e}")        
            break  

def recv(thread_name, drone):
    while True: 
        try:
            data, address = drone.recvfrom(1518)
            data = data.decode(encoding="utf-8")
            print(f"{thread_name}: {data}")
        except Exception:
            print (f"{thread_name} exited")  
            break

def sendCommand(drone, com):
    print(f"sent command: {com} to {drone.getsockname()}")
    drone.sendto(com.encode(), ('192.168.10.1', 8889))

def sendCommandAll(drones, com):
    for drone in drones:
        print(f"sent command: {com} to {drone.getsockname()}")
        drone.sendto(com.encode(), ('192.168.10.1', 8889))

def bindSocket(interface_ip, port):
    drone = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    drone.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    drone.bind((interface_ip, port))
    return drone

drones =[]
drone1 = bindSocket('192.168.10.3', 56815)
drones.append(drone1)
drone2 = bindSocket('192.168.10.2', 56814)
drones.append(drone2)

recvThread1 = threading.Thread(target=recv, args=('drone-1', drone1), daemon=True)
recvThread1.start()
recvThread2 = threading.Thread(target=recv, args=('drone-2', drone2), daemon=True)
recvThread2.start()

sendCommandAll(drones, "command")

time.sleep(1)

sendCommand(drone1, "port 8890 11112")
sendCommand(drone2, "port 8890 11111")

#time.sleep(1)

#s.sendCommand(drone1, "wifi 1 tellote1234")
#s.sendCommand(drone2, "wifi 2 tellote1234")

time.sleep(1)

sendCommandAll(drones, "battery?")

time.sleep(1)

sendCommand(drone1, "streamoff")
sendCommand(drone2, "streamoff")

time.sleep(1)

sendCommand(drone1, "streamon")
sendCommand(drone2, "streamon")

print(f"trying to open {URL1}")
stream1 = cv2.VideoCapture(URL1)
if stream1.isOpened() == False:
    print(f'[!] error opening {URL1}')

stream("stream-1", stream1)


print(f"trying to open {URL2}")
stream2 = cv2.VideoCapture(URL2)
if stream2.isOpened() == False:
    print(f'[!] error opening {URL2}')

stream("stream-2", stream2)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass