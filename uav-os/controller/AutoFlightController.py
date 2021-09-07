import time
import keyboard
from module.terminalModule import setTerminal
import numpy as np


# TODO:拿到 Destination之位置以後 進行角度修正與前進

def autoFlightController(tello, afStateService, logger, terminalService):
    tello.rotate_clockwise(235)
    while True:
        setTerminal(terminalService, tello)
        tello.move_forward(20)
        x = terminalService.getInfo('position_X')
        y = terminalService.getInfo('position_Y')

        if (x, y) == (70, 70):
            print("Reach Destination")
            tello.move_forward(20)
            afStateService.finding_aruco()
            break
        time.sleep(0.2)


# Angle for route Function

# Parameter
def AngleCalculateForRoute(source, destination):
    """
    :param source: 目前無人機的位置
    :param destination: 想要移動到的位置
    :returns angle: 先行旋轉角度 distance： 旋轉後直線前進距離
    """
    v1 = destination - source
    v2 = np.array([0, 1])

    cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    angle = np.arccos(cosine_angle) * 180 / np.pi
    distance = 0
    return angle * 180 / np.pi


# TODO: 給予點對點算出角度
# print(AngleCalculateForRoute(np.array([30, 30]), np.array([0, 0])))
