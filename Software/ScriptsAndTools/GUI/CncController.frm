VERSION 5.00
Object = "{831FDD16-0C5C-11D2-A9FC-0000F8754DA1}#2.1#0"; "MSCOMCTL.OCX"
Begin VB.Form frmMain 
   BorderStyle     =   1  'Fixed Single
   Caption         =   "PrinterCnc Controller  - <https://github.com/cdhigh>"
   ClientHeight    =   8295
   ClientLeft      =   45
   ClientTop       =   435
   ClientWidth     =   10725
   LinkTopic       =   "Form1"
   MaxButton       =   0   'False
   MinButton       =   0   'False
   ScaleHeight     =   8295
   ScaleWidth      =   10725
   StartUpPosition =   2  '屏幕中心
   Tag             =   "p@protocol=WM_DELETE_WINDOW"
   Begin VB.Frame tabPosition__Tab2 
      Caption         =   "打印区域定位"
      Height          =   2415
      Left            =   10800
      TabIndex        =   50
      Top             =   5400
      Width           =   4935
      Begin VB.CommandButton cmdMoveToRightBottom 
         Caption         =   "右下角"
         Height          =   300
         Left            =   3120
         TabIndex        =   63
         Top             =   1920
         Width           =   1335
      End
      Begin VB.CommandButton cmdMoveToLeftBottom 
         Caption         =   "左下角"
         Height          =   300
         Left            =   3120
         TabIndex        =   62
         Top             =   1500
         Width           =   1335
      End
      Begin VB.CommandButton cmdMoveToRightUp 
         Caption         =   "右上角"
         Height          =   300
         Left            =   3120
         TabIndex        =   61
         Top             =   1080
         Width           =   1335
      End
      Begin VB.CommandButton cmdMoveToLeftUp 
         Caption         =   "左上角"
         Height          =   300
         Left            =   3120
         TabIndex        =   60
         Top             =   660
         Width           =   1335
      End
      Begin VB.CommandButton cmdUpdateMinMax 
         Caption         =   "分析"
         Height          =   300
         Left            =   3120
         TabIndex        =   59
         Top             =   240
         Width           =   1335
      End
      Begin VB.TextBox txtMaxY 
         Height          =   270
         Left            =   1200
         Locked          =   -1  'True
         TabIndex        =   58
         Top             =   1920
         Width           =   1095
      End
      Begin VB.TextBox txtMinY 
         Height          =   270
         Left            =   1200
         Locked          =   -1  'True
         TabIndex        =   57
         Top             =   1395
         Width           =   1095
      End
      Begin VB.TextBox txtMaxX 
         Height          =   270
         Left            =   1200
         Locked          =   -1  'True
         TabIndex        =   56
         Top             =   885
         Width           =   1095
      End
      Begin VB.TextBox txtMinX 
         Height          =   270
         Left            =   1200
         Locked          =   -1  'True
         TabIndex        =   55
         Top             =   360
         Width           =   1095
      End
      Begin VB.Label lblMaxY 
         Alignment       =   1  'Right Justify
         Caption         =   "Y最大"
         Height          =   255
         Left            =   360
         TabIndex        =   54
         Top             =   1920
         Width           =   615
      End
      Begin VB.Label lblMinY 
         Alignment       =   1  'Right Justify
         Caption         =   "Y最小"
         Height          =   255
         Left            =   360
         TabIndex        =   53
         Top             =   1395
         Width           =   615
      End
      Begin VB.Label lblMaxX 
         Alignment       =   1  'Right Justify
         Caption         =   "X最大"
         Height          =   255
         Left            =   360
         TabIndex        =   52
         Top             =   885
         Width           =   615
      End
      Begin VB.Label lblMinX 
         Alignment       =   1  'Right Justify
         Caption         =   "X最小"
         Height          =   255
         Left            =   360
         TabIndex        =   51
         Top             =   360
         Width           =   615
      End
   End
   Begin VB.Frame tabPosition__Tab1 
      Caption         =   "设定原点"
      Height          =   2415
      Left            =   10800
      TabIndex        =   37
      Top             =   2760
      Width           =   4935
      Begin VB.CommandButton cmdZMicroUp 
         Caption         =   "→"
         Height          =   495
         Left            =   2880
         TabIndex        =   65
         Top             =   720
         Width           =   495
      End
      Begin VB.CommandButton cmdZMicroDown 
         Caption         =   "←"
         Height          =   495
         Left            =   1920
         TabIndex        =   64
         Top             =   720
         Width           =   495
      End
      Begin VB.CommandButton cmdYUp 
         Caption         =   "↑"
         Height          =   495
         Left            =   720
         TabIndex        =   47
         Top             =   240
         Width           =   495
      End
      Begin VB.CommandButton cmdYDown 
         Caption         =   "↓"
         Height          =   495
         Left            =   720
         TabIndex        =   46
         Top             =   1200
         Width           =   495
      End
      Begin VB.CommandButton cmdXLeft 
         Caption         =   "←"
         Height          =   495
         Left            =   240
         TabIndex        =   45
         Top             =   720
         Width           =   495
      End
      Begin VB.CommandButton cmdXRight 
         Caption         =   "→"
         Height          =   495
         Left            =   1200
         TabIndex        =   44
         Top             =   720
         Width           =   495
      End
      Begin VB.CommandButton cmdZUp 
         Caption         =   "↑"
         Height          =   495
         Left            =   2400
         TabIndex        =   43
         Top             =   240
         Width           =   495
      End
      Begin VB.CommandButton cmdZDown 
         Caption         =   "↓"
         Height          =   495
         Left            =   2400
         TabIndex        =   42
         Top             =   1200
         Width           =   495
      End
      Begin VB.CommandButton cmdResetX 
         Caption         =   "X清零"
         Height          =   375
         Left            =   3600
         TabIndex        =   41
         Top             =   240
         Width           =   1095
      End
      Begin VB.CommandButton cmdResetY 
         Caption         =   "Y清零"
         Height          =   375
         Left            =   3600
         TabIndex        =   40
         Top             =   720
         Width           =   1095
      End
      Begin VB.CommandButton cmdResetZ 
         Caption         =   "Z清零"
         Height          =   375
         Left            =   3600
         TabIndex        =   39
         Top             =   1200
         Width           =   1095
      End
      Begin VB.CommandButton cmdResetXYZ 
         Caption         =   "全部清零"
         Height          =   375
         Left            =   3600
         TabIndex        =   38
         Top             =   1680
         Width           =   1095
      End
      Begin VB.Label lblXY 
         Alignment       =   2  'Center
         Caption         =   "XY"
         Height          =   300
         Left            =   720
         TabIndex        =   49
         Top             =   1920
         Width           =   435
      End
      Begin VB.Label lblZ 
         Alignment       =   2  'Center
         AutoSize        =   -1  'True
         Caption         =   "Z"
         Height          =   255
         Left            =   2400
         TabIndex        =   48
         Top             =   1920
         Width           =   495
      End
   End
   Begin MSComctlLib.TabStrip tabPosition 
      Height          =   2655
      Left            =   120
      TabIndex        =   36
      Top             =   4440
      Width           =   4935
      _ExtentX        =   8705
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
      Top             =   7440
      Width           =   1815
   End
   Begin VB.Frame frmSpeed 
      Caption         =   "速度（值越小越快）/ 笔宽（mm）"
      Height          =   2295
      Left            =   120
      TabIndex        =   23
      Top             =   2040
      Width           =   4935
      Begin VB.TextBox txtPenWidth 
         Height          =   375
         Left            =   1800
         TabIndex        =   34
         Text            =   "0.6"
         Top             =   1680
         Width           =   1215
      End
      Begin VB.CommandButton cmdApplyAxisSpeed 
         Caption         =   "应用"
         Height          =   1095
         Left            =   3360
         TabIndex        =   30
         Top             =   600
         Width           =   1095
      End
      Begin VB.TextBox txtZSpeed 
         Height          =   375
         Left            =   1800
         TabIndex        =   29
         Text            =   "60"
         Top             =   1200
         Width           =   1215
      End
      Begin VB.TextBox txtYSpeed 
         Height          =   375
         Left            =   1800
         TabIndex        =   28
         Text            =   "120"
         Top             =   720
         Width           =   1215
      End
      Begin VB.TextBox txtXSpeed 
         Height          =   375
         Left            =   1800
         TabIndex        =   27
         Text            =   "100"
         Top             =   240
         Width           =   1215
      End
      Begin VB.Label lblPenWidth 
         Alignment       =   1  'Right Justify
         Caption         =   "笔尖直径"
         Height          =   255
         Left            =   600
         TabIndex        =   35
         Top             =   1680
         Width           =   975
      End
      Begin VB.Label lblZSpeed 
         Alignment       =   1  'Right Justify
         Caption         =   "Z轴速度"
         Height          =   255
         Left            =   600
         TabIndex        =   26
         Top             =   1200
         Width           =   975
      End
      Begin VB.Label lblYSpeed 
         Alignment       =   1  'Right Justify
         Caption         =   "Y轴速度"
         Height          =   255
         Left            =   600
         TabIndex        =   25
         Top             =   720
         Width           =   975
      End
      Begin VB.Label lblXSpeed 
         Alignment       =   1  'Right Justify
         Caption         =   "X轴速度"
         Height          =   255
         Left            =   600
         TabIndex        =   24
         Top             =   240
         Width           =   975
      End
   End
   Begin VB.CommandButton cmdPause 
      Caption         =   "暂停(&P)"
      Height          =   615
      Left            =   5800
      TabIndex        =   15
      Top             =   7440
      Width           =   1815
   End
   Begin VB.CommandButton cmdStop 
      Caption         =   "停止(&T)"
      Height          =   615
      Left            =   8520
      TabIndex        =   16
      Tag             =   "p@bg"
      Top             =   7440
      Width           =   1815
   End
   Begin VB.Frame frmManualCmd 
      Caption         =   "手动执行命令"
      Height          =   975
      Left            =   5160
      TabIndex        =   10
      Top             =   6120
      Width           =   5415
      Begin VB.CommandButton cmdSendCommand 
         Caption         =   "执行"
         Height          =   390
         Left            =   4560
         TabIndex        =   13
         Top             =   345
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
         Height          =   390
         Left            =   240
         TabIndex        =   11
         Tag             =   "p@bindcommand=<Return>"
         Top             =   345
         Width           =   4215
      End
   End
   Begin VB.Frame frmLog 
      Caption         =   "收发数据"
      Height          =   5415
      Left            =   5160
      TabIndex        =   17
      Top             =   600
      Width           =   5415
      Begin VB.ComboBox cmbKeepLogNum 
         Height          =   300
         ItemData        =   "CncController.frx":0000
         Left            =   1320
         List            =   "CncController.frx":0022
         Style           =   2  'Dropdown List
         TabIndex        =   32
         Top             =   4920
         Width           =   1455
      End
      Begin VB.CommandButton cmdSaveLog 
         Caption         =   "保存"
         Height          =   300
         Left            =   3120
         TabIndex        =   21
         Top             =   4920
         Width           =   975
      End
      Begin VB.VScrollBar scrVLog 
         Height          =   3975
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
         Top             =   4920
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
         Height          =   3900
         ItemData        =   "CncController.frx":0062
         Left            =   240
         List            =   "CncController.frx":0064
         TabIndex        =   18
         Top             =   240
         Width           =   4695
      End
      Begin VB.Line lneUp 
         BorderColor     =   &H00C0C0C0&
         X1              =   240
         X2              =   5040
         Y1              =   4680
         Y2              =   4680
      End
      Begin VB.Line lneDown 
         BorderColor     =   &H00C0FFFF&
         BorderWidth     =   3
         X1              =   240
         X2              =   5040
         Y1              =   4680
         Y2              =   4680
      End
      Begin VB.Label lblKeepLogNum 
         Caption         =   "保留条目"
         Height          =   255
         Left            =   240
         TabIndex        =   33
         Top             =   4920
         Width           =   855
      End
      Begin VB.Label lblTimeToFinish 
         Caption         =   "预计剩余时间：00:00:00"
         Height          =   255
         Left            =   2760
         TabIndex        =   31
         Top             =   4320
         Width           =   2415
      End
      Begin VB.Label lblQueueCmdNum 
         Caption         =   "剩余命令：0"
         Height          =   255
         Left            =   240
         TabIndex        =   22
         Top             =   4320
         Width           =   2055
      End
   End
   Begin VB.Frame frmSerial 
      Caption         =   "端口设置"
      Height          =   1335
      Left            =   120
      TabIndex        =   3
      Top             =   600
      Width           =   4935
      Begin VB.CommandButton cmdCloseSerial 
         Caption         =   "关闭"
         Enabled         =   0   'False
         Height          =   375
         Left            =   3360
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
         Width           =   1695
      End
      Begin VB.CommandButton cmdOpenSerial 
         Caption         =   "打开"
         Height          =   375
         Left            =   3360
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
         Width           =   1695
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
      Left            =   3080
      TabIndex        =   14
      Top             =   7440
      Width           =   1815
   End
   Begin VB.CommandButton cmdChooseFile 
      Caption         =   "..."
      Height          =   375
      Left            =   9960
      TabIndex        =   2
      Top             =   120
      Width           =   615
   End
   Begin VB.TextBox txtSourceFile 
      Height          =   375
      Left            =   1200
      TabIndex        =   1
      Top             =   120
      Width           =   8655
   End
   Begin VB.Label lblSourceFile 
      Alignment       =   1  'Right Justify
      Caption         =   "输入文件"
      Height          =   375
      Left            =   120
      TabIndex        =   0
      Top             =   120
      Width           =   975
   End
End
Attribute VB_Name = "frmMain"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

