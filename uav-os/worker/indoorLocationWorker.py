import numpy as np
import cv2 as cv
from djitellopy import Tello
import time
from module.indoorLocationAlgo.QrcodePositionAlgo import streamDecode
import keyboard
import time


# Transfer location ID to (x, y) value
def transferLocationID(x):
    return {
        '-1': (-1, -1),
        '1': (0, 0), '11': (0, 30), '21': (0, 60), '31': (0, 90), '41': (0, 120),
        '2': (30, 0), '12': (30, 30), '22': (30, 60), '32': (30, 90), '42': (30, 120),
        '3': (60, 0), '13': (60, 30), '23': (60, 60), '33': (60, 90), '43': (60, 120),
        '4': (90, 0), '14': (90, 30), '24': (90, 60), '34': (90, 90), '44': (90, 120),
        '5': (120, 0), '15': (120, 30), '25': (120, 60), '35': (120, 90), '45': (120, 120),
        '6': (150, 0), '16': (150, 30), '26': (150, 60), '36': (150, 90), '46': (150, 120),
        '7': (180, 0), '17': (180, 30), '27': (180, 60), '37': (180, 90), '47': (180, 120),
        '8': (210, 0), '18': (210, 30), '28': (210, 60), '38': (210, 90), '48': (210, 120),
        '9': (240, 0), '19': (240, 30), '29': (240, 60), '39': (240, 90), '49': (240, 120),
        '10': (270, 0), '20': (270, 30), '30': (270, 60), '40': (270, 90), '50': (270, 120)
    }[x]


def indoorLocationWorker(telloFrameBFR, indoorLocationShared, terminalService, tello):
    count = 1
    while True:
        frame = telloFrameBFR.frame
        count += 1
        # _, frame = cap.read()
        if count % 1 == 0:
            # flipFrame = frame = cv.flip(frame, 1)
            flipFrame = frame = cv.flip(frame, 0)
            rotateAngle, qrPosition, _ = streamDecode(flipFrame)
            # print('---------------Estimate Analytics----------------')
            # print('Rotate Angle: ' + str(rotateAngle))
            # print('Qrcode Position: ' + str(qrPosition))
            # print('-------------------------------------------------')

            # tello.send_rc_control(0, 0, 0, 0)
            indoorLocationShared.x_location, indoorLocationShared.y_location = transferLocationID(str(qrPosition))
            indoorLocationShared.direction = rotateAngle
            terminalService.setInfo('rotate', rotateAngle)
            terminalService.setInfo('position_X', indoorLocationShared.x_location)
            terminalService.setInfo('position_Y', indoorLocationShared.y_location)

        # print(indoorLocationShared.direction)

    # x, y, dirt = indoorLocationAlgo(frame)

    # indoorLocationShared.x_location = x
    # indoorLocationShared.y_location = x
