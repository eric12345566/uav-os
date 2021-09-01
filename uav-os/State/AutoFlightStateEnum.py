from enum import Enum


class AutoFlightState(Enum):
    INIT = "init"
    READY_TAKEOFF = "ready_takeoff"
    AUTO_LANDING = "auto_landing"
    FORCE_LANDING = "force_landing"
    LANDED = "landed"
    YAW_ALIGN = "yaw_align"
    FINDING_ARUCO = "finding_marker"
    END = "end"

    # TEST MODE
    TEST_MODE = "test_mode"

    KEYBOARD_CONTROL = "keyboard_control"
