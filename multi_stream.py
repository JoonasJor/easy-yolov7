import socket
import threading
import time
import cv2
from algorithm.object_detector import YOLOv7
import json
from utils.detections import draw

# Tello video url
URL1 = "udp://0.0.0.0:11112"
URL2 = "udp://0.0.0.0:11111"

# Yolo settings
WEIGHTS = 'coco.weights'
CLASSES = 'coco.yaml'
DEVICE  = 'cpu'



def stream(thread_name, s):
    # Init yolo
    yolov7 = YOLOv7()
    yolov7.load(WEIGHTS, classes=CLASSES, device=DEVICE) 
    counter = 20
    detections = []
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
                        print(f'\n{thread_name}:\n', json.dumps(detections, indent=4)) 
                frame = draw(frame, detections)
            
                cv2.imshow(thread_name, frame)
                cv2.waitKey(1)
        except Exception as e:   
            print (f"{thread_name} exited: {e}")        
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

drone1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
drone1.bind(('192.168.10.3', 56815))
drone2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
drone2.bind(('192.168.10.2', 56815))

recvThread1 = threading.Thread(target=recv, args=('drone-1', drone1), daemon=True)
recvThread1.start()
recvThread2 = threading.Thread(target=recv, args=('drone-2', drone2), daemon=True)
recvThread2.start()

sendCommand(drone1, "command")
sendCommand(drone2, "command")

time.sleep(1)

sendCommand(drone1, "port 8890 11112")
sendCommand(drone2, "port 8890 11111")

time.sleep(1)

sendCommand(drone1, "streamoff")
sendCommand(drone2, "streamoff")

time.sleep(1)

sendCommand(drone1, "streamon")
sendCommand(drone2, "streamon")

#time.sleep(2)

stream1 = cv2.VideoCapture(URL1)
if stream1.isOpened() == False:
    print(f'[!] error opening {URL1}')
stream2 = cv2.VideoCapture(URL2)
if stream2.isOpened() == False:
    print(f'[!] error opening {URL2}')

streamThread1 = threading.Thread(target=stream, args=('stream1', stream1), daemon=True)
streamThread1.start()  
streamThread2 = threading.Thread(target=stream, args=('stream2', stream2), daemon=True)
streamThread2.start()  

#streamThread1.join()
#streamThread2.join()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    stream1.release()
    stream2.release()
    drone1.shutdown(1)
    drone1.close()
    drone2.shutdown(1)
    drone2.close()
    pass

# Destroy all the windows
cv2.destroyAllWindows()