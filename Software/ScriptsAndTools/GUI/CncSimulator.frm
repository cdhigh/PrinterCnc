VERSION 5.00
Begin VB.Form CncSimulator 
   Caption         =   "PrinterCnc模拟器 【绘图时比较慢，请耐心等候】"
   ClientHeight    =   8310
   ClientLeft      =   60
   ClientTop       =   450
   ClientWidth     =   9690
   LinkTopic       =   "Form1"
   ScaleHeight     =   8310
   ScaleWidth      =   9690
   StartUpPosition =   3  '窗口缺省
   Begin VB.TextBox txtYHeight 
      Height          =   375
      Left            =   8280
      Locked          =   -1  'True
      TabIndex        =   8
      Text            =   "200"
      Top             =   2040
      Width           =   1215
   End
   Begin VB.CommandButton cmdClear 
      Caption         =   "全部清除"
      Height          =   375
      Left            =   8280
      TabIndex        =   3
      Top             =   5640
      Width           =   1215
   End
   Begin VB.TextBox txtXWidth 
      Height          =   375
      Left            =   8280
      TabIndex        =   2
      Text            =   "200"
      Top             =   1080
      Width           =   1215
   End
   Begin VB.PictureBox cavSim 
      Appearance      =   0  'Flat
      BackColor       =   &H00FFFFFF&
      ForeColor       =   &H80000008&
      Height          =   8000
      Left            =   120
      ScaleHeight     =   7965
      ScaleWidth      =   7965
      TabIndex        =   0
      Top             =   120
      Width           =   8000
   End
   Begin VB.Label lblYHeight 
      Alignment       =   1  'Right Justify
      Caption         =   "Y高度（mm）"
      Height          =   255
      Left            =   8280
      TabIndex        =   9
      Top             =   1680
      Width           =   1215
   End
   Begin VB.Label lblYOrd 
      Height          =   375
      Left            =   8280
      TabIndex        =   7
      Top             =   4560
      Width           =   1215
   End
   Begin VB.Label lblYOrdNotify 
      Caption         =   "Y坐标(mm)"
      Height          =   255
      Left            =   8280
      TabIndex        =   6
      Top             =   4200
      Width           =   1215
   End
   Begin VB.Label lblXOrd 
      Height          =   375
      Left            =   8280
      TabIndex        =   5
      Top             =   3600
      Width           =   1215
   End
   Begin VB.Label lblXYOrdNotify 
      Caption         =   "X坐标(mm)"
      Height          =   255
      Left            =   8280
      TabIndex        =   4
      Top             =   3240
      Width           =   1215
   End
   Begin VB.Label lblXWidth 
      Alignment       =   1  'Right Justify
      Caption         =   "X宽度（mm）"
      Height          =   255
      Left            =   8280
      TabIndex        =   1
      Top             =   720
      Width           =   1215
   End
End
Attribute VB_Name = "CncSimulator"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub cavSim_MouseMove(Button As Integer, Shift As Integer, X As Single, Y As Single)

End Sub

Private Sub txtXWidth_Change()

End Sub
