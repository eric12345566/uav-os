import multiprocessing as mp
from multiprocessing.managers import BaseManager
import time

# Process
import process.ControllerProcess as ctrp
import process.FrameProcess as fp
import process.AutoFlightProcess as afp
import process.terminalProcess as tp
# import process.CarSocketServerProcess as cssp
import process.MarkedFrameProcess as mfp

# Class
from classes.FrameClass import FrameClass

# Service
from service.terminalService import terminalService
from service.OSStateService import OSStateService
from service.UAVSocketService import UAVSocketService
from service.FlightCmdService import FlightCmdService

if __name__ == '__main__':
    # record started time
    startTime = time.time()

    '''註冊資料類別
    '''
    BaseManager.register('terminalService', terminalService)
    BaseManager.register('frameClass', FrameClass)
    BaseManager.register('osStateService', OSStateService)
    BaseManager.register( 'uavSocketService', UAVSocketService)
    # BaseManager.register('flightCmdService', FlightCmdService)
    manager = BaseManager()
    manager.start()

    '''共享資料
    '''
    terminalService = manager.terminalService()
    frameService = manager.frameClass()
    osStateService = manager.osStateService()
    uavSocketService = manager.uavSocketService()
    # flightCmdService = manager.flightCmdService()

    '''OS環境變數：test 狀態下不會啟動 Tello 與 openCV
        **目前所有測試，請使用Tello進行，不開放test模式**
    '''
    osStateService.setMode("dev")

    ''' 執行緒創建
    '''
    afpProcess = mp.Process(target=afp.AutoFlightProcess, args=(frameService, osStateService, terminalService, uavSocketService,))
    tpProcess = mp.Process(target=tp.terminalProcess, args=(terminalService,))
    # cssProcess = mp.Process(target=cssp.CarSocketServerProcess, args=(uavSocketService,))
    if osStateService.getMode() != "test":
        frameProcess = mp.Process(target=fp.FrameProcess, args=(frameService, osStateService,))
    else:
        frameProcess = mp.Process(target=fp.FrameProcessTest, args=(frameService, osStateService,))

    # if osStateService.getMode() != "test":
    #     # print("dev")
    #     ctrProcess = mp.Process(target=ctrp.ControllerProcess, args=(frameService, osStateService, flightCmdService,))
    # else:
    #     # print("test")
    #     ctrProcess = mp.Process(target=ctrp.controllerProcessDummy, args=(frameService, osStateService,
    #                                                                       flightCmdService,))
    ''' Start Socket
    '''
    uavSocketService.runSocket()

    ''' 開始執行緒
    '''
    tpProcess.start()
    afpProcess.start()
    # cssProcess.start()
    frameProcess.start()
    # ctrProcess.start()

    ''' 結束執行緒
    '''
    tpProcess.join()
    afpProcess.join()
    # cssProcess.join()
    frameProcess.join()
    # ctrProcess.join()

    endTime = time.time()

    print("elapsed time: ", endTime - startTime)
