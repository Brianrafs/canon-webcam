"""Constantes do Canon EDSDK (Windows, ctypes).

Mantém os mesmos valores usados pela lógica testada, apenas reorganizados
por seção: tipos, objetos, comandos, eventos, propriedades e AE modes.
"""

# --- Data types -------------------------------------------------------
kEdsDataType_Unknown = 0
kEdsDataType_Bool = 1
kEdsDataType_Int32 = 2
kEdsDataType_Uint32 = 3
kEdsDataType_Int64 = 4
kEdsDataType_Uint64 = 5
kEdsDataType_Float = 6
kEdsDataType_String = 7

# --- Object kinds -----------------------------------------------------
kEdsObjectKind_Release = 0x00000000
kEdsObjectKind_Camera = 0x00000001
kEdsObjectKind_Volume = 0x00000002
kEdsObjectKind_Folder = 0x00000003
kEdsObjectKind_DirectoryItem = 0x00000004
kEdsObjectKind_ImageRef = 0x00000005
kEdsObjectKind_Stream = 0x00000006
kEdsObjectKind_LiveViewImageRef = 0x00000007

# --- Camera commands --------------------------------------------------
kEds_CameraCommand_TakePicture = 0x00000000
kEds_CameraCommand_ExtendShutDownTimer = 0x00000001
kEds_CameraCommand_BulbStart = 0x00000002
kEds_CameraCommand_BulbEnd = 0x00000003
kEds_CameraCommand_PressShutterButton = 0x00000004
kEds_CameraCommand_StartEvf = 0x00000002
kEds_CameraCommand_EndEvf = 0x00000003
kEds_CameraCommand_DriveLens = 0x00000005
kEds_CameraCommand_DoLocking = 0x0000001D
kEds_CameraCommand_MovieSelectCrosshair = 0x00000027
kEds_CameraCommand_DoEvfAf = 0x00000102
kEds_CameraCommand_DriveLensEvf = 0x00000103
kEds_CameraCommand_DoClickWBEvf = 0x00000104

# --- Live View drivers ------------------------------------------------
kEdsEvfDriveLens_NEAR1 = 0x00000001
kEdsEvfDriveLens_NEAR2 = 0x00000002
kEdsEvfDriveLens_NEAR3 = 0x00000003
kEdsEvfDriveLens_FAR1 = 0x00008001
kEdsEvfDriveLens_FAR2 = 0x00008002
kEdsEvfDriveLens_FAR3 = 0x00008003

kEdsEvfAf_ON = 1
kEdsEvfAf_OFF = 0

# --- EVF streams ------------------------------------------------------
kEds_Evf_Stream_FrameInfo = 0x00000001
kEds_Evf_Stream_ByteByByte = 0x00000002
kEds_Evf_Stream_Direct720x480 = 0x00000003
kEds_Evf_Stream_Direct720x480JPEG = 0x00000004

# --- EVF / output devices ---------------------------------------------
kEds_EvfOutputDevice_TFT = 0x00000001
kEds_EvfOutputDevice_PC = 0x00000002
kEds_PropertyID_Evf_OutputDevice = 0x00000003
kEds_PropertyID_Evf_Mode = 0x00000005
kEds_PropertyID_CameraOutput = 0x0000000F

# --- AE modes ----------------------------------------------------------
kEds_AEMode_Movie = 0x00000013
kEds_AEMode_Bulb = 0x00000004
kEds_AEMode_Auto = 0x00000000
kEds_AEMode_Av = 0x00000002
kEds_AEMode_Tv = 0x00000001
kEds_AEMode_Manual = 0x00000003

# --- Stock / bookmark --------------------------------------------------
kEds_StockWarning_None = 0x00000000
kEds_StockWarning_Critical = 0x00000001
kEds_BookmarkID_Unknown = 0x00000000
kEds_BookmarkID_Capture = 0x00000001

# --- File errors -------------------------------------------------------
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

# --- Device events -----------------------------------------------------
kEds_Device_Counter = 0x00000001
kEds_Device_Changed = 0x00000002
kEds_Device_InfoChanged = 0x00000003
kEds_Device_Shutdown = 0x00000004
kEds_Device_BatteryLevelChanged = 0x00000005

# --- Object events -----------------------------------------------------
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

# --- Property events ---------------------------------------------------
kEds_PropertyEvent_PropertyChanged = 0x00000101
kEds_PropertyEvent_PropertyDescChanged = 0x00000102

# --- Capture events ----------------------------------------------------
kEds_CapEvent_ObjectAdded = 0x00000101
kEds_CapEvent_Start = 0x00000102
kEds_CapEvent_Stop = 0x00000103

# --- Info property IDs (idades of camera info) ------------------------
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
kEds_PropertyID_DriveMode = 0x00000012
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
kEds_PropertyID_MFDrive = 0x0000002F
kEds_PropertyID_MovieParam = 0x00000032
kEds_PropertyID_PhotoEffect = 0x00000033
kEds_PropertyID_TempStatus = 0x0000003E
kEds_PropertyID_EvfMagnification = 0x0000003F

# --- Real EDSDK capture property IDs ----------------------------------
kEds_PropertyID_AEMode = 0x00000400
kEds_PropertyID_DriveMode = 0x00000401
kEds_PropertyID_ISOSpeed = 0x00000402
kEds_PropertyID_MeteringMode = 0x00000403
kEds_PropertyID_AFMode = 0x00000404
kEds_PropertyID_Av = 0x00000405
kEds_PropertyID_Tv = 0x00000406
kEds_PropertyID_ExposureCompensation = 0x00000407

# --- AE mode lookup ----------------------------------------------------
AEMODE_TABLE = {
    0x00: "Auto", 0x01: "Tv", 0x02: "Av", 0x03: "Manual",
    0x04: "Bulb", 0x05: "A-DEP", 0x06: "Depth of field",
    0x07: "Custom 1", 0x08: "Custom 2", 0x09: "Custom 3",
    0x0A: "Auto Depth", 0x0B: "P", 0x0C: "P(CA)", 0x0D: "SCN",
    0x0E: "Portrait", 0x0F: "Landscape", 0x10: "Close-up",
    0x11: "Sports", 0x12: "Night scene", 0x13: "Movie",
}