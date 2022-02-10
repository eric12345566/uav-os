import math


def angleBtw2Points(pointA, pointB):
    xA, yA = pointA
    xB, yB = pointB
    changeInX = xB - xA
    changeInY = yB - yA
    return math.degrees(math.atan2(changeInY, changeInX))


if __name__ == '__main__':
    print(angleBtw2Points([2, 2], [4, 0]))
