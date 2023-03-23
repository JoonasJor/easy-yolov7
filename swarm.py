import socket
import cv2
from algorithm.object_detector import YOLOv7
from utils.detections import draw
import queue
import threading
import json

# Yolo settings
WEIGHTS = 'coco.weights'
CLASSES = 'coco.yaml'
DEVICE  = 'cpu'

def displayStream(stream_name, stream):
    # Init yolo
    yolov7 = YOLOv7()
    yolov7.load(WEIGHTS, classes=CLASSES, device=DEVICE) 
    detections = []
    counter = 20
    
    while True:
        try:
            ret, frame = stream.read()
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
            print (f"stream thread {stream_name} exited: {e}")        
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