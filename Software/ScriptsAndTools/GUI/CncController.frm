VERSION 5.00
Object = "{831FDD16-0C5C-11D2-A9FC-0000F8754DA1}#2.0#0"; "mscomctl.ocx"
Begin VB.Form frmMain 
   Caption         =   "PrinterCnc Controller - <https://github.com/cdhigh>"
   ClientHeight    =   8760
   ClientLeft      =   120
   ClientTop       =   510
   ClientWidth     =   11220
   LinkTopic       =   "Form1"
   ScaleHeight     =   8760
   ScaleWidth      =   11220
   StartUpPosition =   2  '屏幕中心
   Tag             =   "p@protocol=WM_DELETE_WINDOW@icon=app_icon.gif"
   Begin VB.TextBox txtExcellonFile 
      Height          =   375
      Left            =   1920
      TabIndex        =   92
      Top             =   600
      Width           =   8415
   End
   Begin VB.CommandButton cmdExcellonFile 
      Caption         =   "..."
      Height          =   375
      Left            =   10440
      TabIndex        =   91
      Top             =   600
      Width           =   615
   End
   Begin VB.Frame frmStatus 
      Height          =   975
      Left            =   120
      TabIndex        =   87
      Top             =   6720
      Width           =   5415
      Begin VB.Label lblQueueCmdNum 
         Caption         =   "剩余命令：0"
         Height          =   375
         Left            =   360
         TabIndex        =   89
         Top             =   240
         Width           =   2055
      End
      Begin VB.Label lblTimeToFinish 
         Caption         =   "预计剩余时间：00:00:00"
         Height          =   375
         Left            =   2640
         TabIndex        =   88
         Top             =   240
         Width           =   2415
      End
   End
   Begin MSComctlLib.TabStrip tabMachine 
      Height          =   2655
      Left            =   120
      TabIndex        =   86
      Top             =   1200
      Width           =   5415
      _ExtentX        =   9551
      _ExtentY        =   4683
      _Version        =   393216
      BeginProperty Tabs {1EFB6598-857C-11D1-B16A-00C0F0283628} 
         NumTabs         =   1
         BeginProperty Tab1 {1EFB659A-857C-11D1-B16A-00C0F0283628} 
            ImageVarType    =   2
         EndProperty
      EndProperty
   End
   Begin VB.Frame tabMachine__Tab2 
      Caption         =   "控制板参数"
      Height          =   2415
      Left            =   5880
      TabIndex        =   73
      Top             =   8760
      Width           =   5415
      Begin VB.TextBox txtPenWidth 
         Height          =   375
         Left            =   4200
         TabIndex        =   84
         Text            =   "0.6"
         Top             =   720
         Width           =   975
      End
      Begin VB.TextBox txtZLiftSteps 
         Height          =   375
         Left            =   4200
         TabIndex        =   82
         Text            =   "130"
         Top             =   240
         Width           =   975
      End
      Begin VB.TextBox txtYBacklash 
         Height          =   375
         Left            =   1920
         TabIndex        =   80
         Text            =   "0"
         Top             =   1680
         Width           =   975
      End
      Begin VB.TextBox txtYStepsPerCm 
         Height          =   375
         Left            =   1920
         TabIndex        =   78
         Text            =   "1886"
         Top             =   1200
         Width           =   975
      End
      Begin VB.TextBox txtXBacklash 
         Height          =   375
         Left            =   1920
         TabIndex        =   76
         Text            =   "94"
         Top             =   720
         Width           =   975
      End
      Begin VB.TextBox txtXStepsPerCm 
         Height          =   375
         Left            =   1920
         TabIndex        =   74
         Text            =   "1886"
         Top             =   240
         Width           =   975
      End
      Begin VB.Label lblPenWidth 
         Alignment       =   1  'Right Justify
         Caption         =   "笔尖直径"
         Height          =   255
         Left            =   3120
         TabIndex        =   85
         Top             =   720
         Width           =   855
      End
      Begin VB.Label lblZLiftSteps 
         Alignment       =   1  'Right Justify
         Caption         =   "Z轴升起"
         Height          =   255
         Left            =   3120
         TabIndex        =   83
         Top             =   240
         Width           =   855
      End
      Begin VB.Label lblYBacklash 
         Alignment       =   1  'Right Justify
         Caption         =   "Y轴回差"
         Height          =   255
         Left            =   360
         TabIndex        =   81
         Top             =   1680
         Width           =   1455
      End
      Begin VB.Label lblYStepsPerCm 
         Alignment       =   1  'Right Justify
         Caption         =   "Y轴每CM步进数"
         Height          =   255
         Left            =   360
         TabIndex        =   79
         Top             =   1200
         Width           =   1455
      End
      Begin VB.Label lblXBacklash 
         Alignment       =   1  'Right Justify
         Caption         =   "X轴回差"
         Height          =   255
         Left            =   360
         TabIndex        =   77
         Top             =   720
         Width           =   1455
      End
      Begin VB.Label lblXStepsPerCm 
         Alignment       =   1  'Right Justify
         Caption         =   "X轴每CM步进数"
         Height          =   255
         Left            =   360
         TabIndex        =   75
         Top             =   240
         Width           =   1455
      End
   End
   Begin VB.Frame tabMachine__Tab1 
      Caption         =   "轴速度（越小越快）"
      Height          =   2415
      Left            =   240
      TabIndex        =   59
      Top             =   8760
      Width           =   5415
      Begin VB.CommandButton cmdApplyAxisSpeed 
         Caption         =   "应用"
         Height          =   375
         Left            =   1560
         TabIndex        =   72
         Top             =   1800
         Width           =   2175
      End
      Begin VB.TextBox txtAcceleration 
         Height          =   375
         Left            =   3960
         TabIndex        =   70
         Text            =   "100"
         Top             =   1200
         Width           =   1215
      End
      Begin VB.TextBox txtXMaxSpeed 
         Height          =   375
         Left            =   3960
         TabIndex        =   67
         Text            =   "50"
         Top             =   240
         Width           =   1215
      End
      Begin VB.TextBox txtYMaxSpeed 
         Height          =   375
         Left            =   3960
         TabIndex        =   66
         Text            =   "50"
         Top             =   720
         Width           =   1215
      End
      Begin VB.TextBox txtXSpeed 
         Height          =   375
         Left            =   1320
         TabIndex        =   62
         Text            =   "100"
         Top             =   240
         Width           =   1215
      End
      Begin VB.TextBox txtYSpeed 
         Height          =   375
         Left            =   1320
         TabIndex        =   61
         Text            =   "120"
         Top             =   720
         Width           =   1215
      End
      Begin VB.TextBox txtZSpeed 
         Height          =   375
         Left            =   1320
         TabIndex        =   60
         Text            =   "80"
         Top             =   1200
         Width           =   1215
      End
      Begin VB.Label lblAcceleration 
         Alignment       =   1  'Right Justify
         Caption         =   "加速度"
         Height          =   255
         Left            =   2760
         TabIndex        =   71
         Top             =   1200
         Width           =   975
      End
      Begin VB.Label lblXMaxSpeed 
         Alignment       =   1  'Right Justify
         Caption         =   "X轴最快"
         Height          =   255
         Left            =   2760
         TabIndex        =   69
         Top             =   240
         Width           =   975
      End
      Begin VB.Label lblYMaxSpeed 
         Alignment       =   1  'Right Justify
         Caption         =   "Y轴最快"
         Height          =   255
         Left            =   2760
         TabIndex        =   68
         Top             =   720
         Width           =   975
      End
      Begin VB.Label lblXSpeed 
         Alignment       =   1  'Right Justify
         Caption         =   "X轴速度"
         Height          =   255
         Left            =   120
         TabIndex        =   65
         Top             =   240
         Width           =   975
      End
      Begin VB.Label lblYSpeed 
         Alignment       =   1  'Right Justify
         Caption         =   "Y轴速度"
         Height          =   255
         Left            =   120
         TabIndex        =   64
         Top             =   720
         Width           =   975
      End
      Begin VB.Label lblZSpeed 
         Alignment       =   1  'Right Justify
         Caption         =   "Z轴速度"
         Height          =   255
         Left            =   120
         TabIndex        =   63
         Top             =   1200
         Width           =   975
      End
   End
   Begin VB.Frame tabPosition__Tab3 
      Caption         =   "其他配置"
      Height          =   2415
      Left            =   11520
      TabIndex        =   54
      Top             =   5280
      Width           =   5415
      Begin VB.CheckBox chkSortCommands 
         Caption         =   "排序绘图命令"
         Height          =   255
         Left            =   360
         TabIndex        =   90
         Top             =   1320
         Value           =   1  'Checked
         Width           =   2055
      End
      Begin VB.CheckBox chkOmitRegionCmd 
         Caption         =   "忽略区域绘图命令"
         Height          =   255
         Left            =   360
         TabIndex        =   58
         Top             =   840
         Width           =   2055
      End
      Begin VB.CheckBox chkForceHole 
         Caption         =   "强制所有焊盘开孔"
         Height          =   255
         Left            =   360
         TabIndex        =   57
         Top             =   360
         Width           =   2175
      End
      Begin VB.TextBox txtMinHole 
         Height          =   270
         Left            =   4080
         TabIndex        =   55
         Text            =   "0.8"
         Top             =   360
         Width           =   975
      End
      Begin VB.Label lblMinHole 
         Alignment       =   1  'Right Justify
         Caption         =   "最小开孔(mm)"
         Height          =   255
         Left            =   2520
         TabIndex        =   56
         Top             =   360
         Width           =   1455
      End
   End
   Begin VB.Frame tabPosition__Tab2 
      Caption         =   "打印区域定位"
      Height          =   2415
      Left            =   11520
      TabIndex        =   38
      Top             =   2640
      Width           =   5415
      Begin VB.CommandButton cmdMoveToRightBottom 
         Caption         =   "右下角"
         Height          =   300
         Left            =   3480
         TabIndex        =   51
         Top             =   1920
         Width           =   1335
      End
      Begin VB.CommandButton cmdMoveToLeftBottom 
         Caption         =   "左下角"
         Height          =   300
         Left            =   3480
         TabIndex        =   50
         Top             =   1500
         Width           =   1335
      End
      Begin VB.CommandButton cmdMoveToRightUp 
         Caption         =   "右上角"
         Height          =   300
         Left            =   3480
         TabIndex        =   49
         Top             =   1080
         Width           =   1335
      End
      Begin VB.CommandButton cmdMoveToLeftUp 
         Caption         =   "左上角"
         Height          =   300
         Left            =   3480
         TabIndex        =   48
         Top             =   660
         Width           =   1335
      End
      Begin VB.CommandButton cmdUpdateMinMax 
         Caption         =   "分析"
         Height          =   300
         Left            =   3480
         TabIndex        =   47
         Top             =   240
         Width           =   1335
      End
      Begin VB.TextBox txtMaxY 
         Height          =   270
         Left            =   1560
         Locked          =   -1  'True
         TabIndex        =   46
         Top             =   1920
         Width           =   1095
      End
      Begin VB.TextBox txtMinY 
         Height          =   270
         Left            =   1560
         Locked          =   -1  'True
         TabIndex        =   45
         Top             =   1395
         Width           =   1095
      End
      Begin VB.TextBox txtMaxX 
         Height          =   270
         Left            =   1560
         Locked          =   -1  'True
         TabIndex        =   44
         Top             =   885
         Width           =   1095
      End
      Begin VB.TextBox txtMinX 
         Height          =   270
         Left            =   1560
         Locked          =   -1  'True
         TabIndex        =   43
         Top             =   360
         Width           =   1095
      End
      Begin VB.Label lblMaxY 
         Alignment       =   1  'Right Justify
         Caption         =   "Y最大"
         Height          =   255
         Left            =   720
         TabIndex        =   42
         Top             =   1920
         Width           =   615
      End
      Begin VB.Label lblMinY 
         Alignment       =   1  'Right Justify
         Caption         =   "Y最小"
         Height          =   255
         Left            =   720
         TabIndex        =   41
         Top             =   1395
         Width           =   615
      End
      Begin VB.Label lblMaxX 
         Alignment       =   1  'Right Justify
         Caption         =   "X最大"
         Height          =   255
         Left            =   720
         TabIndex        =   40
         Top             =   885
         Width           =   615
      End
      Begin VB.Label lblMinX 
         Alignment       =   1  'Right Justify
         Caption         =   "X最小"
         Height          =   255
         Left            =   720
         TabIndex        =   39
         Top             =   360
         Width           =   615
      End
   End
   Begin VB.Frame tabPosition__Tab1 
      Caption         =   "设定原点"
      Height          =   2415
      Left            =   11520
      TabIndex        =   25
      Top             =   120
      Width           =   5415
      Begin VB.CommandButton cmdZMicroUp 
         Caption         =   "→"
         Height          =   495
         Left            =   3120
         TabIndex        =   53
         Top             =   720
         Width           =   495
      End
      Begin VB.CommandButton cmdZMicroDown 
         Caption         =   "←"
         Height          =   495
         Left            =   2160
         TabIndex        =   52
         Top             =   720
         Width           =   495
      End
      Begin VB.CommandButton cmdYUp 
         Caption         =   "↑"
         Height          =   495
         Left            =   960
         TabIndex        =   35
         Top             =   240
         Width           =   495
      End
      Begin VB.CommandButton cmdYDown 
         Caption         =   "↓"
         Height          =   495
         Left            =   960
         TabIndex        =   34
         Top             =   1200
         Width           =   495
      End
      Begin VB.CommandButton cmdXLeft 
         Caption         =   "←"
         Height          =   495
         Left            =   480
         TabIndex        =   33
         Top             =   720
         Width           =   495
      End
      Begin VB.CommandButton cmdXRight 
         Caption         =   "→"
         Height          =   495
         Left            =   1440
         TabIndex        =   32
         Top             =   720
         Width           =   495
      End
      Begin VB.CommandButton cmdZUp 
         Caption         =   "↑"
         Height          =   495
         Left            =   2640
         TabIndex        =   31
         Top             =   240
         Width           =   495
      End
      Begin VB.CommandButton cmdZDown 
         Caption         =   "↓"
         Height          =   495
         Left            =   2640
         TabIndex        =   30
         Top             =   1200
         Width           =   495
      End
      Begin VB.CommandButton cmdResetX 
         Caption         =   "X清零"
         Height          =   375
         Left            =   3960
         TabIndex        =   29
         Top             =   240
         Width           =   1095
      End
      Begin VB.CommandButton cmdResetY 
         Caption         =   "Y清零"
         Height          =   375
         Left            =   3960
         TabIndex        =   28
         Top             =   720
         Width           =   1095
      End
      Begin VB.CommandButton cmdResetZ 
         Caption         =   "Z清零"
         Height          =   375
         Left            =   3960
         TabIndex        =   27
         Top             =   1200
         Width           =   1095
      End
      Begin VB.CommandButton cmdResetXYZ 
         Caption         =   "全部清零"
         Height          =   375
         Left            =   3960
         TabIndex        =   26
         Top             =   1680
         Width           =   1095
      End
      Begin VB.Label lblXY 
         Alignment       =   2  'Center
         Caption         =   "XY"
         Height          =   300
         Left            =   960
         TabIndex        =   37
         Top             =   1920
         Width           =   435
      End
      Begin VB.Label lblZ 
         Alignment       =   2  'Center
         AutoSize        =   -1  'True
         Caption         =   "Z"
         Height          =   255
         Left            =   2640
         TabIndex        =   36
         Top             =   1920
         Width           =   495
      End
   End
   Begin MSComctlLib.TabStrip tabPosition 
      Height          =   2655
      Left            =   120
      TabIndex        =   24
      Top             =   3960
      Width           =   5415
      _ExtentX        =   9551
      _ExtentY        =   4683
      _Version        =   393216
      BeginProperty Tabs {1EFB6598-857C-11D1-B16A-00C0F0283628} 
         NumTabs         =   2
         BeginProperty Tab1 {1EFB659A-857C-11D1-B16A-00C0F0283628} 
            ImageVarType    =   2
         EndProperty
         BeginProperty Tab2 {1EFB659A-857C-11D1-B16A-00C0F0283628} 
            ImageVarType    =   2
         EndProperty
      EndProperty
   End
   Begin VB.CommandButton cmdStartSimulator 
      Caption         =   "打开模拟器(&E)"
      Height          =   615
      Left            =   360
      TabIndex        =   12
      Top             =   7920
      Width           =   1815
   End
   Begin VB.CommandButton cmdPause 
      Caption         =   "暂停(&P)"
      Height          =   615
      Left            =   6120
      TabIndex        =   15
      Top             =   7920
      Width           =   1815
   End
   Begin VB.CommandButton cmdStop 
      Caption         =   "停止(&T)"
      Height          =   615
      Left            =   9000
      TabIndex        =   16
      Tag             =   "p@bg"
      Top             =   7920
      Width           =   1815
   End
   Begin VB.Frame frmManualCmd 
      Caption         =   "手动执行命令"
      Height          =   975
      Left            =   5640
      TabIndex        =   10
      Top             =   6720
      Width           =   5415
      Begin VB.CommandButton cmdSendCommand 
         Caption         =   "执行"
         Height          =   510
         Left            =   4560
         TabIndex        =   13
         Top             =   225
         Width           =   735
      End
      Begin VB.TextBox txtManualCommand 
         BeginProperty Font 
            Name            =   "Courier New"
            Size            =   12
            Charset         =   0
            Weight          =   400
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   510
         Left            =   240
         TabIndex        =   11
         Tag             =   "p@bindcommand=<Return>"
         Top             =   225
         Width           =   4215
      End
   End
   Begin VB.Frame frmLog 
      Caption         =   "收发数据"
      Height          =   3975
      Left            =   5640
      TabIndex        =   17
      Top             =   2640
      Width           =   5415
      Begin VB.ComboBox cmbKeepLogNum 
         Height          =   300
         ItemData        =   "CncController.frx":0000
         Left            =   1320
         List            =   "CncController.frx":0022
         Style           =   2  'Dropdown List
         TabIndex        =   22
         Top             =   3480
         Width           =   1455
      End
      Begin VB.CommandButton cmdSaveLog 
         Caption         =   "保存"
         Height          =   300
         Left            =   3120
         TabIndex        =   21
         Top             =   3480
         Width           =   975
      End
      Begin VB.VScrollBar scrVLog 
         Height          =   2895
         Left            =   4920
         TabIndex        =   20
         Top             =   240
         Width           =   255
      End
      Begin VB.CommandButton cmdClearLog 
         Caption         =   "清空"
         Height          =   300
         Left            =   4200
         TabIndex        =   19
         Top             =   3480
         Width           =   975
      End
      Begin VB.ListBox lstLog 
         BeginProperty Font 
            Name            =   "宋体"
            Size            =   12
            Charset         =   134
            Weight          =   400
            Underline       =   0   'False
            Italic          =   0   'False
            Strikethrough   =   0   'False
         EndProperty
         Height          =   2940
         ItemData        =   "CncController.frx":0062
         Left            =   240
         List            =   "CncController.frx":0064
         TabIndex        =   18
         Top             =   240
         Width           =   4695
      End
      Begin VB.Label lblKeepLogNum 
         Caption         =   "保留条目"
         Height          =   255
         Left            =   240
         TabIndex        =   23
         Top             =   3480
         Width           =   855
      End
   End
   Begin VB.Frame frmSerial 
      Caption         =   "端口设置"
      Height          =   1335
      Left            =   5640
      TabIndex        =   3
      Top             =   1200
      Width           =   5415
      Begin VB.CommandButton cmdCloseSerial 
         Caption         =   "关闭"
         Enabled         =   0   'False
         Height          =   375
         Left            =   3720
         TabIndex        =   9
         Top             =   720
         Width           =   1095
      End
      Begin VB.ComboBox cmbTimeOut 
         Height          =   300
         ItemData        =   "CncController.frx":0066
         Left            =   1320
         List            =   "CncController.frx":0082
         Style           =   2  'Dropdown List
         TabIndex        =   8
         Top             =   720
         Width           =   2055
      End
      Begin VB.CommandButton cmdOpenSerial 
         Caption         =   "打开"
         Height          =   375
         Left            =   3720
         TabIndex        =   6
         Top             =   240
         Width           =   1095
      End
      Begin VB.ComboBox cmbSerial 
         Height          =   300
         ItemData        =   "CncController.frx":00CE
         Left            =   1320
         List            =   "CncController.frx":00F0
         TabIndex        =   5
         Top             =   240
         Width           =   2055
      End
      Begin VB.Label lblTimeOut 
         Alignment       =   1  'Right Justify
         Caption         =   "超时时间"
         Height          =   255
         Left            =   240
         TabIndex        =   7
         Top             =   720
         Width           =   855
      End
      Begin VB.Label lblPortNo 
         Alignment       =   1  'Right Justify
         Caption         =   "端口号"
         Height          =   255
         Left            =   240
         TabIndex        =   4
         Top             =   240
         Width           =   855
      End
   End
   Begin VB.CommandButton cmdStart 
      Caption         =   "启动(&S)"
      Height          =   615
      Left            =   3240
      TabIndex        =   14
      Top             =   7920
      Width           =   1815
   End
   Begin VB.CommandButton cmdChooseFile 
      Caption         =   "..."
      Height          =   375
      Left            =   10440
      TabIndex        =   2
      Top             =   120
      Width           =   615
   End
   Begin VB.TextBox txtSourceFile 
      Height          =   375
      Left            =   1920
      TabIndex        =   1
      Top             =   120
      Width           =   8415
   End
   Begin VB.Label lblDrillFile 
      Alignment       =   1  'Right Justify
      Caption         =   "Excellon文件(可选)"
      Height          =   375
      Left            =   120
      TabIndex        =   93
      Top             =   600
      Width           =   1695
   End
   Begin VB.Label lblSourceFile 
      Alignment       =   1  'Right Justify
      Caption         =   "输入文件"
      Height          =   375
      Left            =   120
      TabIndex        =   0
      Top             =   120
      Width           =   1695
   End
End
Attribute VB_Name = "frmMain"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

