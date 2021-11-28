import time
import keyboard
from module.terminalModule import setTerminal
import numpy as np
import math
import json
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
    while True:
        counter = 0
        positionList = []
        rotateList = []
        while counter != 100:
            setTerminal(terminalService, tello)
            x = terminalService.getInfo('position_X')
            y = terminalService.getInfo('position_Y')
            rotateAngle = terminalService.getInfo('rotate')
            positionList.append(([x, y]))
            rotateList.append(round(rotateAngle))
            counter += 1
        print(str(positionList))
        print(str(rotateList))
        maxPosition = max(positionList, key=positionList.count)
        maxRotateAngle = max(rotateList, key=rotateList.count)
        if maxPosition[0] != -1:
            break
    return maxPosition, maxRotateAngle


def autoFlightController(tello, afStateService, logger, terminalService, destination):
    print("Get in Auto Flight")
    # tello.rotate_clockwise(235)
    source, currentRotateAngle = positionConfirm(terminalService, tello)
    print(source, currentRotateAngle)
    print('------------------------------------------------------')
    # Destination 需要從自走車那邊共享過來
    # destination = np.array([412, 124])

    # 計算角度與距離

    targetRotateAngle, targetDistance, v1 = AngleCalculateForRoute(source, destination)
    print(targetRotateAngle, targetDistance)
    print('------------------------------------------------------')
    rotateController(targetRotateAngle, currentRotateAngle, targetDistance, tello, v1)


def rotateController(targetRotateAngle, currentRotateAngle, targetDistance, tello, v1):
    neededRotateAngle = targetRotateAngle - currentRotateAngle
    print("----------旋轉角度----------")
    print(str(neededRotateAngle))
    if neededRotateAngle > 0:
        neededRotateAngle
    else:
        neededRotateAngle = neededRotateAngle + 360
    time.sleep(0.5)
    try:
        tello.rotate_clockwise(neededRotateAngle)
        # if v1[0] >= 0:
        #
        # else:
        #     tello.rotate_counter_clockwise(neededRotateAngle)
    except:
        rotateController(targetRotateAngle, currentRotateAngle, targetDistance, tello, v1)
    # 判斷方位
    time.sleep(2)
    tello.move_forward(int(targetDistance))
    time.sleep(2)
    # tello.move_forward(int(targetDistance / 2))


# Parameter
def AngleCalculateForRoute(source, destination):
    """
    :param source: 目前無人機的位置
    :param destination: 想要移動到的位置
    :returns angle: 先行旋轉角度 distance： 旋轉後直線前進距離
    """

    print("Destination, source")
    print(destination, source)
    # v1 = source - destination
    v1 = destination - source
    # 固定一向量往上的方向
    v2 = np.array([0, 1])

    print("V1:" + str(v1))
    print("\n\n\n\n\n\n\n")


    cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    angle = np.arccos(cosine_angle) * 180 / np.pi
    if v1[0] < 0:
        angle =  360 - angle
    print(angle)
    move_distance = distance(v1)
    print(move_distance)
    return round(angle), move_distance, v1


def toDoubleQuotation(routeDataStr):
    routeStr = str(routeDataStr)
    routeStr = routeStr.replace('\'', "\"")
    return routeStr


def flightRouteParse(routeData):
    routeData = toDoubleQuotation(routeData)
    decodedData = json.loads(routeData)
    getOnStation = decodedData["getOnStation"]
    getOffStation = decodedData["getOffStation"]
    pass

# TODO: 給予點對點算出角度
# print(AngleCalculateForRoute(np.array([240, 120]), np.array([30, 30])))