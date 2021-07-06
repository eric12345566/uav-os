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

    """ log Tello Info
    """
    logger.ctrp_info("battery: " + str(tello.get_battery()))
    logger.ctrp_info("temperature: " + str(tello.get_temperature()))

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
        # logger.ctrp_debug("State: " + str(FlightCmdService.currentState()))
        if OSStateService.getCurrentState() != OSState.INITIALIZING:
            if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
                """ READY_FOR_CMD
                """
                logger.ctrp_debug("CTR ready")
                FlightCmdService.readyInit()
            elif FlightCmdService.currentState() == FlightState.INPUT_CMD:
                """ INPUT_CMD
                """
                logger.ctrp_debug("CTR input")
                pass
            elif FlightCmdService.currentState() == FlightState.RUNNING_CMD:
                """ RUNNING_CMD
                """
                logger.ctrp_debug("Controller Run Cmd")
                telloCmdPopRunner(FlightCmdService, tello)
                if FlightCmdService.isCmdRunAllComplete() and FlightCmdService.currentState() != FlightState.FORCE_LAND:
                    FlightCmdService.controller_CmdDone()
                    logger.ctrp_debug("CMD DONE")
            elif FlightCmdService.currentState() == FlightState.GET_INFO:
                """ GET_INFO
                """
                logger.ctrp_debug("CTR Get info")
                telloGetInfoRunner(FlightCmdService, tello)
            elif FlightCmdService.currentState() == FlightState.FORCE_LAND:
                """ FORCE_LAND
                """
                logger.ctrp_warning("Force Land Commit..")
                tello.land()
            elif FlightCmdService.currentState() == FlightState.DONE:
                """ DONE
                """
                logger.ctrp_debug("CTR Done")
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
        elif cmd['cmd'] == CmdEnum.send_rc_control:
            tello.send_rc_control(cmd['value'][0], cmd['value'][1], cmd['value'][2], cmd['value'][3])


def telloCmdPopRunner(FlightCmdService, tello):
    cmd = FlightCmdService.controller_PopCmd()
    if cmd['cmd'] == CmdEnum.takeoff:
        tello.takeoff()
    elif cmd['cmd'] == CmdEnum.move_forward:
        tello.move_forward(cmd['value'])
    elif cmd['cmd'] == CmdEnum.move_back:
        tello.move_back(cmd['value'])
    elif cmd['cmd'] == CmdEnum.move_left:
        tello.move_left(cmd['value'])
    elif cmd['cmd'] == CmdEnum.move_right:
        tello.move_right(cmd['value'])
    elif cmd['cmd'] == CmdEnum.move_down:
        tello.move_down(cmd['value'])
    elif cmd['cmd'] == CmdEnum.land:
        tello.land()
    elif cmd['cmd'] == CmdEnum.send_rc_control:
        # logger.ctrp_debug("rc: " + str(cmd['value'][0]) + "," + str(cmd['value'][1]) + ","
        #                   + str(cmd['value'][2]) + "," + str(cmd['value'][3]))
        tello.send_rc_control(cmd['value'][0], cmd['value'][1], cmd['value'][2], cmd['value'][3])


def telloGetInfoRunner(FlightCmdService, tello):
    cmd = FlightCmdService.controller_getUavInfoCmd()
    result = None
    if cmd == CmdEnum.get_battery:
        result = tello.get_battery()
    elif cmd == CmdEnum.get_height:
        result = tello.get_height()
    elif cmd == CmdEnum.get_distance_tof:
        result = tello.get_distance_tof()
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
