import cv2 as cv
from State.OSStateEnum import OSState


def frameProcess(shareFrame, stateService):
    # cap = cv.VideoCapture(0)
    print("frameProcess: Start")
    print("state: ", stateService.getCurrentState())

    while True:
        if stateService.getCurrentState() != OSState.INITIALIZING:
            # ret, frame = cap.read()
            # share.set(frame)
            frame = shareFrame.get()
            cv.imshow('frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    # cap.release()
    cv.destroyAllWindows()
    print("frameProcess: End")
