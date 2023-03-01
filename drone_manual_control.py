from djitellopy import Tello
from algorithm.object_detector import YOLOv7
from utils.detections import draw
import cv2
import pygame
import numpy as np
import time
import logging
import json

# Yolo settings
WEIGHTS = 'coco.weights'
CLASSES = 'coco.yaml'
DEVICE  = 'gpu'
# Speed of the drone
S = 60
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.
FPS = 120
# Tello video url
URL = "udp://0.0.0.0:11111"

class FrontEnd(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations (yaw)
            - W and S: Up and down.
            - P: Turn mission pad detection on/off
            - 0/1/2: Set mission pad detection direction      
    """

    def __init__(self):
        # Init pygame
        pygame.init()

        # Creat pygame window
        pygame.display.set_caption(URL)
        self.screen = pygame.display.set_mode([960, 720])

        # Init yolo
        self.yolov7 = YOLOv7()
        self.yolov7.load(WEIGHTS, classes=CLASSES, device=DEVICE) 

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_control = False
        self.pad_detection = False
        self.pad_direction = 0

        # create update timer
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

        Tello.LOGGER.setLevel(logging.WARNING)

    def run(self):

        self.tello.connect()
        self.tello.set_speed(self.speed)

        # In case streaming is on. This happens when we quit this program without the escape key.
        self.tello.streamoff()
        self.tello.streamon()

        stream = cv2.VideoCapture(URL)
        if stream.isOpened() == False:
            print(f'[!] error opening {URL}')

        self.screen.fill([0, 0, 0])

        should_stop = False
        while not should_stop:

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            ret, frame = stream.read()
            if ret == True:
                detections, detected_frame = self.detect(frame)
                if len(detections) != 0:
                    print(f'\n{URL}:\n', json.dumps(detections, indent=4))
                
                # text overlays
                text_battery = "Battery: {}%".format(self.tello.get_battery())
                text_pad_detection = f"Pad Detection: {self.pad_detection} {self.pad_direction}"
                cv2.putText(detected_frame, text_battery, (5, 720 - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(detected_frame, text_pad_detection, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                detected_frame = cv2.cvtColor(detected_frame, cv2.COLOR_BGR2RGB)
                detected_frame = np.rot90(detected_frame)
                detected_frame = np.flipud(detected_frame)

                detected_frame = pygame.surfarray.make_surface(detected_frame)
                self.screen.blit(detected_frame, (0, 0))
                pygame.display.update()

            time.sleep(1 / FPS)
            
        # Call it always before finishing. To deallocate resources.
        self.tello.end()
        self.yolov7.unload()

    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP:  # set forward velocity
            self.for_back_velocity = S
        elif key == pygame.K_DOWN:  # set backward velocity
            self.for_back_velocity = -S
        elif key == pygame.K_LEFT:  # set left velocity
            self.left_right_velocity = -S
        elif key == pygame.K_RIGHT:  # set right velocity
            self.left_right_velocity = S
        elif key == pygame.K_w:  # set up velocity
            self.up_down_velocity = S
        elif key == pygame.K_s:  # set down velocity
            self.up_down_velocity = -S
        elif key == pygame.K_a:  # set yaw counter clockwise velocity
            self.yaw_velocity = -S
        elif key == pygame.K_d:  # set yaw clockwise velocity
            self.yaw_velocity = S

    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP or key == pygame.K_DOWN:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_t:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:  # land
            not self.tello.land()
            self.send_rc_control = False
        elif key == pygame.K_p: # turn mission pad detection on/off
            self.pad_detection = not self.pad_detection
            if self.pad_detection:
                self.tello.enable_mission_pads()
                self.tello.set_mission_pad_detection_direction(self.pad_direction)
            else:
                self.tello.disable_mission_pads()
        elif key == pygame.K_0: # mission pad detection direction downward
            self.pad_direction = 0
        elif key == pygame.K_1: # forward
            self.pad_direction = 1
        elif key == pygame.K_2: # both
            self.pad_direction = 2

    def detect(self, frame):
        detections = self.yolov7.detect(frame)
        detected_frame = draw(frame, detections)

        return detections, detected_frame
            
    def update(self):
        """ Update routine. Send velocities to Tello.
        """
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity,
                self.up_down_velocity, self.yaw_velocity)
        if self.pad_detection:
            pad = self.tello.get_mission_pad_id()
            if(pad != -1 & pad != -2):
                print(f"ID: {pad}")

def main():
    frontend = FrontEnd()
    frontend.run()

if __name__ == '__main__':
    main()