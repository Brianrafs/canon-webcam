import ctypes
import ctypes.wintypes as wintypes
import os
import sys
import time
import numpy as np
from pathlib import Path

kEdsDataType_Unknown = 0
kEdsDataType_Bool = 1
kEdsDataType_Int32 = 2
kEdsDataType_Uint32 = 3
kEdsDataType_Int64 = 4
kEdsDataType_Uint64 = 5
kEdsDataType_Float = 6
kEdsDataType_String = 7

kEdsObjectKind_Release = 0x00000000
kEdsObjectKind_Camera = 0x00000001
kEdsObjectKind_Volume = 0x00000002
kEdsObjectKind_Folder = 0x00000003
kEdsObjectKind_DirectoryItem = 0x00000004
kEdsObjectKind_ImageRef = 0x00000005
kEdsObjectKind_Stream = 0x00000006
kEdsObjectKind_LiveViewImageRef = 0x00000007

kEds_PropertyID_OEM1 = 0x00000001
kEds_CameraCommand_TakePicture = 0x00000004
kEds_CameraCommand_StartEvf = 0x00000002
kEds_CameraCommand_EndEvf = 0x00000003
kEds_CameraCommand_DriveLens = 0x00000005
kEds_CameraCommand_DoLocking = 0x0000001D
kEds_CameraCommand_MovieSelectCrosshair = 0x00000027

kEds_Evf_Stream_FrameInfo = 0x00000001
kEds_Evf_Stream_ByteByByte = 0x00000002
kEds_Evf_Stream_Direct720x480 = 0x00000003
kEds_Evf_Stream_Direct720x480JPEG = 0x00000004

kEds_EvfOutputDevice_TFT = 0x00000001
kEds_EvfOutputDevice_PC = 0x00000002
kEds_PropertyID_Evf_OutputDevice = 0x00000003
kEds_PropertyID_Evf_Mode = 0x00000005
kEds_PropertyID_CameraOutput = 0x0000000F

kEds_AEMode_Movie = 0x00000013
kEds_AEMode_Bulb = 0x00000004
kEds_AEMode_Auto = 0x00000000
kEds_AEMode_Av = 0x00000002
kEds_AEMode_Tv = 0x00000001
kEds_AEMode_Manual = 0x00000003

kEds_StockWarning_None = 0x00000000
kEds_StockWarning_Critical = 0x00000001

kEds_BookmarkID_Unknown = 0x00000000
kEds_BookmarkID_Capture = 0x00000001

kEds_Err_File_NotFound = 0x00000001
kEds_Err_File_PermissionError = 0x00000002
kEds_Err_File_DiskFull = 0x00000003
kEds_Err_File_AllreadyExists = 0x00000004
kEds_Err_File_SyntaxError = 0x00000005
kEds_Err_File_WriterError = 0x00000006
kEds_Err_File_WriteProtectError = 0x00000007
kEds_Err_File_ReadError = 0x00000008
kEds_Err_File_NotImage = 0x00000009
kEds_Err_File_TooDeep = 0x0000000A
kEds_Err_File_Unavailable = 0x0000000B
kEds_Err_File_InvalidObject = 0x0000000C
kEds_Err_File_LinkError = 0x0000000D
kEds_Err_File_WouldExceedMax = 0x0000000E
kEds_Err_File_Legacy = 0x0000000F

kEds_Device_Counter = 0x00000001
kEds_Device_Changed = 0x00000002
kEds_Device_InfoChanged = 0x00000003
kEds_Device_Shutdown = 0x00000004
kEds_Device_BatteryLevelChanged = 0x00000005

kEds_ObjectEvent_VolumeAdded = 0x00000101
kEds_ObjectEvent_VolumeRemoved = 0x00000102
kEds_ObjectEvent_VolumeUpdateInfo = 0x00000103
kEds_ObjectEvent_FolderUpdateInfo = 0x00000104
kEds_ObjectEvent_DirItemCreated = 0x00000105
kEds_ObjectEvent_DirItemRemoved = 0x00000106
kEds_ObjectEvent_DirItemInfoChanged = 0x00000107
kEds_ObjectEvent_DirItemContentChanged = 0x00000108
kEds_ObjectEvent_DirItemRequestTransfer = 0x00000109
keds_ObjectEvent_DirItemRequestTransferDT = 0x0000010A
kEds_ObjectEvent_DirItemCancelled = 0x0000010B
kEds_ObjectEvent_VolumeFreeSpaceUpdated = 0x0000010C

kEds_PropertyEvent_PropertyChanged = 0x00000101
kEds_PropertyEvent_PropertyDescChanged = 0x00000102

