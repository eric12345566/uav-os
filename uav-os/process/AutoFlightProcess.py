import time
import cv2 as cv
from State.OSStateEnum import OSState


def autoFlightProcess(share, stateService):
    time.sleep(3)
    while True and stateService.getCurrentState() == OSState.READY:
        frame = share.get()
        print("frame: ", frame)
        cv.imshow('ctr', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cv.destroyAllWindows()
