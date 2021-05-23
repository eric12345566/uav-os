import time
from State.OSStateEnum import OSState
from djitellopy import Tello
from State.FlightStateEnum import FlightState
from State.CmdEnum import CmdEnum
from service.LoggerService import LoggerService

logger = LoggerService()


def ControllerProcess(telloFrameShared, OSStateService, FlightCmdService):
    """ init Tello object
    """
    tello = Tello()
    tello.connect()

    """ stream
    """
    tello.streamoff()
    tello.streamon()

    """ shared stream UDP address
    """
    telloFrameShared.setAddress(tello.get_udp_video_address())

    """ State Change
    """
    OSStateService.controllerInitReady()
    FlightCmdService.initDone()

    while True:
        if OSStateService.getCurrentState() != OSState.INITIALIZING:
            if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
                """ READY_FOR_CMD
                """
                pass
            elif FlightCmdService.currentState() == FlightState.INPUT_CMD:
                """ INPUT_CMD
                """
                pass
            elif FlightCmdService.currentState() == FlightState.RUNNING_CMD:
                """ RUNNING_CMD
                """
                telloCmdPopRunner(FlightCmdService, tello)
                if FlightCmdService.isCmdRunAllComplete():
                    FlightCmdService.controller_CmdDone()
            elif FlightCmdService.currentState() == FlightState.GET_INFO:
                """ GET_INFO
                """
                telloGetInfoRunner(FlightCmdService, tello)
            elif FlightCmdService.currentState() == FlightState.DONE:
                """ DONE
                """
                FlightCmdService.controller_StateBackToReady()


""" CMD Runner
"""


def telloCmdRunner(cmdList, tello):
    for idx, cmd in enumerate(cmdList):
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


def telloCmdPopRunner(FlightCmdService, tello):
    cmd = FlightCmdService.controller_PopCmd()
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


def telloGetInfoRunner(FlightCmdService, tello):
    cmd = FlightCmdService.controller_getUavInfoCmd()
    result = None
    if cmd == CmdEnum.get_battery:
        result = tello.get_battery()
    elif cmd == CmdEnum.get_height:
        result = tello.get_height()
    FlightCmdService.controller_getUavInfoDone(result)


""" Dummy Runner
"""


def telloGetInfoRunnerDummy(FlightCmdService):
    cmd = FlightCmdService.controller_getUavInfoCmd()
    if cmd == CmdEnum.get_battery:
        logger.ctrp_info("get battery")
    elif cmd == CmdEnum.get_height:
        logger.ctrp_info("get height")
    FlightCmdService.controller_getUavInfoDone(12)


def telloCmdPopRunnerDummy(FlightCmdService):
    cmd = FlightCmdService.controller_PopCmd()
    if cmd['cmd'] == CmdEnum.takeoff:
        logger.ctrp_info("takeoff")
    elif cmd['cmd'] == CmdEnum.move_forward:
        logger.ctrp_info("move_forward")
    elif cmd['cmd'] == CmdEnum.move_left:
        logger.ctrp_info("move_left")
    elif cmd['cmd'] == CmdEnum.move_right:
        logger.ctrp_info("move_right")
    elif cmd['cmd'] == CmdEnum.land:
        logger.ctrp_info("land")
    time.sleep(1)


def controllerProcessDummy(telloFrameShared, OSStateService, FlightCmdService):
    logger.ctrp_info("Start Process")

    """ State Change
    """
    OSStateService.controllerInitReady()
    FlightCmdService.initDone()

    while True:

        if OSStateService.getCurrentState() != OSState.INITIALIZING:
            if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
                """ READY_FOR_CMD
                """
                pass
            elif FlightCmdService.currentState() == FlightState.INPUT_CMD:
                """ INPUT_CMD
                """
                pass
            elif FlightCmdService.currentState() == FlightState.RUNNING_CMD:
                """ RUNNING_CMD
                """
                telloCmdPopRunnerDummy(FlightCmdService)
                if FlightCmdService.isCmdRunAllComplete():
                    # logger.ctrp_debug("in cmd run all complete")
                    FlightCmdService.controller_CmdDone()
            elif FlightCmdService.currentState() == FlightState.GET_INFO:
                """ GET_INFO
                """
                telloGetInfoRunnerDummy(FlightCmdService)
            elif FlightCmdService.currentState() == FlightState.DONE:
                """ DONE
                """
                FlightCmdService.controller_StateBackToReady()
