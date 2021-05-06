import cv2 as cv
from State.OSStateEnum import OSState


def FrameProcess(shareFrame, OSStateService):
    # cap = cv.VideoCapture(0)
    print("frameProcess: Start")
    print("state: ", OSStateService.getCurrentState())

    if OSStateService.getMode() != 'test':
        initCapOneTime = False
        while True:
            if OSStateService.getCurrentState() != OSState.INITIALIZING:

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
    else:
        print("In Testing mode, Not open Frame")


