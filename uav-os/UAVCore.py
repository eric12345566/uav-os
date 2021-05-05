import multiprocessing as mp
from multiprocessing.managers import BaseManager
import time

# Process
import process.ControllerProcess as ctrp
import process.FrameProcess as fp
import process.AutoFlightProcess as afp

# Class
from classes.FrameClass import FrameClass

# Service
from service.OSStateService import StateService

if __name__ == '__main__':
    # record started time
    startTime = time.time()

    '''註冊資料類別
    '''
    # 註冊共享類別
    BaseManager.register('frameClass', FrameClass)
    BaseManager.register('stateService', StateService)
    manager = BaseManager()
    manager.start()
    # lock = mp.Lock()

    '''共享資料
    '''
    # frameObj = manager.frameClass()
    telloFrame = manager.frameClass()
    stateService = manager.stateService()

    ''' 執行緒創建
    '''
    # 創建執行緒
    # afpProcess = mp.Process(target=afp.autoFlightProcess, args=(telloFrame, stateService))
    ctrProcess = mp.Process(target=ctrp.controllerProcess, args=(telloFrame, stateService,))
    # ctrProcess = mp.Process(target=ctrp.controllerProcessDummy, args=())
    frameProcess = mp.Process(target=fp.frameProcess, args=(telloFrame, stateService, ))

    # 開始執行緒
    # afpProcess.start()
    frameProcess.start()
    ctrProcess.start()

    # 結束執行緒
    # afpProcess.join()
    frameProcess.join()
    ctrProcess.join()

    endTime = time.time()

    print("elapsed time: ", endTime - startTime)
