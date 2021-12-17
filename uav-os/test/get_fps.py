import time

import cv2
from djitellopy import Tello

tello = Tello()
tello.connect()

tello.streamoff()
tello.streamon()

print("Done: ", tello.get_udp_video_address())
cap = cv2.VideoCapture(tello.get_udp_video_address())
print("Done Cap")
if not cap.isOpened():
    print('VideoCapture not opened')
    exit(-1)

while True:
    ret, frame = cap.read()

    if not ret:
        print('frame empty')
        break

    cv2.imshow('image', frame)

    # 获取 OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    # 对于 webcam 不能采用 get(CV_CAP_PROP_FPS) 方法
    # 而是：
    if int(major_ver) < 3:
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
    else:
        fps = cap.get(cv2.CAP_PROP_FPS)
        print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))

        # Number of frames to capture
        num_frames = 120
        print("Capturing {0} frames".format(num_frames))

        # Start time
        start = time.time()
        # Grab a few frames
        for i in range(0, num_frames):
            ret, frame = cap.read()
        # End time
        end = time.time()

        # Time elapsed
        seconds = end - start
        print("Time taken : {0} seconds".format(seconds))

        # 计算FPS，alculate frames per second
        fps = num_frames / seconds
        print("Estimated frames per second : {0}".format(fps))

    if cv2.waitKey(1)&0XFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()