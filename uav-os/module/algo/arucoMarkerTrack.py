import cv2
import cv2.aruco as aruco
import numpy as np


def arucoTrackPostEstimate(matrix_coefficients, distortion_coefficients, frame):
    centerX = None
    centerY = None
    rvec = None
    tvec = None

    # operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Change grayscale
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)  # Use 5x5 dictionary to find markers
    parameters = aruco.DetectorParameters_create()  # Marker detection parameters
    # lists of ids and the corners belonging to each id
    corners, ids, rejected_img_points = aruco.detectMarkers(gray, aruco_dict,
                                                            parameters=parameters,
                                                            cameraMatrix=matrix_coefficients,
                                                            distCoeff=distortion_coefficients)

    if np.all(ids is not None):  # If there are markers found by detector
        for i in range(0, len(ids)):  # Iterate in markers
            # Estimate pose of each marker and return the values rvec and tvec---different from camera coefficients
            rvec, tvec, markerPoints = aruco.estimatePoseSingleMarkers(corners[i], 0.066, matrix_coefficients,
                                                                       distortion_coefficients)
            # 記得更改第二個參數 -> ArUco Marker 大小的數值，通常以 m米 為單位
            (rvec - tvec).any()  # get rid of that nasty numpy value array error

            x_sum = corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]
            y_sum = corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]

            _x_centerPixel = x_sum * .25
            _y_centerPixel = y_sum * .25

            centerX = int(_x_centerPixel)
            centerY = int(_y_centerPixel)
    else:
        centerX = None
        centerY = None
        rvec = None
        tvec = None
    return centerX, centerY, rvec, tvec, ids


def arucoTrackWriteFrame(matrix_coefficients, distortion_coefficients, frame):
    centerX = 0
    centerY = 0
    frameHeight, frameWidth, _ = frame.shape

    # Center point of frame
    centerX = frameWidth // 2
    centerY = frameHeight // 2

    # 是否frame的中心點在marker方框中
    # isFrameCenterInMarker = -2

    # operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Change grayscale
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)  # Use 5x5 dictionary to find markers
    parameters = aruco.DetectorParameters_create()  # Marker detection parameters
    # lists of ids and the corners belonging to each id
    corners, ids, rejected_img_points = aruco.detectMarkers(gray, aruco_dict,
                                                            parameters=parameters,
                                                            cameraMatrix=matrix_coefficients,
                                                            distCoeff=distortion_coefficients)

    if np.all(ids is not None):  # If there are markers found by detector
        for i in range(0, len(ids)):  # Iterate in markers
            # Estimate pose of each marker and return the values rvec and tvec---different from camera coefficients
            rvec, tvec, markerPoints = aruco.estimatePoseSingleMarkers(corners[i], 0.066, matrix_coefficients,
                                                                       distortion_coefficients)
            # 記得更改第二個參數 -> ArUco Marker 大小的數值，通常以 m米 為單位
            (rvec - tvec).any()  # get rid of that nasty numpy value array error

            x_sum = corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]
            y_sum = corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]

            # 四個角標點
            frame = cv2.circle(frame, (int(corners[0][0][0][0]), int(corners[0][0][0][1])), 5, (255, 255, 0), -1)
            frame = cv2.circle(frame, (int(corners[0][0][1][0]), int(corners[0][0][1][1])), 5, (255, 255, 0), -1)
            frame = cv2.circle(frame, (int(corners[0][0][2][0]), int(corners[0][0][2][1])), 5, (255, 255, 0), -1)
            frame = cv2.circle(frame, (int(corners[0][0][3][0]), int(corners[0][0][3][1])), 5, (255, 255, 0), -1)

            # 標上四個點座標
            xy = "%d,%d" % (corners[0][0][0][0], corners[0][0][0][1])
            frame = cv2.putText(frame, xy, (int(corners[0][0][0][0]), int(corners[0][0][0][1])), cv2.FONT_HERSHEY_PLAIN, 3,
                                (255, 255, 0), thickness=2)
            xy = "%d,%d" % (corners[0][0][1][0], corners[0][0][1][1])
            frame = cv2.putText(frame, xy, (int(corners[0][0][1][0]), int(corners[0][0][1][1])), cv2.FONT_HERSHEY_PLAIN, 3,
                                (255, 255, 0), thickness=2)
            xy = "%d,%d" % (corners[0][0][2][0], corners[0][0][2][1])
            frame = cv2.putText(frame, xy, (int(corners[0][0][2][0]), int(corners[0][0][2][1])), cv2.FONT_HERSHEY_PLAIN, 3,
                                (255, 255, 0), thickness=2)
            xy = "%d,%d" % (corners[0][0][3][0], corners[0][0][3][1])
            frame = cv2.putText(frame, xy, (int(corners[0][0][3][0]), int(corners[0][0][3][1])), cv2.FONT_HERSHEY_PLAIN, 3,
                                (255, 255, 0), thickness=2)

            # 檢查 frame 中心點有沒有在 ArUco Marker 方框內
            # rect = np.array(corners)
            # rect = rect.reshape([4, 1, 2]).astype(np.int64)
            # isFrameCenterInMarker = cv2.pointPolygonTest(rect, (centerX, centerY), False)

            _x_centerPixel = x_sum * .25
            _y_centerPixel = y_sum * .25
            centerX = int(_x_centerPixel)
            centerY = int(_y_centerPixel)
            frame = cv2.circle(frame, (int(_x_centerPixel), int(_y_centerPixel)), 5, (255, 0, 0), -1)

        aruco.drawDetectedMarkers(frame, corners)  # Draw A square around the markers
        aruco.drawAxis(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.01)  # Draw Axis
    return centerX, centerY


