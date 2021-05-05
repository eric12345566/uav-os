import cv2 as cv
from State.OSStateEnum import OSState


def frameProcess(shareFrame, stateService):
    # cap = cv.VideoCapture(0)
    print("frameProcess: Start")
    print("state: ", stateService.getCurrentState())

    initCapOneTime = False
    while True:
        if stateService.getCurrentState() != OSState.INITIALIZING:

            if not initCapOneTime:
                address = shareFrame.getAddress()
                cap = cv.VideoCapture(address)
                initCapOneTime = True

            if not cap.isOpened():
                print('VideoCapture not opened')
                exit(-1)

            ret, frame = cap.read()
            shareFrame.setFrame(frame)

            if not ret:
                print('frame empty')
                break

            cv.imshow('frame', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv.destroyAllWindows()
    print("frameProcess: End")
