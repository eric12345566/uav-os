import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import math
import json


def distance(List):  # 計算與中間點之距離

    # List[0][0] +
    # for point in List:    #先找到中間點

    # print(len(List))
    middlePoint = [(List[0][0] + List[2][0]) / 2, (List[0][1] + List[2][1]) / 2]
    disToMiddle = math.sqrt((480 - middlePoint[0]) ** 2 + (360 - middlePoint[1]) ** 2)
    # # print(math.sqrt((480 - (List[0][0] + List[2][0])/2)**2) , (List[0][1] + List[2][1])/2)

    return [middlePoint, disToMiddle]


def drawPolyGon(positions, frame):
    middleIndex = 0
    list = []  # 所有的Point
    minDistance = 100000
    middleQRcode = []  # 存放middlepoint

    for index, pos in enumerate(positions, start=0):  # 所有的QR code

        # print('Index')
        # print(index)
        red = 0
        green = 0
        pList = []  # 單次的Point四點
        for i in range(4):  # QR code四個點
            pList.append([pos.polygon[i].x, pos.polygon[i].y])
            # cv2.circle(frame, (pos.polygon[i].x, pos.polygon[i].y), 5, (255, 0, 0), -1)  # draw circle points
            # cv2.putText(frame, str([pos.polygon[i].x, pos.polygon[i].y]) + str(i),
            #             (pos.polygon[i].x - 10, pos.polygon[i].y - 10)
            #             , cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1, cv2.LINE_AA)
        # print('Distance:')
        # print(distance(pList))
        eachPoint = distance(pList)
        # cv2.circle(frame, (int(eachPoint[0][0]), int(eachPoint[0][1])), 5, (255, 0, 0), -1)  # Draw Middle Point
        # cv2.putText(frame, str(round(eachPoint[1], 2)) + str(i),
        #             (int(eachPoint[0][0]) - 10, int(eachPoint[0][1]) - 10)
        #             , cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)
        # cv2.circle(frame, (pos.polygon[i].x, pos.polygon[i].y), 5, (255, 0, 0), -1)

        if eachPoint[1] < minDistance:
            minDistance = eachPoint[1]
            # 紀錄最中間再所有position的Index
            middleIndex = index
            # 紀錄最中間的座標
            middleQRcode = pList

        # Calculate Distance
        list.append(pList)
        # pts = np.array(pList, np.int32)
        # pts = pts.reshape((-1, 1, 2))
        # cv2.polylines(frame, [pts], True, (0, 255, 0))

    # TODO: Decode QrcodeID from Zbar
    QrPositionID = positions[middleIndex].data
    QrPositionID = json.loads(QrPositionID)
    QrPositionID = QrPositionID["id"]
    # print(QrPositionID)
    # pts = np.array(middleQRcode, np.int32)
    # pts = pts.reshape((-1, 1, 2))
    # print("=====================PTS=====================")
    # print(middleQRcode)
    # cv2.polylines(frame, [pts], True, (0, 0, 255))

    # 解決Frame超出界線的問題（x<0 or y<0）
    top_left_x = min([middleQRcode[0][0], middleQRcode[1][0], middleQRcode[2][0], middleQRcode[3][0]]) - 25
    top_left_x = 0 if top_left_x < 0 else top_left_x
    top_left_y = min([middleQRcode[0][1], middleQRcode[1][1], middleQRcode[2][1], middleQRcode[3][1]]) - 25
    top_left_y = 0 if top_left_y < 0 else top_left_y
    bot_right_x = max([middleQRcode[0][0], middleQRcode[1][0], middleQRcode[2][0], middleQRcode[3][0]]) + 25
    bot_right_x = 0 if bot_right_x < 0 else bot_right_x
    bot_right_y = max([middleQRcode[0][1], middleQRcode[1][1], middleQRcode[2][1], middleQRcode[3][1]]) + 25
    bot_right_y = 0 if bot_right_y < 0 else bot_right_y

    frame = frame[top_left_y:bot_right_y + 1, top_left_x:bot_right_x + 1]
    # print(top_left_x, top_left_y, bot_right_x, bot_right_y)
    return frame, QrPositionID


