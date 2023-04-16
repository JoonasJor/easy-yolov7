import socket
import cv2
from algorithm.object_detector import YOLOv7
from utils.detections import draw
import json
import queue

# Yolo settings
WEIGHTS = 'coco.weights'
CLASSES = 'coco.yaml'
DEVICE  = 'cpu'

object_class = "bottle"

def displayStream(stream_name, stream, q, yolo_detection):
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
                if(yolo_detection):
                    counter += 1
                    if(counter >= 20):
                        counter = 0                                    
                        detections = yolov7.detect(frame)
                        if len(detections) != 0:
                            for i, detection in enumerate(detections):
                                if(detection["class"] == object_class):
                                    #print(detection["class"])
                                    q.put(detection)
                                    
                                #print(detection["class"])
                            #print(f'\n{stream_name}:\n', json.dumps(detections, indent=4)) 
                            #print(detections)
                    frame = draw(frame, detections)
                cv2.imshow(stream_name, frame)
                cv2.waitKey(1)
        except Exception:   
            print (f"stream thread {stream_name} exited")        
            break  

# receive responses from drones
def recv(thread_name, drone):
    while True: 
        try:
            data, address = drone.recvfrom(1518)
            data = data.decode(encoding="utf-8")
            print(f"{thread_name}: {data}")
        except Exception:
            print (f"{thread_name} exited")  
            break

# send command to one drone
def sendCommand(drone, com):
    if("rc 0 0 0 0" not in com):
        print(f"sent command: {com} to {drone.getsockname()}")
    drone.sendto(com.encode(), ('192.168.10.1', 8889))

# send command to all drones
def sendCommandAll(drones, com):
    for drone in drones:
        if("rc 0 0 0 0" not in com):
            print(f"sent command: {com} to {drone.getsockname()}")
        drone.sendto(com.encode(), ('192.168.10.1', 8889))

# bind to network interface
def bindSocket(interface_ip, port):
    drone = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    drone.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    drone.bind((interface_ip, port))
    return drone