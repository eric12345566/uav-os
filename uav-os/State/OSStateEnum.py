from enum import Enum


class OSState(Enum):
    INITIALIZING = 'initializing'
    READY = 'ready'
    AUTO_FLIGHT = 'auto_flight'
    ERROR = 'error'
    EXITING = 'exiting'