kEds_CapEvent_ObjectAdded = 0x00000101
kEds_CapEvent_Start = 0x00000102
kEds_CapEvent_Stop = 0x00000103

kEds_PropertyID_Unknown = 0x00000000
kEds_PropertyID_ProductName = 0x00000002
kEds_PropertyID_BodyID = 0x00000003
kEds_PropertyID_LensName = 0x00000004
kEds_PropertyID_LensID = 0x00000005
kEds_PropertyID_FirmwareVersion = 0x00000006
kEds_PropertyID_BatteryLevel = 0x00000007
kEds_PropertyID_CFn = 0x00000008
kEds_PropertyID_SetElapsedTime = 0x00000009
kEds_PropertyID_OwnPlaylist = 0x0000000A
kEds_PropertyID_MyMenu = 0x0000000B
kEds_PropertyID_BatteryType = 0x0000000C
kEds_PropertyID_CFn4 = 0x0000000D
kEds_PropertyID_DateTime = 0x0000000E
kEds_PropertyID_CameraOutput = 0x0000000F
kEds_PropertyID_TvAvPositioning = 0x00000010
k_EdS_PropertyID_AEMode = 0x00000011
kEds_PropertyID_DriveMode = 0x00000012
kEds_PropertyID_ISOSpeed = 0x00000013
kEds_PropertyID_MeteringMode = 0x00000014
kEds_PropertyID_ExposureCompensation = 0x00000015
kEds_PropertyID_FlashCompensation = 0x00000016
kEds_PropertyID_AEBracket = 0x00000017
kEds_PropertyID_FlashMode = 0x00000018
kEds_PropertyID_AfMode = 0x00000019
kEds_PropertyID_WhiteBalance = 0x0000001A
kEds_PropertyID_Sharpness = 0x0000001B
kEds_PropertyID_ColorSpace = 0x0000001C
kEds_PropertyID_ToneCurve = 0x0000001D
kEds_PropertyID_Saturation = 0x0000001E
kEds_PropertyID_Brightness = 0x0000001F
kEds_PropertyID_Contrast = 0x00000020
kEds_PropertyID_Hue = 0x00000021
kEds_PropertyID_ImageQuality = 0x00000022
kEds_PropertyID_JpegQuality = 0x00000023
kEds_PropertyID_Orientation = 0x00000024
kEds_PropertyID_FocusInfo = 0x00000025
kEds_PropertyID_AttemptFocus = 0x00000026
kEds_PropertyID_WhiteBalanceShift = 0x00000027
kEds_PropertyID_DepthOfField = 0x00000028
kEds_PropertyID_PictureStyle = 0x00000029
kEds_PropertyID_Capability = 0x0000002A
kEds_PropertyID_Zoom = 0x0000002B
kEds_PropertyID_AEBracket = 0x0000002C
kEds_PropertyID_FEBBracket = 0x0000002D
kEds_PropertyID_AEBracketCount = 0x0000002E
kEds_PropertyID_MFDrive = 0x0000002F
kEds_PropertyID_WBBrakcet = 0x00000030
kEds_PropertyID_ISOBracket = 0x00000031
kEds_PropertyID_MovieParam = 0x00000032
kEds_PropertyID_PhotoEffect = 0x00000033
kEds_PropertyID_RemapLens = 0x00000034
kEds_PropertyID_LensAFswitch = 0x00000035
kEds_PropertyID_LensBarrel = 0x00000036
kEds_PropertyID_LensStabilizerMode = 0x00000037
kEds_PropertyID_LensAFMinMU = 0x00000038
kEds_PropertyID_FocusArea = 0x00000039
kEds_PropertyID_AutoFocusPoint = 0x0000003A
kEds_PropertyID_Artist = 0x0000003B
kEds_PropertyID_Copyright = 0x0000003C
kEds_PropertyID_Frame_ver = 0x0000003D
kEds_PropertyID_TempStatus = 0x0000003E
kEds_PropertyID_EvfMagnification = 0x0000003F
kEds_PropertyID_EvfBlackLevel = 0x00000040
kEds_PropertyID_EvfExposure = 0x00000041
kEds_PropertyID_DepthOfFieldPreview = 0x00000042
kEds_PropertyID_EvfColorTemp = 0x00000043
kEds_PropertyID_EvfWeather = 0x00000044
kEds_PropertyID_EvfLensAdjust = 0x00000045
kEds_PropertyID_EvfAdjust = 0x00000046
kEds_PropertyID_EvfInfoType = 0x00000047
kEds_PropertyID_CroppyByX3 = 0x00000048
kEds_PropertyID_EosScroll = 0x00000049
kEds_PropertyID_AEModeSelect = 0x0000004A
kEds_PropertyID_StroboSetting = 0x0000004B
kEds_PropertyID_LensComp = 0x0000004C
kEds_PropertyID_StroboEtfComp = 0x0000004D
kEds_PropertyID_StroboControl = 0x0000004E
kEds_PropertyID_LensDustRemoval = 0x0000004F

