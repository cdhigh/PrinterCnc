VERSION 5.00
Begin VB.Form frmMain 
   BorderStyle     =   1  'Fixed Single
   Caption         =   "PrinterCncController [https://github.com/cdhigh/PrinterCnc]"
   ClientHeight    =   7170
   ClientLeft      =   45
   ClientTop       =   435
   ClientWidth     =   10725
   LinkTopic       =   "Form1"
   MaxButton       =   0   'False
   MinButton       =   0   'False
   ScaleHeight     =   7170
   ScaleWidth      =   10725
   StartUpPosition =   2  '屏幕中心
   Tag             =   "p@protocol=WM_DELETE_WINDOW"
   Begin VB.CommandButton cmdPause 
      Caption         =   "暂停(&P)"
      Height          =   615
      Left            =   4320
      TabIndex        =   25
      Top             =   6240
      Width           =   2175
   End
   Begin VB.CommandButton cmdStop 
      Caption         =   "停止(&T)"
      Height          =   615
      Left            =   7800
      TabIndex        =   26
      Tag             =   "p@bg"
      Top             =   6240
      Width           =   2175
   End
   Begin VB.Frame Frame1 
      Caption         =   "手动执行命令"
      Height          =   975
      Left            =   120
      TabIndex        =   21
      Top             =   4800
      Width           =   4935
      Begin VB.CommandButton cmdSendCommand 
         Caption         =   "执行"
         Height          =   495
         Left            =   3960
         TabIndex        =   23
         Top             =   360
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
         Height          =   495
         Left            =   240
         TabIndex        =   22
         Tag             =   "p@bindcommand=<Return>"
         Top             =   360
         Width           =   3615
      End
   End
   Begin VB.Frame frmLog 
      Caption         =   "收发数据"
      Height          =   5175
      Left            =   5160
      TabIndex        =   27
      Top             =   600
      Width           =   5415
      Begin VB.CommandButton cmdSaveLog 
         Caption         =   "保存"
         Height          =   375
         Left            =   2760
         TabIndex        =   32
         Top             =   4680
         Width           =   1095
      End
      Begin VB.VScrollBar scrVLog 
         Height          =   4215
         Left            =   4920
         TabIndex        =   30
         Top             =   360
         Width           =   255
      End
      Begin VB.CommandButton cmdClearLog 
         Caption         =   "清空"
         Height          =   375
         Left            =   4080
         TabIndex        =   29
         Top             =   4680
         Width           =   1095
      End
      Begin VB.ListBox lstLog 
         Height          =   4200
         ItemData        =   "CncController.frx":0000
         Left            =   240
         List            =   "CncController.frx":0002
         TabIndex        =   28
         Top             =   360
         Width           =   4695
      End
      Begin VB.Label lblQueueCmdNum 
         Caption         =   "剩余命令："
         Height          =   375
         Left            =   240
         TabIndex        =   33
         Top             =   4680
         Width           =   2415
      End
   End
   Begin VB.Frame frmSerial 
      Caption         =   "端口设置"
      Height          =   1575
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
         Top             =   840
         Width           =   1095
      End
      Begin VB.ComboBox cmbTimeOut 
         Height          =   300
         ItemData        =   "CncController.frx":0004
         Left            =   1320
         List            =   "CncController.frx":0023
         TabIndex        =   8
         Top             =   840
         Width           =   1695
      End
      Begin VB.CommandButton cmdOpenSerial 
         Caption         =   "打开"
         Height          =   375
         Left            =   3360
         TabIndex        =   6
         Top             =   360
         Width           =   1095
      End
      Begin VB.ComboBox cmbSerial 
         Height          =   300
         ItemData        =   "CncController.frx":0051
         Left            =   1320
         List            =   "CncController.frx":0073
         TabIndex        =   5
         Top             =   360
         Width           =   1695
      End
      Begin VB.Label Label3 
         Alignment       =   1  'Right Justify
         Caption         =   "超时时间"
         Height          =   255
         Left            =   240
         TabIndex        =   7
         Top             =   840
         Width           =   855
      End
      Begin VB.Label Label2 
         Alignment       =   1  'Right Justify
         Caption         =   "端口号"
         Height          =   255
         Left            =   240
         TabIndex        =   4
         Top             =   360
         Width           =   855
      End
   End
   Begin VB.CommandButton cmdStart 
      Caption         =   "启动(&S)"
      Enabled         =   0   'False
      Height          =   615
      Left            =   840
      TabIndex        =   24
      Top             =   6240
      Width           =   2175
   End
   Begin VB.Frame frmSetupManual 
      Caption         =   "手动调整"
      Height          =   2415
      Left            =   120
      TabIndex        =   10
      Top             =   2280
      Width           =   4935
      Begin VB.CommandButton cmdResetXYZ 
         Caption         =   "全部清零"
         Height          =   375
         Left            =   3360
         TabIndex        =   31
         Top             =   1800
         Width           =   1095
      End
      Begin VB.CommandButton cmdResetZ 
         Caption         =   "Z清零"
         Height          =   375
         Left            =   3360
         TabIndex        =   20
         Top             =   1320
         Width           =   1095
      End
      Begin VB.CommandButton cmdResetY 
         Caption         =   "Y清零"
         Height          =   375
         Left            =   3360
         TabIndex        =   19
         Top             =   840
         Width           =   1095
      End
      Begin VB.CommandButton cmdResetX 
         Caption         =   "X清零"
         Height          =   375
         Left            =   3360
         TabIndex        =   18
         Top             =   360
         Width           =   1095
      End
      Begin VB.CommandButton cmdZDown 
         Caption         =   "↓"
         Height          =   495
         Left            =   2400
         TabIndex        =   17
         Top             =   1320
         Width           =   495
      End
      Begin VB.CommandButton cmdZUp 
         Caption         =   "↑"
         Height          =   495
         Left            =   2400
         TabIndex        =   16
         Top             =   480
         Width           =   495
      End
      Begin VB.CommandButton cmdXRight 
         Caption         =   "→"
         Height          =   495
         Left            =   1200
         TabIndex        =   14
         Top             =   960
         Width           =   495
      End
      Begin VB.CommandButton cmdXLeft 
         Caption         =   "←"
         Height          =   495
         Left            =   240
         TabIndex        =   13
         Top             =   960
         Width           =   495
      End
      Begin VB.CommandButton cmdYDown 
         Caption         =   "↓"
         Height          =   495
         Left            =   720
         TabIndex        =   12
         Top             =   1440
         Width           =   495
      End
      Begin VB.CommandButton cmdYUp 
         Caption         =   "↑"
         Height          =   495
         Left            =   720
         TabIndex        =   11
         Top             =   480
         Width           =   495
      End
      Begin VB.Label Label1 
         Caption         =   "XY     Z"
         Height          =   375
         Left            =   1560
         TabIndex        =   15
         Top             =   1920
         Width           =   975
      End
      Begin VB.Line Line2 
         BorderColor     =   &H00FFFFFF&
         X1              =   1920
         X2              =   1920
         Y1              =   360
         Y2              =   1680
      End
      Begin VB.Line Line1 
         BorderColor     =   &H00404040&
         BorderWidth     =   2
         X1              =   1920
         X2              =   1920
         Y1              =   360
         Y2              =   1680
      End
   End
   Begin VB.CommandButton cmdChoosePreview 
      Caption         =   "..."
      Height          =   375
      Left            =   9960
      TabIndex        =   2
      Top             =   120
      Width           =   615
   End
   Begin VB.TextBox txtPreview 
      Height          =   375
      Left            =   1200
      TabIndex        =   1
      Top             =   120
      Width           =   8655
   End
   Begin VB.Label lblPreview 
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

