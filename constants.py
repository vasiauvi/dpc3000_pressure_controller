"""Constants file"""
# -----------------------------
# DPC3000 COMMANDS LIST
# -----------------------------
CHECK = "@check\r"
READPRESS = "@ReadPress:bar\r"
SETPRESS = "@SetPress:"
STOP = "@Stop\r"
VENT = "@Vent\r"
TICKPRESS = "@TickPress\r"  # ErrUnknCmd
TICKVAC = "@TickVac\r"
READMODE = "@ReadMode\r"
SETMODE = "@SetMode:"  # SetMode:{Mode} Control, Measure, Vent
READSTATUS = "@ReadStatus\r"
READSTATUS_BIN = "@ReadStatus:bin\r"
PRECISSION = 0.1  # bar

# -----------------------------
# DPC3000 error codes
# -----------------------------
PRESS_ERRORCODES = {
    "CER": "Communication Error",
    "PER": "Parameter Error",
    "VER": "Value Error",
    "TER": "Timeout",
    "FER": "Format Error",
    "SER": "Command Error",
    "ErrUnknCmd": "Unknown Command",
    "ErrFunction": "Error Function",
    "ErrParameter": "Parameter Error",
}
PRESS_ERRORS = [
    "CER",
    "PER",
    "VER",
    "TER",
    "FER",
    "SER",
    "ErrUnknCmd",
    "ErrFunction",
    "ErrParameter",
]
MODES = ["Control", "Measure", "Vent"]
# -----------------------------
# DPC3000 status
# -----------------------------
PRESS_STATUS = {
    1: "Pressure is within the tolerance band",
    2: "Fine control (PI control) completed",
    4: "Coarse control completed",
    8: "Venting valve is open",
    16: "Controller is in overload state",
    32: "Zero offset compensation is active",
    64: "Controller timeout",
    128: "Controller is in stop state",
}

# -----------------------------
