VERSION 5.00
Begin VB.Form CncSimulator 
   BorderStyle     =   3  'Fixed Dialog
   Caption         =   "PrinterCnc模拟器 【绘图时比较慢，请耐心等候】"
   ClientHeight    =   8310
   ClientLeft      =   45
   ClientTop       =   435
   ClientWidth     =   9690
   LinkTopic       =   "Form1"
   MaxButton       =   0   'False
   MinButton       =   0   'False
   ScaleHeight     =   8310
   ScaleWidth      =   9690
   ShowInTaskbar   =   0   'False
   StartUpPosition =   3  '窗口缺省
   Begin VB.CommandButton cmdClear 
      Caption         =   "全部清除"
      Height          =   375
      Left            =   8280
      TabIndex        =   3
      Top             =   1920
      Width           =   1215
   End
   Begin VB.TextBox txtXYWidth 
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
   Begin VB.Label lblXYWidth 
      Alignment       =   1  'Right Justify
      Caption         =   "X/Y宽度（mm）"
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
