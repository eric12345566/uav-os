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

    telloFrameShared.setAddress(tello.get_udp_video_address())

    # telloFrames = telloFrameObj.frame
    # telloFrameShared.set(telloFrames)

    # Ready To Go
    stateService.setState(OSState.READY)
    print("TELLO is : ", stateService.getCurrentState())

    while True:
        # telloFrames = telloFrameObj.frame
        # telloFrameShared.set(telloFrames)
        pass


def telloCmdRunner(cmdList):

    for cmd in cmdList:
        print("CMD: ", cmd)


def controllerProcessDummy():
    print("telloStart")
