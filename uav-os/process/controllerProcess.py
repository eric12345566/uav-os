import time
import cv2 as cv


def controllerProcess(text, share):
    time.sleep(3)
    while True:
        frame = share.get()
        cv.imshow('ctr', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cv.destroyAllWindows()