# Real EDSDK capture property IDs
kEds_PropertyID_AEMode = 0x00000400
kEds_PropertyID_DriveMode = 0x00000401
kEds_PropertyID_ISOSpeed = 0x00000402
kEds_PropertyID_MeteringMode = 0x00000403
kEds_PropertyID_AFMode = 0x00000404
kEds_PropertyID_Av = 0x00000405
kEds_PropertyID_Tv = 0x00000406
kEds_PropertyID_ExposureCompensation = 0x00000407
kEds_PropertyID_FlashCompensation = 0x00000408
kEds_PropertyID_FocalLength = 0x00000409
kEds_PropertyID_FocusInfo = 0x00000104

# Camera commands (real EDSDK)
kEds_CameraCommand_TakePicture = 0x00000000
kEds_CameraCommand_ExtendShutDownTimer = 0x00000001
kEds_CameraCommand_BulbStart = 0x00000002
kEds_CameraCommand_BulbEnd = 0x00000003
kEds_CameraCommand_PressShutterButton = 0x00000004
kEds_CameraCommand_DoEvfAf = 0x00000102
kEds_CameraCommand_DriveLensEvf = 0x00000103
kEds_CameraCommand_DoClickWBEvf = 0x00000104

kEdsEvfDriveLens_NEAR1 = 0x00000001
kEdsEvfDriveLens_NEAR2 = 0x00000002
kEdsEvfDriveLens_NEAR3 = 0x00000003
kEdsEvfDriveLens_FAR1 = 0x00008001
kEdsEvfDriveLens_FAR2 = 0x00008002
kEdsEvfDriveLens_FAR3 = 0x00008003

kEdsEvfAf_ON = 1
kEdsEvfAf_OFF = 0

# Value lookup tables (raw code -> human label)
ISO_TABLE = {
    0x00: "Auto", 0x18: "H", 0x28: "6", 0x30: "12", 0x38: "25",
    0x40: "50", 0x48: "100", 0x4B: "125", 0x4C: "160", 0x50: "200",
    0x53: "250", 0x54: "320", 0x58: "400", 0x5B: "500", 0x5C: "640",
    0x60: "800", 0x63: "1000", 0x64: "1250", 0x68: "1600", 0x6B: "2000",
    0x6C: "2500", 0x70: "3200", 0x73: "4000", 0x74: "5000", 0x78: "6400",
    0x7B: "8000", 0x7C: "10000", 0x80: "12800", 0x83: "16000",
    0x84: "20000", 0x88: "25600", 0x90: "51200", 0x98: "102400",
}

AV_TABLE = {
    0x08: "1", 0x0B: "1.1", 0x0E: "1.2", 0x13: "1.4", 0x14: "1.6",
    0x18: "1.8", 0x1B: "2", 0x1C: "2.2", 0x20: "2.5", 0x23: "2.8",
    0x24: "3.2", 0x28: "3.5", 0x2B: "4", 0x2E: "4.5", 0x33: "5",
    0x34: "5.6", 0x38: "6.3", 0x3B: "7.1", 0x40: "8", 0x43: "9",
    0x44: "10", 0x48: "11", 0x4B: "13", 0x50: "14", 0x53: "16",
    0x58: "18", 0x5B: "20", 0x60: "22", 0x63: "25", 0x68: "29",
    0x6B: "32", 0x70: "36", 0x73: "40", 0x78: "45", 0x7B: "51",
    0x80: "57", 0x83: "64", 0x88: "72", 0x8B: "81", 0x90: "91",
}

