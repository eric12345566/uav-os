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

    if cv2.waitKey(1)&0XFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()