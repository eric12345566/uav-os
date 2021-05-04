from State.OSStateEnum import OSState
from djitellopy import Tello


def controllerProcess(telloFrameShared, stateService):
    """ init Tello object
    """
    tello = Tello()
    tello.connect()

    """ stream
    """
    tello.streamoff()
    tello.streamon()

    telloFrameObj = tello.get_frame_read()
    telloFrames = telloFrameObj.frame
    telloFrameShared.set(telloFrames)

    # Ready To Go
    stateService.setState(OSState.READY)
    print("TELLO is : ", stateService.getCurrentState())

    while True:
        telloFrames = telloFrameObj.frame
        telloFrameShared.set(telloFrames)


def controllerProcessDummy():
    print("telloStart")