TV_TABLE = {
    0x0C: "30\"", 0x10: "25\"", 0x13: "20\"", 0x14: "15\"", 0x18: "13\"",
    0x1B: "10\"", 0x1C: "8\"", 0x20: "6\"", 0x23: "5\"", 0x24: "4\"",
    0x28: "3.2\"", 0x2B: "2.5\"", 0x2C: "2\"", 0x30: "1.6\"", 0x33: "1.3\"",
    0x34: "1\"", 0x38: "0.8\"", 0x3B: "0.6\"", 0x3C: "0.5\"", 0x40: "0.4\"",
    0x43: "0.3\"", 0x44: "0.25\"", 0x48: "0.2\"", 0x4B: "0.16\"",
    0x4C: "1/8", 0x50: "1/10", 0x53: "1/13", 0x54: "1/15", 0x58: "1/20",
    0x5B: "1/25", 0x5C: "1/30", 0x60: "1/40", 0x63: "1/50", 0x64: "1/60",
    0x68: "1/80", 0x6B: "1/100", 0x6C: "1/125", 0x70: "1/160",
    0x73: "1/200", 0x74: "1/250", 0x78: "1/320", 0x7B: "1/400",
    0x7C: "1/500", 0x80: "1/640", 0x83: "1/800", 0x84: "1/1000",
    0x88: "1/1250", 0x8B: "1/1600", 0x8C: "1/2000", 0x90: "1/2500",
    0x93: "1/3200", 0x94: "1/4000", 0x98: "1/5000", 0x9B: "1/6400",
    0x9C: "1/8000",
}

AEMODE_TABLE = {
    0x00: "Auto", 0x01: "Tv", 0x02: "Av", 0x03: "Manual",
    0x04: "Bulb", 0x05: "A-DEP", 0x06: "Depth of field",
    0x07: "Custom 1", 0x08: "Custom 2", 0x09: "Custom 3",
    0x0A: "Auto Depth", 0x0B: "P", 0x0C: "P(CA)", 0x0D: "SCN",
    0x0E: "Portrait", 0x0F: "Landscape", 0x10: "Close-up",
    0x11: "Sports", 0x12: "Night scene", 0x13: "Movie",
}



class EdsError(Exception):
    def __init__(self, code, message=""):
        self.code = code
        super().__init__(f"EDSDK Error 0x{code:08X}: {message}")


