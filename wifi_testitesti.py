from djitellopy import Tello

tello1 = Tello('192.168.10.3')
tello2 = Tello('192.168.10.2')

tello1.connect()
tello2.connect()
print(tello1.get_battery())
print(tello2.get_battery())
tello1.takeoff()
tello2.takeoff()
tello1.land()
tello2.land()