def arucoMultiTrackWriteFrame(matrix_coefficients, distortion_coefficients, frame):
    centerX = []
    centerY = []
    # 是否frame的中心點在marker方框中
    # isFrameCenterInMarker = -2

    # operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Change grayscale
    aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)  # Use 5x5 dictionary to find markers
    parameters = aruco.DetectorParameters_create()  # Marker detection parameters
    # lists of ids and the corners belonging to each id
    corners, ids, rejected_img_points = aruco.detectMarkers(gray, aruco_dict,
                                                            parameters=parameters,
                                                            cameraMatrix=matrix_coefficients,
                                                            distCoeff=distortion_coefficients)

    if np.all(ids is not None):  # If there are markers found by detector
        for i in range(0, len(ids)):  # Iterate in markers
            # Estimate pose of each marker and return the values rvec and tvec---different from camera coefficients
            rvec, tvec, markerPoints = aruco.estimatePoseSingleMarkers(corners[i], 0.066, matrix_coefficients,
                                                                       distortion_coefficients)
            # 記得更改第二個參數 -> ArUco Marker 大小的數值，通常以 m米 為單位
            (rvec - tvec).any()  # get rid of that nasty numpy value array error

            x_sum = corners[i][0][0][0] + corners[i][0][1][0] + corners[i][0][2][0] + corners[i][0][3][0]
            y_sum = corners[i][0][0][1] + corners[i][0][1][1] + corners[i][0][2][1] + corners[i][0][3][1]

            # 四個角標點
            frame = cv2.circle(frame, (int(corners[i][0][0][0]), int(corners[i][0][0][1])), 5, (255, 255, 0), -1)
            frame = cv2.circle(frame, (int(corners[i][0][1][0]), int(corners[i][0][1][1])), 5, (255, 255, 0), -1)
            frame = cv2.circle(frame, (int(corners[i][0][2][0]), int(corners[i][0][2][1])), 5, (255, 255, 0), -1)
            frame = cv2.circle(frame, (int(corners[i][0][3][0]), int(corners[i][0][3][1])), 5, (255, 255, 0), -1)

            # 標上四個點座標
            xy = "%d,%d" % (corners[i][0][0][0], corners[i][0][0][1])
            frame = cv2.putText(frame, xy, (int(corners[i][0][0][0]), int(corners[i][0][0][1])), cv2.FONT_HERSHEY_PLAIN,
                                3,
                                (255, 255, 0), thickness=2)
            xy = "%d,%d" % (corners[i][0][1][0], corners[i][0][1][1])
            frame = cv2.putText(frame, xy, (int(corners[i][0][1][0]), int(corners[i][0][1][1])), cv2.FONT_HERSHEY_PLAIN,
                                3,
                                (255, 255, 0), thickness=2)
            xy = "%d,%d" % (corners[i][0][2][0], corners[i][0][2][1])
            frame = cv2.putText(frame, xy, (int(corners[i][0][2][0]), int(corners[i][0][2][1])), cv2.FONT_HERSHEY_PLAIN,
                                3,
                                (255, 255, 0), thickness=2)
            xy = "%d,%d" % (corners[i][0][3][0], corners[i][0][3][1])
            frame = cv2.putText(frame, xy, (int(corners[i][0][3][0]), int(corners[i][0][3][1])), cv2.FONT_HERSHEY_PLAIN,
                                3,
                                (255, 255, 0), thickness=2)

            # 檢查 frame 中心點有沒有在 ArUco Marker 方框內
            # rect = np.array(corners)
            # rect = rect.reshape([4, 1, 2]).astype(np.int64)
            # isFrameCenterInMarker = cv2.pointPolygonTest(rect, (centerX, centerY), False)

            _x_centerPixel = x_sum * .25
            _y_centerPixel = y_sum * .25
            centerX.append(int(_x_centerPixel))
            centerY.append(int(_y_centerPixel))
            frame = cv2.circle(frame, (int(_x_centerPixel), int(_y_centerPixel)), 5, (255, 0, 0), -1)
            aruco.drawAxis(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.01)  # Draw Axis
        aruco.drawDetectedMarkers(frame, corners)  # Draw A square around the markers

    return centerX, centerY, ids