def streamDecode(frame):
    recFrame = frame  # copy origin frame
    decodeObjects = pyzbar.decode(frame)  # decode QRcode
    # print(decodeObjects)
    QrPositionID = -1
    if decodeObjects:
        # print(decodeObjects)
        recFrame, QrPositionID = drawPolyGon(decodeObjects, recFrame)
        # # print(drawPolyGon(decodeObjects, recFrame))
        # for obj in decodeObjects:
        #     # print("QrCode Position: ", obj.polygon[1].x)
    # cv2.circle(recFrame, (480, 360), 5, (255, 0, 0), -1)  # draw circle points
    recFrame = cv2.resize(recFrame, None, fx=1.25, fy=1.25, interpolation=cv2.INTER_CUBIC)

    rotateAngle, recFrame = QrcodeEstimate(recFrame)
    # print('---------------------Return RotateAngle---------------------')
    # print(rotateAngle)
    # print('------------------------------------------------------------')

    # TODO:跟著Position編號一起傳回去
    return rotateAngle, QrPositionID, frame
    # cv2.imshow("Frame", recFrame)
    # key = cv2.waitKey(1)
    # if key == ord('q') or key == 27:  # Esc
    #     break


# Angle Testing Function
def AngleCalculate(v1, v2, v3):
    a = v1  # B點表示要被計算的點
    b = v2
    c = v3
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    # print(np.degrees(angle))
    return angle


def dotproduct(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))


def length(v):
    return math.sqrt(dotproduct(v, v))


# v2: 中間點, v1:
def VectorAngle(v1, v2, v3):
    vector1 = v1 - v2
    vector2 = v3 - v2

    # angle_1 -> v3 出發到 v1 的弧度
    angle = math.atan2(vector1[0] * vector2[1] - vector1[1] * vector2[0],
                       vector1[0] * vector2[0] + vector1[1] * vector2[1])
    # print("[VectorAngle]: signedAngle: ")
    # print(angle)
    if angle > 0:
        return True
    else:
        return False


# Sorting vertex
def VertexSort(v1, v2, v3):
    maxAngle = 0
    rightVertex = 0
    bottomVertex = 0
    a1 = AngleCalculate(v2, v1, v3)
    # a2 is the angle that we want calculate
    a2 = AngleCalculate(v1, v2, v3)
    a3 = AngleCalculate(v1, v3, v2)

    # To Sort angle and find largest angle to be second vertex
    if a1 > a2 and a3 < a1:
        if a1 > a3:
            maxAngle = 1
            if VectorAngle(v2, v1, v3):
                rightVertex = 2
                bottomVertex = 3
            else:
                rightVertex = 3
                bottomVertex = 2
    else:
        if a2 > a3:
            maxAngle = 2
            if VectorAngle(v1, v2, v3):
                rightVertex = 1
                bottomVertex = 3
            else:
                rightVertex = 3
                bottomVertex = 1
        else:
            maxAngle = 3
            if VectorAngle(v1, v3, v2):
                rightVertex = 1
                bottomVertex = 2
            else:
                rightVertex = 2
                bottomVertex = 1
    # print(maxAngle)
    return maxAngle, rightVertex, bottomVertex


