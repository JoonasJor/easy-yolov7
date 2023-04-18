## Tello Edu swarm with multiple stream support and real-time object detection

This was a student group project aimed to evaluate the capabilities of Tello Edu drone swarms. 
We achieved:
- Manually controlling the drones in a swarm
- Displaying streams from all the drones in a swarm with real-time object detection
- A mapping system which allows:
  - the drones to avoid collision with each other. 
  - the detected object to be drawn on the map


### Multiple streams
For multiple streams you will need separate network card/usb wifi dongle with static ip for each drone.

### Object detection
[easy-yolov7](https://github.com/theos-ai/easy-yolov7) is used for object detection. 

Install all easy-yolov7 dependencies:

```
pip install -r requirements.txt
```
Install cython-bbox for Windows:
```
pip install -e git+https://github.com/samson-wang/cython_bbox.git#egg=cython-bbox
```
For better performance set "DEVICE" in **swarm.py** to "gpu" (requires CUDA-Enabled GPU).
### Mapping
The drones' coordinates on the map are calculated from user inputs. 
