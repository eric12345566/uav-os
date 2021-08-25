import time
import keyboard
from module.terminalModule import setTerminal

# TODO:拿到 Destination之位置以後 進行角度修正與前進

def autoFlightController(tello, afStateService, logger, terminalService):
    tello.rotate_clockwise(235)
    while True:
        setTerminal(terminalService, tello)
        tello.move_forward(20)
        x = terminalService.getInfo('position_X')
        y = terminalService.getInfo('position_Y')

        if x == 70 and y == 70:
            print("Reach Destination")
            tello.move_forward(30)
            tello.land()
            afStateService.end()
            break
        time.sleep(0.2)
