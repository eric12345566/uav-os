import time
import cv2 as cv


def frameProcess(share):
    cap = cv.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        share.set(frame)
        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()