# 進行定位點預測
def QrcodeEstimate(frame):
    # image = cv2.imread("./image/IMG_7617.JPG")
    image = frame.copy()
    oriImage = frame.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 高斯濾波法
    src_gray = cv2.GaussianBlur(image, (7, 7), 0)
    ret, mask = cv2.threshold(src_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    copyImage = mask
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    copyImage = cv2.morphologyEx(copyImage, cv2.MORPH_OPEN, element)
    canny = cv2.Canny(copyImage, 100, 200)

    contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    hierarchy = hierarchy[0]
    found = []
    for i in range(len(contours)):
        k = i
        c = 0
        while hierarchy[k][2] != -1:
            k = hierarchy[k][2]
            c = c + 1
        if c >= 5:
            found.append(i)

    for i in found:
        img_dc = image.copy()
        # cv2.drawContours(img_dc, contours, i, (0, 255, 0), 50)
        # cv2.drawContours(oriImage, contours, i, (0, 255, 0), 25)
        # show(img_dc)

    # Box Place the location of all vertex
    Box = []
    # print("Vertex Box: ")
    for i in found:
        rect = cv2.minAreaRect(contours[i])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        # 找到三個框框的四個座標
        Box.append(box)
        # cv2.circle(draw_img, (box[0][0], box[0][1]), 30, (0, 255, 255), 3)
        # cv2.circle(draw_img, (box[1][0], box[1][1]), 30, (0, 255, 255), 3)
        # cv2.circle(draw_img, (box[2][0], box[2][1]), 30, (0, 255, 255), 3)
        # cv2.circle(draw_img, (box[3][0], box[3][1]), 30, (0, 255, 255), 3)
        # pts = np.array(box, np.int32)
        # pts = pts.reshape((-1, 1, 2))
        # # 用綠線畫出所有的定位點
        # cv2.polylines(oriImage, [pts], True, (0, 255, 0), 5)
    # print(Box)
    # print("Box!!!")
    # print(len(Box))

    # 如果沒有超過三個 回傳角度為-1
    if len(Box) < 3:
        return -1, canny
    # 在Plot 標出定位點位置
    # show(draw_img)
    boxes = []
    for i in found:
        rect = cv2.minAreaRect(contours[i])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        box = map(tuple, box)
        boxes.append(box)

    # mPoint : three middle point of three squares
    mPoint = ((Box[0][0] + Box[0][2]) / 2, (Box[1][0] + Box[1][2]) / 2, (Box[2][0] + Box[2][2]) / 2)
    cv2.circle(oriImage, (int(mPoint[0][0]), int(mPoint[0][1])), 30, (0, 255, 255), 3)
    cv2.circle(oriImage, (int(mPoint[1][0]), int(mPoint[1][1])), 30, (0, 255, 255), 3)
    cv2.circle(oriImage, (int(mPoint[2][0]), int(mPoint[2][1])), 30, (0, 255, 255), 3)

    # print("MiddlePoint: " + str(mPoint))
    # pts = np.array(Box[VertexSort(mPoint[0], mPoint[1], mPoint[2]) - 1], np.int32)
    # pts = pts.reshape((-1, 1, 2))
    # # 用綠線畫出所有的定位點
    # cv2.polylines(oriImage, [pts], True, (0, 0, 255), 5)

    VertexSortResult = VertexSort(mPoint[0], mPoint[1], mPoint[2])

    # Red:0(middle), Green:1(right), Blue:2(bottom) Mark color to recognize sorted vertex
    cv2.drawContours(oriImage, contours, found[VertexSortResult[0] - 1], (0, 0, 255), 10)
    cv2.drawContours(oriImage, contours, found[VertexSortResult[1] - 1], (0, 255, 0), 10)
    cv2.drawContours(oriImage, contours, found[VertexSortResult[2] - 1], (255, 0, 0), 10)

    leftVertex = VertexSortResult[0]
    rightVertex = VertexSortResult[1]
    bottomVertex = VertexSortResult[2]
    middlePoint = (mPoint[rightVertex - 1] + mPoint[bottomVertex - 1]) / 2

    directionEnd = (mPoint[rightVertex - 1] + mPoint[leftVertex - 1]) / 2
    # print(directionEnd)
    cv2.circle(oriImage, (int(directionEnd[0]), int(directionEnd[1])), 30, (0, 255, 255), 3)

    directionVector = directionEnd - middlePoint
    # print(directionEnd, middlePoint)
    # print(directionVector)
    forwardVector = [0, -100]
    radian = math.atan2(directionVector[1], directionVector[0]) - math.atan2(forwardVector[1], forwardVector[0])
    # print("__________________RotateAngle___________________")
    # print(radian)

    if radian < 0:
        rotateAngle = radian * 180 / math.pi + 360
    else:
        rotateAngle = radian * 180 / math.pi

    cv2.putText(oriImage, str(round(rotateAngle, 2)),
                (int(middlePoint[0]) + 20, int(middlePoint[1]) - 30)
                , cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), 5, cv2.LINE_AA)
    # print(rotateAngle)
    # print("_________________________________________________")
    cv2.arrowedLine(oriImage, (int(middlePoint[0]), int(middlePoint[1])), (int(directionEnd[0]), int(directionEnd[1])),
                    (0, 255, 255), 30, tipLength=0.2)

    cv2.circle(oriImage, (int(middlePoint[0]), int(middlePoint[1])), 30, (0, 255, 255), 3)
    # print(middlePoint[0], rightVertex, bottomVertex, middlePoint)

    return rotateAngle, oriImage
    # return oriImage
    # Mask才是影像二階之後
    # cv2.imshow('Result', oriImage)
    # cv2.imshow('Canny', canny)
    # cv2.waitKey(0)
