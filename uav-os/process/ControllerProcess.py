import time
from State.OSStateEnum import OSState
from djitellopy import Tello
from State.FlightStateEnum import FlightState
from State.CmdEnum import CmdEnum
from service.LoggerService import LoggerService


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
    # OSStateService.setState(OSState.READY)
    OSStateService.controllerInitReady()
    FlightCmdService.initDone()
    while True:
        if OSStateService.getCurrentState() != OSState.INITIALIZING:
            # print("Flight State: ", FlightCmdService.currentState())
            # state: ready_for_cmd
            if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
                """ READY_FOR_CMD
                """
                # print("CtrProcess: ready, ", FlightCmdService.currentState())
                pass
            elif FlightCmdService.currentState() == FlightState.INPUT_CMD:
                # print("CtrProcess: wait for input cmd..")
                """ INPUT_CMD
                """
                pass
            elif FlightCmdService.currentState() == FlightState.RUNNING_CMD:
                # print("CtrProcess: running cmd..")
                """ RUNNING_CMD
                """
                telloCmdRunner(FlightCmdService.controller_GetCmdList(), tello)
                FlightCmdService.controller_CmdDone()
            elif FlightCmdService.currentState() == FlightState.DONE:
                # print("Done")
                """ DONE
                """
                FlightCmdService.controller_StateBackToReady()


def telloCmdRunner(cmdList, tello):
    for cmd in cmdList:
        if cmd['cmd'] == CmdEnum.takeoff:
            tello.takeoff()
        elif cmd['cmd'] == CmdEnum.move_forward:
            tello.move_forward(cmd['value'])
        elif cmd['cmd'] == CmdEnum.move_left:
            tello.move_left(cmd['value'])
        elif cmd['cmd'] == CmdEnum.move_right:
            tello.move_right(cmd['value'])
        elif cmd['cmd'] == CmdEnum.land:
            tello.land()


def controllerProcessDummy(telloFrameShared, OSStateService, FlightCmdService):
    print("Tello Fly")

    # Controller Ready
    OSStateService.setState(OSState.READY)
    FlightCmdService.initDone()

    while True:

        # state: ready_for_cmd
        if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
            print("CtrProcess: ready, ", FlightCmdService.currentState())
            pass
        elif FlightCmdService.currentState() == FlightState.INPUT_CMD:
            print("CtrProcess: wait for input cmd..")
        elif FlightCmdService.currentState() == FlightState.RUNNING_CMD:
            print("CtrProcess: running cmd..")
            i = 0
            # for cmd in FlightCmdService.controller_GetCmdList():
            #     print("i: ", i)
            #     print(cmd)
            #     i += 1
            telloCmdRunner(FlightCmdService.controller_GetCmdList())
            FlightCmdService.controller_CmdDone()
        elif FlightCmdService.currentState() == FlightState.DONE:
            print("Done")
            FlightCmdService.controller_StateBackToReady()
            break