ERROR_MESSAGES = {
    0x00000000: "OK",
    0x00000001: "File not found",
    0x00000002: "Permission error",
    0x00000003: "Disk full",
    0x00000004: "File already exists",
    0x00000005: "File syntax error",
    0x00000006: "File write error",
    0x00000007: "File write protect",
    0x00000008: "File read error",
    0x00000009: "File not image",
    0x0000000A: "Directory too deep",
    0x0000000B: "File unavailable",
    0x0000000C: "Invalid object",
    0x0000000D: "Link error",
    0x0000000E: "Would exceed max",
    0x0000000F: "Legacy format",
    0x00000010: "Invalid device command",
    0x00000011: "Invalid parameter",
    0x00000012: "Device busy",
    0x00000013: "Device memory full",
    0x00000014: "Device internal error",
    0x00000015: "Invalid device response",
    0x00000016: "Device connection error",
    0x00000017: "Device data error",
    0x00000018: "Device unsupported",
    0x0000001A: "Transfer already started",
    0x0000001B: "Transfer not started",
    0x0000001C: "Invalid dataset",
    0x0000001D: "Invalid handle",
    0x0000001E: "Object not initialized",
    0x0000001F: "Object already initialized",
    0x00000020: "Handle already used",
    0x00000021: "Cannot set the designated state",
    0x00000022: "Invalid ref",
    0x00000023: "Invalid enum",
    0x00000024: "Invalid refererence",
    0x00000025: "No such property",
    0x00000026: "Invalid property type",
    0x00000027: "Invalid property value",
    0x00000028: "Property not available",
    0x00000029: "Property temporarily unavailable",
    0x0000002A: "Property not supported",
    0x0000002B: "Invalid property ID",
    0x0000002C: "Invalid pointer",
    0x0000002D: "Invalid length",
    0x0000002E: "Invalid data size",
    0x0000002F: "Invalid time",
    0x00000030: "Invalid capture",
    0x00000031: "Invalid interval",
    0x00000032: "Invalid region",
    0x00000033: "Invalid streak",
    0x00000034: "Invalid zoom region",
    0x00000035: "Invalid focus point",
    0x00000036: "Invalid panning region",
    0x00000037: "Invalid scene",
    0x00000038: "Invalid depth",
    0x00000040: "Internal error",
    0x00000041: "Internal memory error",
    0x00000042: "Internal error",
    0x00000043: "Internal error",
    0x00000044: "Internal error",
    0x00000045: "Internal error",
    0x00000046: "Internal error",
    0x00000047: "Internal error",
    0x00000048: "Internal error",
    0x00000049: "Internal error",
    0x00000050: "Read error",
    0x00000051: "Read error",
    0x00000052: "Read error",
    0x00000053: "Read error",
    0x00000054: "Read error",
    0x00000055: "Read error",
    0x00000056: "Read error",
    0x00000057: "Read error",
    0x00000058: "Read error",
    0x0000005F: "Read error",
    0x00000060: "Write error",
    0x00000061: "Write error",
    0x00000062: "Write error",
    0x00000063: "Write error",
    0x00000064: "Write error",
    0x00000065: "Write error",
    0x00000066: "Write error",
    0x00000067: "Write error",
    0x00000068: "Write error",
    0x0000006F: "Write error",
    0x00000070: "Shutter release failed",
    0x00000071: "Bulb photography failed",
    0x00000073: "No camera",
    0x00000080: "Not supported",
    0x00000081: "Handshake failed",
    0x00000082: "SDK lock error",
    0x00000083: "Initialization error",
    0x00000084: "Communication error",
    0x00000085: "Communication error",
    0x00000086: "Communication error",
    0x00000087: "Communication error",
    0x00000088: "Communication error",
    0x00000089: "Communication error",
    0x0000008A: "Communication error",
    0x0000008B: "Communication error",
    0x0000008C: "Communication error",
    0x0000008D: "Communication error",
    0x0000008E: "Communication error",
    0x0000008F: "Communication error",
    0x00000090: "Unknown command",
    0x00000091: "Unknown command",
    0x00000092: "Unknown command",
    0x00000093: "Unknown command",
    0x00000099: "Lock failure",
    0x0000009A: "Lock failure",
    0x0000009B: "Lock failure",
    0x0000009C: "Lock failure",
    0x0000009D: "Lock failure",
    0x0000009F: "Lock failure",
    0x000000A0: "Try again",
    0x000000A1: "Try again",
    0x000000A2: "Try again",
    0x000000A3: "Try again",
    0x000000A4: "Try again",
    0x000000A5: "Try again",
    0x000000A6: "Try again",
    0x000000A7: "Try again",
    0x000000A8: "Try again",
    0x000000A9: "Try again",
    0x000000AA: "Try again",
    0x000000AB: "Try again",
    0x000000B0: "Missing component",
    0x000000B1: "Missing component",
    0x000000B2: "Missing component",
    0x000000B3: "Missing component",
    0x000000B4: "Missing component",
    0x000000B5: "Missing component",
    0x000000B6: "Missing component",
    0x000000B7: "Missing component",
    0x000000B8: "Missing component",
    0x000000B9: "Missing component",
    0x000000C0: "Compatibility error",
    0x000000C1: "Compatibility error",
    0x000000C2: "Compatibility error",
    0x000000C3: "Compatibility error",
    0x000000C4: "Compatibility error",
    0x000000C5: "Compatibility error",
    0x000000C6: "Compatibility error",
    0x000000C7: "Compatibility error",
    0x000000C8: "Compatibility error",
    0x000000F0: "Unknown error",
    0x000000FF: "Operational error",
    0x00000100: "SDK not initialized",
    0x00000101: "Memory full",
    0x00000102: "Version error",
    0x00000103: "Not initialized",
    0x00000104: "Not loaded",
    0x00000105: "Already initialized",
    0x00000106: "Already loaded",
    0x00000107: "Invalid directory",
    0x00000108: "File already exists",
    0x00000109: "Directory not empty",
}


def check_result(result, context=""):
    if result != 0:
        msg = ERROR_MESSAGES.get(result, "Unknown error")
        raise EdsError(result, f"{context}: {msg}" if context else msg)
    return result


class EdsDirectoryItemRef(ctypes.Structure):
    _fields_ = [("ref", ctypes.c_void_p)]


class EdsStreamRef(ctypes.Structure):
    _fields_ = [("ref", ctypes.c_void_p)]


class EdsBaseRef(ctypes.Structure):
    _fields_ = [("ref", ctypes.c_void_p)]


