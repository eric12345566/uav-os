# TODO:拿到 Destination之位置以後 進行角度修正與前進

def autoFlightController(tello, afStateService, logger, terminalService):

    while True:
        tello.rotate_clockwise(30)
        if terminalService.getInfo('rotate') == 0:
            tello.land()
            break

