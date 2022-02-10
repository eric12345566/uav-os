import cv2
import cv2.aruco as aruco
import numpy as np


def arucoMarkerDetect(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_1000)
    arucoParameters = aruco.DetectorParameters_create()
    _corners, _ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=arucoParameters)

    return _corners, _ids, rejectedImgPoints


def arucoMarkerSelectDetect(frame, selectID):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_1000)
    arucoParameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=arucoParameters)

    resultCorners = [[]]
    haveMarker = False

    if np.all(ids is not None):
        for i in range(0, len(ids)):
            if ids[i] == [selectID]:
                haveMarker = True
                resultCorners[0] = corners[i]
    else:
        resultCorners = [[]]
        haveMarker = False

    return resultCorners, haveMarker


def arucoMarkerDetectFrame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_1000)
    arucoParameters = aruco.DetectorParameters_create()
    _corners, _ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=arucoParameters)

    if np.all(_ids is not None):
        # print(_ids)
        x_sum = _corners[0][0][0][0] + _corners[0][0][1][0] + _corners[0][0][2][0] + _corners[0][0][3][0]
        y_sum = _corners[0][0][0][1] + _corners[0][0][1][1] + _corners[0][0][2][1] + _corners[0][0][3][1]

        _x_centerPixel = x_sum * .25
        _y_centerPixel = y_sum * .25
        frame = cv2.circle(frame, (int(_x_centerPixel), int(_y_centerPixel)), 5, (255, 0, 0), -1)

    frame = aruco.drawDetectedMarkers(frame, _corners)

    return frame


def arucoMarkerDetectFrameTest(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_1000)
    arucoParameters = aruco.DetectorParameters_create()
    _corners, _ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=arucoParameters)

    if np.all(_ids is not None):
        # print(_ids)
        x_sum = _corners[0][0][0][0] + _corners[0][0][1][0] + _corners[0][0][2][0] + _corners[0][0][3][0]
        y_sum = _corners[0][0][0][1] + _corners[0][0][1][1] + _corners[0][0][2][1] + _corners[0][0][3][1]

        rect = np.array(_corners)
        rect = rect.reshape([4, 1, 2]).astype(np.int64)
        print(rect)
        dist = cv2.pointPolygonTest(rect, (463, 1663), False)
        print(dist)

        _x_centerPixel = x_sum * .25
        _y_centerPixel = y_sum * .25
        frame = cv2.circle(frame, (int(_x_centerPixel), int(_y_centerPixel)), 5, (255, 0, 0), 5)

    frame = aruco.drawDetectedMarkers(frame, _corners)

    return frame