class CanonEDSDK:
    def __init__(self):
        self._dll = None
        self._camera_ref = None
        self._live_view_active = False
        self._initialized = False
        self._find_edsdk_dll()

    def _find_edsdk_dll(self):
        search_paths = []

        project_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths.extend([
            os.path.join(project_dir, "libs", "EDSDK.dll"),
            os.path.join(project_dir, "EDSDK.dll"),
            os.path.join(project_dir, "sdktest", "EDSDK.dll"),
        ])

        if sys.platform == "win32":
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            app_data = os.environ.get("APPDATA", "")

            search_paths.extend([
                os.path.join(program_files, "Canon", "EOS Webcam Utility Pro", "EDSDK.dll"),
                os.path.join(program_files, "Canon", "EOS Webcam Utility", "EDSDK.dll"),
                os.path.join(program_files, "Canon", "EDSDK", "Library", "DLL", "EDSDK.dll"),
                os.path.join(program_files, "Canon", "EOS Utility", "EDSDK.dll"),
                os.path.join(program_files, "Canon", "EOS Utility", "bin", "EDSDK.dll"),
                os.path.join(program_files_x86, "Canon", "EDSDK", "Library", "DLL", "EDSDK.dll"),
                os.path.join(program_files_x86, "Canon", "EOS Utility", "EDSDK.dll"),
                os.path.join(program_files_x86, "Canon", "EOS Utility", "bin", "EDSDK.dll"),
                os.path.join(program_files_x86, "Canon", "EOS Webcam Utility", "EDSDK.dll"),
                os.path.join(app_data, "Canon", "EDSDK", "EDSDK.dll"),
            ])

            for path in Path(program_files).rglob("EDSDK.dll"):
                search_paths.append(str(path))
            for path in Path(program_files_x86).rglob("EDSDK.dll"):
                search_paths.append(str(path))

        for path in search_paths:
            if os.path.exists(path):
                try:
                    self._dll = ctypes.WinDLL(path)
                    print(f"[EDSDK] DLL found: {path}")
                    return
                except OSError:
                    continue

        raise FileNotFoundError(
            "Canon EDSDK.dll not found. Please install Canon EOS Utility "
            "or download the Canon EDSDK from Canon's developer website.\n"
            f"Searched paths:\n" + "\n".join(f"  - {p}" for p in search_paths[:10])
        )

    def _setup_functions(self):
        dll = self._dll
        self._available_functions = set()

        def setup_func(name, restype=None, argtypes=None):
            try:
                func = getattr(dll, name)
                if restype is not None:
                    func.restype = restype
                if argtypes is not None:
                    func.argtypes = argtypes
                self._available_functions.add(name)
                return True
            except AttributeError:
                return False

        setup_func("EdsInitializeSDK", ctypes.c_uint32, [])
        setup_func("EdsTerminateSDK", ctypes.c_uint32, [])
        setup_func("EdsGetCameraList", ctypes.c_uint32, [ctypes.POINTER(ctypes.c_void_p)])
        setup_func("EdsGetChildCount", ctypes.c_uint32, [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)])
        setup_func("EdsGetChildAtIndex", ctypes.c_uint32, [ctypes.c_void_p, ctypes.c_int32, ctypes.POINTER(ctypes.c_void_p)])
        setup_func("EdsOpenSession", ctypes.c_uint32, [ctypes.c_void_p])
        setup_func("EdsCloseSession", ctypes.c_uint32, [ctypes.c_void_p])
        setup_func("EdsRelease", ctypes.c_uint32, [ctypes.c_void_p])
        setup_func("EdsSendCommand", ctypes.c_uint32, [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int32])
        setup_func("EdsSendStatusCommand", ctypes.c_uint32, [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int32])
        setup_func("EdsGetPropertySize", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int32,
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)
        ])
        setup_func("EdsGetPropertyData", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int32,
            ctypes.c_uint32, ctypes.c_void_p
        ])
        setup_func("EdsSetPropertyData", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int32,
            ctypes.c_uint32, ctypes.c_void_p
        ])
        setup_func("EdsCreateEvfImageRef", ctypes.c_uint32, [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)])
        setup_func("EdsGetPointer", ctypes.c_uint32, [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)])
        setup_func("EdsGetLength", ctypes.c_uint32, [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)])
        setup_func("EdsGetEvfImageSize", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)
        ])
        setup_func("EdsCreateMemoryStream", ctypes.c_uint32, [ctypes.c_int64, ctypes.POINTER(ctypes.c_void_p)])
        setup_func("EdsGetDirectoryItemSize", ctypes.c_uint32, [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)])
        setup_func("EdsGetDirectoryItemData", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)
        ])
        setup_func("EdsSetEventHandler", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p
        ])
        setup_func("EdsSetCameraAddedHandler", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.c_void_p
        ])
        setup_func("EdsSetObjectEventHandler", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p
        ])
        setup_func("EdsSetPropertyEventHandler", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p
        ])
        setup_func("EdsSetCameraStateEventHandler", ctypes.c_uint32, [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p
        ])
        if not hasattr(self, "_callback_refs"):
            self._callback_refs = []

    def initialize(self):
        if self._initialized:
            return
        self._setup_functions()
        result = self._dll.EdsInitializeSDK()
        check_result(result, "Initialize SDK")
        self._initialized = True
        print("[EDSDK] SDK initialized")

    def terminate(self):
        if not self._initialized:
            return
        self.stop_live_view()
        if self._camera_ref:
            self._dll.EdsCloseSession(self._camera_ref)
            self._dll.EdsRelease(self._camera_ref)
            self._camera_ref = None
        self._dll.EdsTerminateSDK()
        self._initialized = False
        print("[EDSDK] SDK terminated")

    def get_camera_list(self):
        camera_list = ctypes.c_void_p()
        result = self._dll.EdsGetCameraList(ctypes.byref(camera_list))
        check_result(result, "Get camera list")

        count = ctypes.c_uint32(0)
        result = self._dll.EdsGetChildCount(camera_list, ctypes.byref(count))
        check_result(result, "Get camera count")

        cameras = []
        for i in range(count.value):
            camera_ref = ctypes.c_void_p()
            result = self._dll.EdsGetChildAtIndex(camera_list, i, ctypes.byref(camera_ref))
            check_result(result, f"Get camera at index {i}")

            product_name = self._get_string_property(camera_ref, kEds_PropertyID_ProductName)
            body_id = self._get_string_property(camera_ref, kEds_PropertyID_BodyID)

            cameras.append({
                "ref": camera_ref,
                "name": product_name or f"Canon Camera {i}",
                "body_id": body_id or "Unknown",
            })

        self._dll.EdsRelease(camera_list)
        return cameras

    def _get_string_property(self, camera_ref, property_id):
        try:
            size = ctypes.c_uint32(0)
            data_type = ctypes.c_uint32(0)
            result = self._dll.EdsGetPropertySize(
                camera_ref, property_id, 0,
                ctypes.byref(data_type), ctypes.byref(size)
            )
            if result != 0:
                return None

            if size.value == 0:
                return None

            buffer = ctypes.create_string_buffer(size.value)
            result = self._dll.EdsGetPropertyData(
                camera_ref, property_id, 0,
                size.value, buffer
            )
            if result != 0:
                return None

            return buffer.value.decode("utf-8", errors="replace").rstrip("\x00")
        except Exception:
            return None

    def _get_int_property(self, camera_ref, property_id):
        try:
            size = ctypes.c_uint32(0)
            data_type = ctypes.c_uint32(0)
            result = self._dll.EdsGetPropertySize(
                camera_ref, property_id, 0,
                ctypes.byref(data_type), ctypes.byref(size)
            )
            if result != 0:
                return None

            if size.value == 0:
                return None

            value = ctypes.c_uint32(0)
            result = self._dll.EdsGetPropertyData(
                camera_ref, property_id, 0,
                size.value, ctypes.byref(value)
            )
            if result != 0:
                return None

            return value.value
        except Exception:
            return None

    def connect(self, camera_index=0):
        cameras = self.get_camera_list()
        if not cameras:
            raise EdsError(0, "No Canon cameras found. Make sure the camera is connected via USB and turned on.")

        if camera_index >= len(cameras):
            camera_index = 0

        camera = cameras[camera_index]
        self._camera_ref = camera["ref"]

        result = self._dll.EdsOpenSession(self._camera_ref)
        check_result(result, "Open session")

        print(f"[EDSDK] Connected to: {camera['name']} ({camera['body_id']})")
        return camera["name"]

    def get_property_u32(self, property_id, default=None):
        return self._get_int_property(self._camera_ref, property_id) if self._camera_ref else default

    def set_property_u32(self, property_id, value):
        if not self._camera_ref:
            return 0x00000002
        v = ctypes.c_uint32(value)
        return self._dll.EdsSetPropertyData(self._camera_ref, property_id, 0, 4, ctypes.byref(v))

    def get_property_desc(self, property_id):
        if not self._camera_ref:
            return []
        class PropDesc(ctypes.Structure):
            _fields_ = [
                ("PropID", ctypes.c_uint32),
                ("form", ctypes.c_int),
                ("numElements", ctypes.c_uint32),
                ("numElementsData", ctypes.c_uint32),
                ("PropDesc", ctypes.c_uint32 * 128),
            ]
        d = PropDesc()
        r = self._dll.EdsGetPropertyDesc(self._camera_ref, property_id, ctypes.byref(d))
        if r != 0:
            return []
        return list(d.PropDesc[: d.numElements]) if d.numElements <= 128 else []

    def get_label_for(self, property_id, value, table):
        label = table.get(value)
        return label if label is not None else f"0x{value:04X}"

    def auto_focus(self, mode=kEdsEvfAf_ON):
        if not self._camera_ref:
            return 0x00000002
        return self._dll.EdsSendCommand(self._camera_ref, kEds_CameraCommand_DoEvfAf, mode)

    def drive_lens(self, direction):
        if not self._camera_ref:
            return 0x00000002
        return self._dll.EdsSendCommand(self._camera_ref, kEds_CameraCommand_DriveLensEvf, direction)

    def extend_shutdown_timer(self):
        if not self._camera_ref:
            return 0x00000002
        return self._dll.EdsSendCommand(self._camera_ref, kEds_CameraCommand_ExtendShutDownTimer, 0)

    def take_photo(self):
        if not self._camera_ref:
            return 0x00000002
        return self._dll.EdsSendCommand(self._camera_ref, kEds_CameraCommand_TakePicture, 0)

    def disconnect(self):
        if self._camera_ref:
            self.stop_live_view()
            self._dll.EdsCloseSession(self._camera_ref)
            self._dll.EdsRelease(self._camera_ref)
            self._camera_ref = None
            print("[EDSDK] Disconnected")

    def start_live_view(self):
        if not self._camera_ref:
            raise EdsError(0, "No camera connected")

        if "EdsSetPropertyData" in self._available_functions:
            output_device = ctypes.c_uint32(kEds_EvfOutputDevice_PC)
            result = self._dll.EdsSetPropertyData(
                self._camera_ref,
                kEds_PropertyID_Evf_OutputDevice,
                0,
                ctypes.sizeof(output_device),
                ctypes.byref(output_device)
            )
            if result != 0:
                print(f"[EDSDK] WARNING: set EVF output device failed: 0x{result:08X}")

        last_error = None
        for attempt in range(3):
            result = self._dll.EdsSendCommand(
                self._camera_ref,
                kEds_CameraCommand_StartEvf,
                0
            )
            if result == 0:
                self._live_view_active = True
                time.sleep(0.2)
                print("[EDSDK] Live View started")
                return
            last_error = result
            print(f"[EDSDK] Start Live View attempt {attempt + 1} failed: 0x{result:08X} (retrying)")
            time.sleep(0.3)

        check_result(last_error, "Start Live View")

    def stop_live_view(self):
        if not self._camera_ref or not self._live_view_active:
            return

        result = self._dll.EdsSendCommand(
            self._camera_ref,
            kEds_CameraCommand_EndEvf,
            0
        )
        if result == 0:
            self._live_view_active = False
            print("[EDSDK] Live View stopped")

    def capture_live_view_frame(self):
        if not self._camera_ref or not self._live_view_active:
            return None

        try:
            evf_image_ref = ctypes.c_void_p()
            result = self._dll.EdsCreateEvfImageRef(self._camera_ref, ctypes.byref(evf_image_ref))
            if result != 0:
                return None

            stream_ref = ctypes.c_void_p()
            result = self._dll.EdsGetChildAtIndex(evf_image_ref, 0, ctypes.byref(stream_ref))
            if result != 0:
                self._dll.EdsRelease(evf_image_ref)
                return None

            pointer = ctypes.c_void_p()
            result = self._dll.EdsGetPointer(stream_ref, ctypes.byref(pointer))
            if result != 0:
                self._dll.EdsRelease(stream_ref)
                self._dll.EdsRelease(evf_image_ref)
                return None

            length = ctypes.c_uint32(0)
            result = self._dll.EdsGetLength(stream_ref, ctypes.byref(length))
            if result != 0:
                self._dll.EdsRelease(stream_ref)
                self._dll.EdsRelease(evf_image_ref)
                return None

            if length.value == 0:
                self._dll.EdsRelease(stream_ref)
                self._dll.EdsRelease(evf_image_ref)
                return None

            jpeg_data = ctypes.string_at(pointer, length.value)

            self._dll.EdsRelease(stream_ref)
            self._dll.EdsRelease(evf_image_ref)

            import cv2
            import numpy as np
            nparr = np.frombuffer(jpeg_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame

        except Exception as e:
            print(f"[EDSDK] Live View capture error: {e}")
            return None

    def set_live_view_zoom(self, zoom):
        if not self._camera_ref:
            return
        self._dll.EdsSendCommand(
            self._camera_ref,
            0x00000007,
            zoom
        )

    def get_battery_level(self):
        if not self._camera_ref:
            return None
        return self._get_int_property(self._camera_ref, kEds_PropertyID_BatteryLevel)

    def get_camera_name(self):
        if not self._camera_ref:
            return "No camera"
        name = self._get_string_property(self._camera_ref, kEds_PropertyID_ProductName)
        return name or "Canon Camera"
