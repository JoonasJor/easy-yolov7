import socket
import time
import cv2

# Tello video url
URL1 = "udp://0.0.0.0:11110"
URL2 = "udp://0.0.0.0:11111"

drone1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone1.bind(('192.168.10.3', 0))

drone1.sendto('command'.encode(), 0, ('192.168.10.1', 8889))
drone1.sendto('port 9000 11110'.encode(), 0, ('192.168.10.1', 8889))

time.sleep(1)

drone2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
drone2.bind(('192.168.10.2', 0))

drone2.sendto('command'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('port 9000 11111'.encode(), 0, ('192.168.10.1', 8889))

'''
drone1.sendto('command'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('command'.encode(), 0, ('192.168.10.1', 8889))

drone1.sendto('port 8889 11110'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('port 8889 11111'.encode(), 0, ('192.168.10.1', 8889))
'''

time.sleep(1)

drone1.sendto('command'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('command'.encode(), 0, ('192.168.10.1', 8889))

drone1.sendto('streamoff'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('streamoff'.encode(), 0, ('192.168.10.1', 8889))

time.sleep(1)

drone1.sendto('command'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('command'.encode(), 0, ('192.168.10.1', 8889))

drone1.sendto('streamon'.encode(), 0, ('192.168.10.1', 8889))
drone2.sendto('streamon'.encode(), 0, ('192.168.10.1', 8889))

time.sleep(1)

stream1 = cv2.VideoCapture(URL2)
if stream1.isOpened() == False:
    print(f'[!] error opening {URL2}')

while(True):
    
    # Capture the video frame
    # by frame
    ret1, frame1 = stream1.read()
    if ret1 == True:
        cv2.imshow('frame', frame1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
stream1.release()
# Destroy all the windows
cv2.destroyAllWindows()