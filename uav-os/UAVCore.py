import multiprocessing as mp
import time
import process.controllerProcess as ctrp
import process.frameProcess as fp

if __name__ == '__main__':
    # record started time
    startTime = time.time()
    arr1 = mp.Array('d', [[1, 2, 3], 4])
    # init
    ctrProcess = mp.Process(target=ctrp.controllerProcess, args=('hello controller', arr1,))
    frameProcess = mp.Process(target=fp.frameProcess, args=(arr1,))

    ctrProcess.start()
    frameProcess.start()

    ctrProcess.join()
    frameProcess.join()

    endTime = time.time()

    print("elapsed time: ", endTime - startTime)
