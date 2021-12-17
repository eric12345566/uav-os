import time
def terminalController( terminalService, uavSocketService ):
    while True:
        telloHeight = terminalService.getInfo('high')
        telloBattery = terminalService.getInfo('battery')
        qrPosition = terminalService.getInfo('qrPosition')
        uavSocketService.updateUavBodyCondition(telloBattery, qrPosition, telloHeight)
        time.sleep(0.2)