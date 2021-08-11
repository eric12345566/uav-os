import numpy as np
import cv2 as cv
from djitellopy import Tello

from module.indoorLocationAlgo.QrcodePositionAlgo import streamDecode


# Transfer location ID to (x, y) value
def transferLocationID(x):
    return {
        '-1': (-1, -1),
        '1': (0, 0),
        '2': (10, 10),
        '3': (30, 30),
        '7': (70, 70),
        '9': (90, 90)
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
            tello.send_rc_control(0, 0, 0, 0)
            indoorLocationShared.x_location, indoorLocationShared.y_location = transferLocationID(str(qrPosition))
            indoorLocationShared.direction = rotateAngle
            terminalService.setInfo('rotate', rotateAngle)
        print(indoorLocationShared.direction)

    # x, y, dirt = indoorLocationAlgo(frame)

    # indoorLocationShared.x_location = x
    # indoorLocationShared.y_location = x
