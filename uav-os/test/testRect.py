import numpy as np
rect = [[[485, 336]], [[548, 340]], [[544, 404]], [[481, 400]]]

rect = np.array(rect)

scaleUpValue = 30
scaleUpDirArray = [(False, False), (True, False), (True, True), (False, True)]

rectNew = np.copy(rect)

for i in range(0, 4):
    firstDir, secondDir = scaleUpDirArray[i]
    # print(rectNew[i][0])
    if firstDir:
        rectNew[i][0][0] += scaleUpValue
    else:
        rectNew[i][0][0] -= scaleUpValue

    if secondDir:
        rectNew[i][0][1] += scaleUpValue
    else:
        rectNew[i][0][1] -= scaleUpValue

    if rectNew[i][0][0] < 0:
        rectNew[i][0][0] = 0

    if rectNew[i][0][1] < 0:
        rectNew[i][0][1] = 0

print(rect)
print(rectNew)
