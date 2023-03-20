import socket
import threading
import time
import cv2

# Tello video url
URL1 = "udp://0.0.0.0:11112"
URL2 = "udp://0.0.0.0:11111"

def stream(thread_name, s):
    while True:
        try:
            ret, frame = s.read()
            if ret == True:
                cv2.imshow(thread_name, frame)
                cv2.waitKey(1)
        except Exception:   
            print (f"{thread_name} exited")        
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

drone1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone1.bind(('192.168.10.3', 0))
drone2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone2.bind(('192.168.10.2', 0))

recvThread1 = threading.Thread(target=recv, args=('drone-1', drone1), daemon=True)
recvThread1.start()
recvThread2 = threading.Thread(target=recv, args=('drone-2', drone2), daemon=True)
recvThread2.start()

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
    drone1.close()
    drone2.close()
    pass

# Destroy all the windows
cv2.destroyAllWindows()