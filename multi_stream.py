import socket
import threading
import time
import cv2
import keyModule as km
import pygame

# Tello video url
URL1 = "udp://0.0.0.0:11112"
URL2 = "udp://0.0.0.0:11111"

exit = False

#km.init()

def stream(thread_name, s):
    global exit
    while True:
        try:
            ret, frame = s.read()
            if ret == True:
                cv2.imshow(thread_name, frame)
                cv2.waitKey(1)
        except Exception:           
            break  
        if(exit):
            s.release()
            return

def recv():
    global exit
    while True: 
        try:
            data, address = drone1.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
            #print(drone)
        except Exception:
            print ('\nExit . . .\n')
            break
        if(exit):                   
            drone1.shutdown(1)
            drone1.close()
            drone2.shutdown(1)
            drone2.close()

drone1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone1.bind(('192.168.10.3', 0))
drone2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone2.bind(('192.168.10.2', 0))

recvThread = threading.Thread(target=recv)
recvThread.start()

drone1.sendto('command'.encode(), ('192.168.10.1', 8889))
drone2.sendto('command'.encode(), ('192.168.10.1', 8889))

time.sleep(1)

drone1.sendto('port 8890 11112'.encode(), ('192.168.10.1', 8889))
drone2.sendto('port 8890 11111'.encode(), ('192.168.10.1', 8889))

time.sleep(1)

drone1.sendto('streamoff'.encode(), ('192.168.10.1', 8889))
drone2.sendto('streamoff'.encode(), 0, ('192.168.10.1', 8889))

time.sleep(1)

drone1.sendto('streamon'.encode(), ('192.168.10.1', 8889))
drone2.sendto('streamon'.encode(), 0, ('192.168.10.1', 8889))

#time.sleep(2)

stream1 = cv2.VideoCapture(URL1)
if stream1.isOpened() == False:
    print(f'[!] error opening {URL1}')
stream2 = cv2.VideoCapture(URL2)
if stream2.isOpened() == False:
    print(f'[!] error opening {URL2}')

streamThread1 = threading.Thread(target=stream, args=('stream1', stream1))
streamThread1.start()  
streamThread2 = threading.Thread(target=stream, args=('stream2', stream2))
streamThread2.start()  

#streamThread1.join()
#streamThread2.join()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    exit = True
    pass

# Destroy all the windows
cv2.destroyAllWindows()