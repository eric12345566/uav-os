from State.OSStateEnum import OSState
from djitellopy import Tello


def ControllerProcess(telloFrameShared, OSStateService, FlightCmdService):
    """ init Tello object
    """
    tello = Tello()
    tello.connect()

    """ stream
    """
    tello.streamoff()
    tello.streamon()

    # shared stream UDP address
    telloFrameShared.setAddress(tello.get_udp_video_address())

    # Ready To Go
    OSStateService.setState(OSState.READY)

    while True:
        pass


def telloCmdRunner(cmdList):

    for cmd in cmdList:
        print("CMD: ", cmd)


def controllerProcessDummy(telloFrameShared, OSStateService, FlightCmdService):
    print("Tello Fly")


