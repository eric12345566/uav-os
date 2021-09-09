import time
import keyboard
from module.terminalModule import setTerminal
import numpy as np
import math

from worker.indoorLocationWorker import transferLocationID


def distance(v1):
    """
    :param v1: Destination - Source
    :return dis: 四捨五入的距離(Int)
    """
    dis = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    return round(dis)


def positionConfirm(terminalService, tello):
    """
    :returns maxLabel:出現最多次的Position, maxRotateAngle:出現最多次的RotateAngle
    """
    counter = 0
    positionList = []
    rotateList = []
    while counter != 10:
        setTerminal(terminalService, tello)
        x = terminalService.getInfo('position_X')
        y = terminalService.getInfo('position_Y')
        rotateAngle = terminalService.getInfo('rotate')
        positionList.append(np.array([x, y]))
        rotateList.append(round(rotateAngle))
        counter += 1
    print(str(positionList))
    print(str(rotateList))
    maxPosition = max(positionList.all(), key=positionList.count)
    maxRotateAngle = max(rotateList, key=rotateList.count)
    return maxPosition, maxRotateAngle


def autoFlightController(tello, afStateService, logger, terminalService):
    print("Get in Auto Flight")
    # tello.rotate_clockwise(235)
    source, currentRotateAngle = positionConfirm(terminalService, tello)
    print(source, currentRotateAngle)
    # Destination 需要從自走車那邊共享過來
    destination = np.array([30, 30])

    # 計算角度與距離

    targetRotateAngle, targetDistance = AngleCalculateForRoute(source, destination)
    # TODO: 使用Tello API 前進到Destination -> AUTO_LANDING

    neededRotateAngle = targetRotateAngle - currentRotateAngle
    if neededRotateAngle > 0:
        tello.rotate_clockwise(neededRotateAngle)
    else:
        tello.rotate_clockwise(neededRotateAngle + 360)
    time.sleep(2)
    tello.move_forward(targetDistance)
    afStateService.autoLanding()
    # while True:
    #     setTerminal(terminalService, tello)
    #     x = terminalService.getInfo('position_X')
    #     y = terminalService.getInfo('position_Y')

    # if (x, y) == (70, 70):
    #     print("Reach Destination")
    #     tello.move_forward(20)
    #     afStateService.finding_aruco()
    #     break
    # time.sleep(0.2)


# Angle for route Function

# Parameter
def AngleCalculateForRoute(source, destination):
    """
    :param source: 目前無人機的位置
    :param destination: 想要移動到的位置
    :returns angle: 先行旋轉角度 distance： 旋轉後直線前進距離
    """
    print(transferLocationID(str(40)))
    v1 = destination - source
    v2 = np.array([0, 1])

    print("V1:" + str(v1))
    print("\n\n\n\n\n\n\n")

    cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    angle = np.arccos(cosine_angle) * 180 / np.pi

    move_distance = distance(v1)
    print(move_distance)
    return angle, distance


# TODO: 給予點對點算出角度
print(AngleCalculateForRoute(np.array([30, 30]), np.array([0, 0])))
