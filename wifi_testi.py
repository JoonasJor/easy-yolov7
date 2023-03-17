import socket
import time
import cv2

# Tello video url
URL = "udp://0.0.0.0:11111"

stream = cv2.VideoCapture(URL)
if stream.isOpened() == False:
    print(f'[!] error opening {URL}')

drone1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone1.bind(('192.168.10.2', 0))
drone2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone2.bind(('192.168.10.3', 0))

drone1.sendto('command'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('command'.encode(), 0, ('192.168.10.1', 8889))

drone1.sendto('takeoff'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('takeoff'.encode(), 0, ('192.168.10.1', 8889))

time.sleep(10)
drone1.sendto('command'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('command'.encode(), 0, ('192.168.10.1', 8889))

drone1.sendto('land'.encode(), 0, ('192.168.10.1', 8889))
print(drone1.recvfrom(1024))
drone2.sendto('land'.encode(), 0, ('192.168.10.1', 8889))
print(drone2.recvfrom(1024))