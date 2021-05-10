import cv2 as cv
from State.OSStateEnum import OSState


def FrameProcess(shareFrame, OSStateService):
    # cap = cv.VideoCapture(0)
    print("frameProcess: Start")
    # OSStateService.frameInitReady()
    if OSStateService.getMode() != 'test':
        initCapOneTime = False
        while True:
            # print("ctr: ",OSStateService.getControllerInitState())
            if OSStateService.getControllerInitState():

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
                OSStateService.frameInitReady()
        cap.release()
        cv.destroyAllWindows()
        print("frameProcess: End")
    else:
        print("In Testing mode, Not open Frame")


