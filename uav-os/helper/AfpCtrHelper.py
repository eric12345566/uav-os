"""
Deprecated: 因為拋棄了 Controller Process，因此不再需要與之溝通的 helper
"""

""" Utilities
"""
def cmdListAdd(cmdList, cmd, value):
    cmdList.append({"cmd": cmd, "value": value})


def cmdListClear(cmdList):
    cmdList.clear()


""" CMD Runner
"""


# TODO: 再多一個是While阻塞式的 CMD List Runner
def cmdListUavRun(FlightCmdService, cmdList):
    if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
        # logger.afp_debug("CTR READY")
        if FlightCmdService.registerInputCmdProcess("autoP"):
            # logger.afp_debug("register CMD Process")
            FlightCmdService.cmdListAssign(cmdList)
            FlightCmdService.startRunCmd()
    if FlightCmdService.currentState() == FlightState.DONE:
        # logger.afp_debug("CTR DONE")
        cmdListClear(cmdList)
        return True


def cmdUavRunOnce(FlightCmdService, cmd, value):
    alreadyRunOnce = False

    while True:
        if FlightCmdService.currentState() == FlightState.READY_FOR_CMD:
            logger.afp_debug("AFP Ready for Cmd")
            if FlightCmdService.registerInputCmdProcess("autoP"):
                logger.afp_debug("AFP register Ctr Process Success")
                pass
            else:
                logger.afp_debug("AFP register Ctr Process Fail, try again..")
                time.sleep(0.5)
        elif FlightCmdService.currentState() == FlightState.INPUT_CMD:
            logger.afp_debug("AFP Run command: " + str(cmd) + ", value: " + str(value))
            FlightCmdService.cmdRunOnce(cmd, value)
            FlightCmdService.startRunCmd()
        elif FlightCmdService.currentState() == FlightState.RUNNING_CMD:
            alreadyRunOnce = True
        elif FlightCmdService.currentState() == FlightState.FORCE_LAND:
            logger.afp_debug("cmd Force Landing")
            break
        elif FlightCmdService.currentState() == FlightState.DONE:
            logger.afp_debug("AFP Done")
            FlightCmdService.afp_StateBackToReady()
            if alreadyRunOnce:
                break


def uavGetInfo(infoCmd, FlightCmdService):
    logger.afp_debug("AFP get info start")
    FlightCmdService.runUavInfoCmd(infoCmd)
    logger.afp_debug("Flight State: " + str(FlightCmdService.currentState()))
    while FlightCmdService.currentState() == FlightState.GET_INFO:
        pass
    logger.afp_debug("AFP get info End")
    return FlightCmdService.getUavInfoValue()