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
from service.OSStateService import OSStateService
from service.FlightCmdService import FlightCmdService

if __name__ == '__main__':
    # record started time
    startTime = time.time()

    '''註冊資料類別
    '''
    # 註冊共享類別
    BaseManager.register('frameClass', FrameClass)
    BaseManager.register('osStateService', OSStateService)
    BaseManager.register('flightCmdService', FlightCmdService)
    manager = BaseManager()
    manager.start()

    '''共享資料
    '''
    # frameObj = manager.frameClass()
    telloFrame = manager.frameClass()
    osStateService = manager.osStateService()
    flightCmdService = manager.flightCmdService()

    '''OS環境變數
    '''
    osStateService.setMode("dev")

    ''' 執行緒創建
    '''
    # 創建執行緒
    afpProcess = mp.Process(target=afp.AutoFlightProcess, args=(telloFrame, osStateService, flightCmdService,))
    frameProcess = mp.Process(target=fp.FrameProcess, args=(telloFrame, osStateService,))

    if osStateService.getMode() != "test":
        print("dev")
        ctrProcess = mp.Process(target=ctrp.ControllerProcess, args=(telloFrame, osStateService, flightCmdService,))
    else:
        print("test")
        ctrProcess = mp.Process(target=ctrp.controllerProcessDummy, args=(telloFrame, osStateService, flightCmdService,))

    # 開始執行緒
    afpProcess.start()
    frameProcess.start()
    ctrProcess.start()

    # 結束執行緒
    afpProcess.join()
    frameProcess.join()
    ctrProcess.join()

    endTime = time.time()

    print("elapsed time: ", endTime - startTime)
