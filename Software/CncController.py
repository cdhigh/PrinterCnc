#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
废喷墨打印机改装的大行程数控雕刻机的PC控制端程序，解析GERBER_RS274X文件并和控制板通讯。
支持Python 2.x/3.x，在python 2.7.8/3.4.1下测试通过。
因为使用Python，没有使用到平台强相关特性，理论上支持Windows/Mac OS/Linux操作系统。
外部库依赖：
    pyserial
注意：
    在一些更老的python版本下运行有可能需要在此文件开头增加一行声明
    from __future__ import unicode_literals
GUI：
    GUI界面采用Python内置的Tkinter标准库，使用作者自己的VisualTkinter工具自动生成界面代码。
    <https://github.com/cdhigh/Visual-Tkinter-for-Python>
致谢：
    此项目参考了<https://github.com/themrleon/OpenCdNC>
代码托管：
    此代码项目开源并托管在<https://github.com/cdhigh/PrinterCnC>
    在github仓库同时也有预编译好的windows exe文件。
Author：
    cdhigh <https://github.com/cdhigh>
License:
    The MIT License (MIT)
第一版完成日期：
    2015-05-14
"""

__Version__ = 'v1.0d'

import os, sys, re, time, datetime, math
try:
    from tkinter import *
except ImportError:  #Python 2.x
    PythonVersion = 2
    from Tkinter import *
    from tkFont import Font
    from ttk import *
    #Usage:showinfo/warning/error,askquestion/okcancel/yesno/retrycancel
    from tkMessageBox import *
    #Usage:f=tkFileDialog.askopenfilename(initialdir='E:/Python')
    import tkFileDialog
    #import tkSimpleDialog
    from Queue import Queue
    import ConfigParser as configparser
else:  #Python 3.x
    PythonVersion = 3
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    import tkinter.filedialog as tkFileDialog
    #import tkinter.simpledialog as tkSimpleDialog    #askstring()
    from queue import Queue
    import configparser
    
try: #用于Beep声音提醒
    import winsound
except ImportError:
    winsound = None
    
from threading import Thread, Event
import serial

CFG_FILE = 'CncController.ini'
ANGLE_PER_SIDE = 0.017453293 * 10 #用多边形逼近圆形时的步进角度，值越小越圆，但数据量越大

if getattr(sys, 'frozen', False): #在cxFreeze打包后
    __file__ = sys.executable
    
#根据文件名后缀判断是否是gerber文件
def isGerberFile(filename):
    return filename.upper().endswith(('.TXT','.GBR','.GERBER','.SOL','.CMP',
                                    '.TOP','.BOT','.GBL','.GTL'))

#用于设定在打开文件对话框里面的GERBER文件后缀
def GerberFileMask():
    return [("Gerber Files","*.sol"),("Gerber Files","*.cmp"),
           ("Gerber Files","*.gbr"),("Gerber Files","*.gbl"),
           ("Gerber Files","*.gtl"),("Gerber Files","*.top"),
           ("Gerber Files","*.bot"),("Gerber Files","*.gerber"),
           ("All Files", "*")]


class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('PrinterCnc Controller - <https://github.com/cdhigh>')
        self.master.resizable(0,0)
        self.icondata = """
            R0lGODlhGAEXAfcAAP//////zP//mf//Zv//M///AP/M///MzP/Mmf/MZv/MM//MAP+Z
            //+ZzP+Zmf+ZZv+ZM/+ZAP9m//9mzP9mmf9mZv9mM/9mAP8z//8zzP8zmf8zZv8zM/8z
            AP8A//8AzP8Amf8AZv8AM/8AAMz//8z/zMz/mcz/Zsz/M8z/AMzM/8zMzMzMmczMZszM
            M8zMAMyZ/8yZzMyZmcyZZsyZM8yZAMxm/8xmzMxmmcxmZsxmM8xmAMwz/8wzzMwzmcwz
            ZswzM8wzAMwA/8wAzMwAmcwAZswAM8wAAJn//5n/zJn/mZn/Zpn/M5n/AJnM/5nMzJnM
            mZnMZpnMM5nMAJmZ/5mZzJmZmZmZZpmZM5mZAJlm/5lmzJlmmZlmZplmM5lmAJkz/5kz
            zJkzmZkzZpkzM5kzAJkA/5kAzJkAmZkAZpkAM5kAAGb//2b/zGb/mWb/Zmb/M2b/AGbM
            /2bMzGbMmWbMZmbMM2bMAGaZ/2aZzGaZmWaZZmaZM2aZAGZm/2ZmzGZmmWZmZmZmM2Zm
            AGYz/2YzzGYzmWYzZmYzM2YzAGYA/2YAzGYAmWYAZmYAM2YAADP//zP/zDP/mTP/ZjP/
            MzP/ADPM/zPMzDPMmTPMZjPMMzPMADOZ/zOZzDOZmTOZZjOZMzOZADNm/zNmzDNmmTNm
            ZjNmMzNmADMz/zMzzDMzmTMzZjMzMzMzADMA/zMAzDMAmTMAZjMAMzMAAAD//wD/zAD/
            mQD/ZgD/MwD/AADM/wDMzADMmQDMZgDMMwDMAACZ/wCZzACZmQCZZgCZMwCZAABm/wBm
            zABmmQBmZgBmMwBmAAAz/wAzzAAzmQAzZgAzMwAzAAAA/wAAzAAAmQAAZgAAMwAAAP//
            /wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            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
            zDe3esw0tlNQGD7xdx/0u9Se8Wxxy6yZX+ptj7vPmci+9rfP/e57//vgD7//+OX6CU2v
            mvqtdj7kqfuQreR+1Oiv9V3Wz36H0NTy0x99H69f/4ZgBdC+dHvslDD0138MUSHm9iAs
            J1X+Unv9hyKKpyEkoHdKN3tnwX8GyGERGFmZB3TVFxu+l4FQR00d6IHpJxcFmIEcpnwA
            soDFFxsYqILExYI8R4F45Xg4J4P3RoMv8nk2Z0ApqIOjwYP31XL/Z0BCOBEjSDklaCjI
            EoI6uITmZIP6Z3dBmIQJIYX7IWBNKCy2gndYiFo8k0oVZYQlxnuQMX5quIZsmH1P8YZB
            YYZtQWxy6FJ0WIcmKH94uIdn2Hx8+Ick9ocuhoaCWIeBWIh6ZoGI2GCHuIiL36aIjviC
            kSiHjTiJjQeJlsiAd5iJg+iHnEhglfiJw+N4oqhum1iKgUOKqOiEp7iKYYeJrohPoRiL
            7dOKtBg7qniLlUSIuliBvNiLpWWLwPg8uTiMhFSMxlhKyJiMbSKMzFiLWfiMGxWEGyeN
            uSQaCSGA1ngiltaFHEUUQOIUKQQUI8QQ2rgdcJiO5JhW6nhFtNcUiuFx5wgZ7ViPQ0Ed
            9rgUZJGPgYF1VNhO+RiQ4LgWAlmQBpl5OZhmOHGQDNmQ+Rh+DhmRTxEVUBiGFnmRGJmR
            GrmRHNmRHvmRIFl/AQEAOw="""
        self.iconimg = PhotoImage(data=self.icondata)
        self.master.tk.call('wm', 'iconphoto', self.master._w, self.iconimg)
        self.master.protocol('WM_DELETE_WINDOW', self.EV_WM_DELETE_WINDOW)
        # To center the window on the screen.
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws / 2) - (750 / 2)
        y = (hs / 2) - (518 / 2)
        self.master.geometry('%dx%d+%d+%d' % (750,518,x,y))
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.tabPosition = Notebook(self.top)
        self.tabPosition.place(relx=0.011, rely=0.51, relwidth=0.481, relheight=0.342)

        self.tabPosition__Tab1 = Frame(self.tabPosition)
        self.style.configure('TcmdZMicroUp.TButton', font=('宋体',9))
        self.cmdZMicroUp = Button(self.tabPosition__Tab1, text='→', command=self.cmdZMicroUp_Cmd, style='TcmdZMicroUp.TButton')
        self.cmdZMicroUp.place(relx=0.576, rely=0.298, relwidth=0.091, relheight=0.205)
        self.style.configure('TcmdZMicroDown.TButton', font=('宋体',9))
        self.cmdZMicroDown = Button(self.tabPosition__Tab1, text='←', command=self.cmdZMicroDown_Cmd, style='TcmdZMicroDown.TButton')
        self.cmdZMicroDown.place(relx=0.399, rely=0.298, relwidth=0.091, relheight=0.205)
        self.style.configure('TcmdYUp.TButton', font=('宋体',9))
        self.cmdYUp = Button(self.tabPosition__Tab1, text='↑', command=self.cmdYUp_Cmd, style='TcmdYUp.TButton')
        self.cmdYUp.place(relx=0.177, rely=0.099, relwidth=0.091, relheight=0.205)
        self.style.configure('TcmdYDown.TButton', font=('宋体',9))
        self.cmdYDown = Button(self.tabPosition__Tab1, text='↓', command=self.cmdYDown_Cmd, style='TcmdYDown.TButton')
        self.cmdYDown.place(relx=0.177, rely=0.497, relwidth=0.091, relheight=0.205)
        self.style.configure('TcmdXLeft.TButton', font=('宋体',9))
        self.cmdXLeft = Button(self.tabPosition__Tab1, text='←', command=self.cmdXLeft_Cmd, style='TcmdXLeft.TButton')
        self.cmdXLeft.place(relx=0.089, rely=0.298, relwidth=0.091, relheight=0.205)
        self.style.configure('TcmdXRight.TButton', font=('宋体',9))
        self.cmdXRight = Button(self.tabPosition__Tab1, text='→', command=self.cmdXRight_Cmd, style='TcmdXRight.TButton')
        self.cmdXRight.place(relx=0.266, rely=0.298, relwidth=0.091, relheight=0.205)
        self.style.configure('TcmdZUp.TButton', font=('宋体',9))
        self.cmdZUp = Button(self.tabPosition__Tab1, text='↑', command=self.cmdZUp_Cmd, style='TcmdZUp.TButton')
        self.cmdZUp.place(relx=0.488, rely=0.099, relwidth=0.091, relheight=0.205)
        self.style.configure('TcmdZDown.TButton', font=('宋体',9))
        self.cmdZDown = Button(self.tabPosition__Tab1, text='↓', command=self.cmdZDown_Cmd, style='TcmdZDown.TButton')
        self.cmdZDown.place(relx=0.488, rely=0.497, relwidth=0.091, relheight=0.205)
        self.style.configure('TcmdResetX.TButton', font=('宋体',9))
        self.cmdResetX = Button(self.tabPosition__Tab1, text='X清零', command=self.cmdResetX_Cmd, style='TcmdResetX.TButton')
        self.cmdResetX.place(relx=0.731, rely=0.099, relwidth=0.202, relheight=0.155)
        self.style.configure('TcmdResetY.TButton', font=('宋体',9))
        self.cmdResetY = Button(self.tabPosition__Tab1, text='Y清零', command=self.cmdResetY_Cmd, style='TcmdResetY.TButton')
        self.cmdResetY.place(relx=0.731, rely=0.298, relwidth=0.202, relheight=0.155)
        self.style.configure('TcmdResetZ.TButton', font=('宋体',9))
        self.cmdResetZ = Button(self.tabPosition__Tab1, text='Z清零', command=self.cmdResetZ_Cmd, style='TcmdResetZ.TButton')
        self.cmdResetZ.place(relx=0.731, rely=0.497, relwidth=0.202, relheight=0.155)
        self.style.configure('TcmdResetXYZ.TButton', font=('宋体',9))
        self.cmdResetXYZ = Button(self.tabPosition__Tab1, text='全部清零', command=self.cmdResetXYZ_Cmd, style='TcmdResetXYZ.TButton')
        self.cmdResetXYZ.place(relx=0.731, rely=0.696, relwidth=0.202, relheight=0.155)
        self.style.configure('TlblXY.TLabel', anchor='center', font=('宋体',9))
        self.lblXY = Label(self.tabPosition__Tab1, text='XY', style='TlblXY.TLabel')
        self.lblXY.place(relx=0.177, rely=0.795, relwidth=0.08, relheight=0.124)
        self.style.configure('TlblZ.TLabel', anchor='center', font=('宋体',9))
        self.lblZ = Label(self.tabPosition__Tab1, text='Z', style='TlblZ.TLabel')
        self.lblZ.place(relx=0.488, rely=0.795, relwidth=0.091, relheight=0.106)
        self.tabPosition.add(self.tabPosition__Tab1, text='设定原点')

        self.tabPosition__Tab2 = Frame(self.tabPosition)
        self.style.configure('TcmdMoveToRightBottom.TButton', font=('宋体',9))
        self.cmdMoveToRightBottom = Button(self.tabPosition__Tab2, text='右下角', command=self.cmdMoveToRightBottom_Cmd, style='TcmdMoveToRightBottom.TButton')
        self.cmdMoveToRightBottom.place(relx=0.643, rely=0.795, relwidth=0.247, relheight=0.124)
        self.style.configure('TcmdMoveToLeftBottom.TButton', font=('宋体',9))
        self.cmdMoveToLeftBottom = Button(self.tabPosition__Tab2, text='左下角', command=self.cmdMoveToLeftBottom_Cmd, style='TcmdMoveToLeftBottom.TButton')
        self.cmdMoveToLeftBottom.place(relx=0.643, rely=0.621, relwidth=0.247, relheight=0.124)
        self.style.configure('TcmdMoveToRightUp.TButton', font=('宋体',9))
        self.cmdMoveToRightUp = Button(self.tabPosition__Tab2, text='右上角', command=self.cmdMoveToRightUp_Cmd, style='TcmdMoveToRightUp.TButton')
        self.cmdMoveToRightUp.place(relx=0.643, rely=0.447, relwidth=0.247, relheight=0.124)
        self.style.configure('TcmdMoveToLeftUp.TButton', font=('宋体',9))
        self.cmdMoveToLeftUp = Button(self.tabPosition__Tab2, text='左上角', command=self.cmdMoveToLeftUp_Cmd, style='TcmdMoveToLeftUp.TButton')
        self.cmdMoveToLeftUp.place(relx=0.643, rely=0.273, relwidth=0.247, relheight=0.124)
        self.style.configure('TcmdUpdateMinMax.TButton', font=('宋体',9))
        self.cmdUpdateMinMax = Button(self.tabPosition__Tab2, text='分析', command=self.cmdUpdateMinMax_Cmd, style='TcmdUpdateMinMax.TButton')
        self.cmdUpdateMinMax.place(relx=0.643, rely=0.099, relwidth=0.247, relheight=0.124)
        self.txtMaxYVar = StringVar(value='')
        self.txtMaxY = Entry(self.tabPosition__Tab2, state='readonly', textvariable=self.txtMaxYVar, font=('宋体',9))
        self.txtMaxY.place(relx=0.288, rely=0.795, relwidth=0.202, relheight=0.112)
        self.txtMinYVar = StringVar(value='')
        self.txtMinY = Entry(self.tabPosition__Tab2, state='readonly', textvariable=self.txtMinYVar, font=('宋体',9))
        self.txtMinY.place(relx=0.288, rely=0.578, relwidth=0.202, relheight=0.112)
        self.txtMaxXVar = StringVar(value='')
        self.txtMaxX = Entry(self.tabPosition__Tab2, state='readonly', textvariable=self.txtMaxXVar, font=('宋体',9))
        self.txtMaxX.place(relx=0.288, rely=0.366, relwidth=0.202, relheight=0.112)
        self.txtMinXVar = StringVar(value='')
        self.txtMinX = Entry(self.tabPosition__Tab2, state='readonly', textvariable=self.txtMinXVar, font=('宋体',9))
        self.txtMinX.place(relx=0.288, rely=0.149, relwidth=0.202, relheight=0.112)
        self.style.configure('TlblMaxY.TLabel', anchor='e', font=('宋体',9))
        self.lblMaxY = Label(self.tabPosition__Tab2, text='Y最大', style='TlblMaxY.TLabel')
        self.lblMaxY.place(relx=0.133, rely=0.795, relwidth=0.114, relheight=0.106)
        self.style.configure('TlblMinY.TLabel', anchor='e', font=('宋体',9))
        self.lblMinY = Label(self.tabPosition__Tab2, text='Y最小', style='TlblMinY.TLabel')
        self.lblMinY.place(relx=0.133, rely=0.578, relwidth=0.114, relheight=0.106)
        self.style.configure('TlblMaxX.TLabel', anchor='e', font=('宋体',9))
        self.lblMaxX = Label(self.tabPosition__Tab2, text='X最大', style='TlblMaxX.TLabel')
        self.lblMaxX.place(relx=0.133, rely=0.366, relwidth=0.114, relheight=0.106)
        self.style.configure('TlblMinX.TLabel', anchor='e', font=('宋体',9))
        self.lblMinX = Label(self.tabPosition__Tab2, text='X最小', style='TlblMinX.TLabel')
        self.lblMinX.place(relx=0.133, rely=0.149, relwidth=0.114, relheight=0.106)
        self.tabPosition.add(self.tabPosition__Tab2, text='打印区域定位')

        self.style.configure('TcmdStartSimulator.TButton', font=('宋体',9))
        self.cmdStartSimulator = Button(self.top, text='打开模拟器(E)', underline=6, command=self.cmdStartSimulator_Cmd, style='TcmdStartSimulator.TButton')
        self.cmdStartSimulator.place(relx=0.032, rely=0.896, relwidth=0.161, relheight=0.079)
        self.top.bind_all('<Alt-E>', lambda e: self.cmdStartSimulator.focus_set() or self.cmdStartSimulator.invoke())
        self.top.bind_all('<Alt-e>', lambda e: self.cmdStartSimulator.focus_set() or self.cmdStartSimulator.invoke())

        self.style.configure('TfrmSpeed.TLabelframe', font=('宋体',9))
        self.style.configure('TfrmSpeed.TLabelframe.Label', font=('宋体',9))
        self.frmSpeed = LabelFrame(self.top, text='速度（值越小越快）/ 笔宽（mm）', style='TfrmSpeed.TLabelframe')
        self.frmSpeed.place(relx=0.011, rely=0.263, relwidth=0.481, relheight=0.234)

        self.style.configure('TcmdPause.TButton', font=('宋体',9))
        self.cmdPause = Button(self.top, text='暂停(P)', underline=3, command=self.cmdPause_Cmd, style='TcmdPause.TButton')
        self.cmdPause.place(relx=0.544, rely=0.896, relwidth=0.161, relheight=0.079)
        self.top.bind_all('<Alt-P>', lambda e: self.cmdPause.focus_set() or self.cmdPause.invoke())
        self.top.bind_all('<Alt-p>', lambda e: self.cmdPause.focus_set() or self.cmdPause.invoke())

        self.style.configure('TcmdStop.TButton', background='#F0F0F0', font=('宋体',9))
        self.cmdStop = Button(self.top, text='停止(T)', underline=3, command=self.cmdStop_Cmd, style='TcmdStop.TButton')
        self.cmdStop.place(relx=0.8, rely=0.896, relwidth=0.161, relheight=0.079)
        self.top.bind_all('<Alt-T>', lambda e: self.cmdStop.focus_set() or self.cmdStop.invoke())
        self.top.bind_all('<Alt-t>', lambda e: self.cmdStop.focus_set() or self.cmdStop.invoke())

        self.style.configure('TfrmManualCmd.TLabelframe', font=('宋体',9))
        self.style.configure('TfrmManualCmd.TLabelframe.Label', font=('宋体',9))
        self.frmManualCmd = LabelFrame(self.top, text='手动执行命令', style='TfrmManualCmd.TLabelframe')
        self.frmManualCmd.place(relx=0.501, rely=0.726, relwidth=0.481, relheight=0.125)

        self.style.configure('TfrmLog.TLabelframe', font=('宋体',9))
        self.style.configure('TfrmLog.TLabelframe.Label', font=('宋体',9))
        self.frmLog = LabelFrame(self.top, text='收发数据', style='TfrmLog.TLabelframe')
        self.frmLog.place(relx=0.501, rely=0.077, relwidth=0.481, relheight=0.635)

        self.style.configure('TfrmSerial.TLabelframe', font=('宋体',9))
        self.style.configure('TfrmSerial.TLabelframe.Label', font=('宋体',9))
        self.frmSerial = LabelFrame(self.top, text='端口设置', style='TfrmSerial.TLabelframe')
        self.frmSerial.place(relx=0.011, rely=0.077, relwidth=0.481, relheight=0.172)

        self.style.configure('TcmdStart.TButton', font=('宋体',9))
        self.cmdStart = Button(self.top, text='启动(S)', underline=3, command=self.cmdStart_Cmd, style='TcmdStart.TButton')
        self.cmdStart.place(relx=0.288, rely=0.896, relwidth=0.161, relheight=0.079)
        self.top.bind_all('<Alt-S>', lambda e: self.cmdStart.focus_set() or self.cmdStart.invoke())
        self.top.bind_all('<Alt-s>', lambda e: self.cmdStart.focus_set() or self.cmdStart.invoke())

        self.style.configure('TcmdChooseFile.TButton', font=('宋体',9))
        self.cmdChooseFile = Button(self.top, text='...', command=self.cmdChooseFile_Cmd, style='TcmdChooseFile.TButton')
        self.cmdChooseFile.place(relx=0.928, rely=0.015, relwidth=0.055, relheight=0.048)

        self.txtSourceFileVar = StringVar(value='')
        self.txtSourceFile = Entry(self.top, textvariable=self.txtSourceFileVar, font=('宋体',9))
        self.txtSourceFile.place(relx=0.107, rely=0.015, relwidth=0.812, relheight=0.048)

        self.style.configure('TlblSourceFile.TLabel', anchor='e', font=('宋体',9))
        self.lblSourceFile = Label(self.top, text='输入文件', style='TlblSourceFile.TLabel')
        self.lblSourceFile.place(relx=0.011, rely=0.015, relwidth=0.087, relheight=0.048)

        self.txtZLiftStepsVar = StringVar(value='130')
        self.txtZLiftSteps = Entry(self.frmSpeed, textvariable=self.txtZLiftStepsVar, font=('宋体',9))
        self.txtZLiftSteps.place(relx=0.731, rely=0.132, relwidth=0.224, relheight=0.207)

        self.txtPenWidthVar = StringVar(value='0.6')
        self.txtPenWidth = Entry(self.frmSpeed, textvariable=self.txtPenWidthVar, font=('宋体',9))
        self.txtPenWidth.place(relx=0.731, rely=0.397, relwidth=0.224, relheight=0.207)

        self.style.configure('TcmdApplyAxisSpeed.TButton', font=('宋体',9))
        self.cmdApplyAxisSpeed = Button(self.frmSpeed, text='应用', command=self.cmdApplyAxisSpeed_Cmd, style='TcmdApplyAxisSpeed.TButton')
        self.cmdApplyAxisSpeed.place(relx=0.554, rely=0.661, relwidth=0.402, relheight=0.207)

        self.txtZSpeedVar = StringVar(value='80')
        self.txtZSpeed = Entry(self.frmSpeed, textvariable=self.txtZSpeedVar, font=('宋体',9))
        self.txtZSpeed.place(relx=0.244, rely=0.661, relwidth=0.224, relheight=0.207)

        self.txtYSpeedVar = StringVar(value='120')
        self.txtYSpeed = Entry(self.frmSpeed, textvariable=self.txtYSpeedVar, font=('宋体',9))
        self.txtYSpeed.place(relx=0.244, rely=0.397, relwidth=0.224, relheight=0.207)

        self.txtXSpeedVar = StringVar(value='100')
        self.txtXSpeed = Entry(self.frmSpeed, textvariable=self.txtXSpeedVar, font=('宋体',9))
        self.txtXSpeed.place(relx=0.244, rely=0.132, relwidth=0.224, relheight=0.207)

        self.style.configure('TlblZLiftSteps.TLabel', anchor='e', font=('宋体',9))
        self.lblZLiftSteps = Label(self.frmSpeed, text='Z轴步进', style='TlblZLiftSteps.TLabel')
        self.lblZLiftSteps.place(relx=0.51, rely=0.132, relwidth=0.18, relheight=0.14)

        self.style.configure('TlblPenWidth.TLabel', anchor='e', font=('宋体',9))
        self.lblPenWidth = Label(self.frmSpeed, text='笔尖直径', style='TlblPenWidth.TLabel')
        self.lblPenWidth.place(relx=0.51, rely=0.397, relwidth=0.18, relheight=0.14)

        self.style.configure('TlblZSpeed.TLabel', anchor='e', font=('宋体',9))
        self.lblZSpeed = Label(self.frmSpeed, text='Z轴速度', style='TlblZSpeed.TLabel')
        self.lblZSpeed.place(relx=0.022, rely=0.661, relwidth=0.18, relheight=0.14)

        self.style.configure('TlblYSpeed.TLabel', anchor='e', font=('宋体',9))
        self.lblYSpeed = Label(self.frmSpeed, text='Y轴速度', style='TlblYSpeed.TLabel')
        self.lblYSpeed.place(relx=0.022, rely=0.397, relwidth=0.18, relheight=0.14)

        self.style.configure('TlblXSpeed.TLabel', anchor='e', font=('宋体',9))
        self.lblXSpeed = Label(self.frmSpeed, text='X轴速度', style='TlblXSpeed.TLabel')
        self.lblXSpeed.place(relx=0.022, rely=0.132, relwidth=0.18, relheight=0.14)

        self.style.configure('TcmdSendCommand.TButton', font=('宋体',9))
        self.cmdSendCommand = Button(self.frmManualCmd, text='执行', command=self.cmdSendCommand_Cmd, style='TcmdSendCommand.TButton')
        self.cmdSendCommand.place(relx=0.842, rely=0.354, relwidth=0.136, relheight=0.4)

        self.txtManualCommandVar = StringVar(value='')
        self.txtManualCommand = Entry(self.frmManualCmd, textvariable=self.txtManualCommandVar, font=('Courier New',12))
        self.txtManualCommand.place(relx=0.044, rely=0.354, relwidth=0.778, relheight=0.4)
        self.txtManualCommand.bind('<Return>', self.txtManualCommand_Return)

        self.cmbKeepLogNumList = ['100','500','1000','2000','3000','4000','5000','8000','10000','20000',]
        self.cmbKeepLogNumVar = StringVar(value='100')
        self.cmbKeepLogNum = Combobox(self.frmLog, state='readonly', text='100', textvariable=self.cmbKeepLogNumVar, values=self.cmbKeepLogNumList, font=('宋体',9))
        self.cmbKeepLogNum.place(relx=0.244, rely=0.9, relwidth=0.269)

        self.style.configure('TcmdSaveLog.TButton', font=('宋体',9))
        self.cmdSaveLog = Button(self.frmLog, text='保存', command=self.cmdSaveLog_Cmd, style='TcmdSaveLog.TButton')
        self.cmdSaveLog.place(relx=0.576, rely=0.9, relwidth=0.18, relheight=0.061)

        self.scrVLog = Scrollbar(self.frmLog, orient='vertical')
        self.scrVLog.place(relx=0.909, rely=0.049, relwidth=0.047, relheight=0.684)

        self.style.configure('TcmdClearLog.TButton', font=('宋体',9))
        self.cmdClearLog = Button(self.frmLog, text='清空', command=self.cmdClearLog_Cmd, style='TcmdClearLog.TButton')
        self.cmdClearLog.place(relx=0.776, rely=0.9, relwidth=0.18, relheight=0.061)

        self.lstLogVar = StringVar(value='')
        self.lstLogFont = Font(font=('宋体',12))
        self.lstLog = Listbox(self.frmLog, listvariable=self.lstLogVar, yscrollcommand=self.scrVLog.set, font=self.lstLogFont)
        self.lstLog.place(relx=0.044, rely=0.049, relwidth=0.867, relheight=0.693)
        self.scrVLog['command'] = self.lstLog.yview

        self.style.configure('TlneUp.TSeparator', background='#C0C0C0')
        self.lneUp = Separator(self.frmLog, orient='horizontal', style='TlneUp.TSeparator')
        self.lneUp.place(relx=0.044, rely=0.851, relwidth=0.886, relheight=0.003)

        self.style.configure('TlneDown.TSeparator', background='#FFFFC0')
        self.lneDown = Separator(self.frmLog, orient='horizontal', style='TlneDown.TSeparator')
        self.lneDown.place(relx=0.044, rely=0.851, relwidth=0.886, relheight=0.0091)

        self.style.configure('TlblKeepLogNum.TLabel', anchor='w', font=('宋体',9))
        self.lblKeepLogNum = Label(self.frmLog, text='保留条目', style='TlblKeepLogNum.TLabel')
        self.lblKeepLogNum.place(relx=0.044, rely=0.9, relwidth=0.158, relheight=0.052)

        self.style.configure('TlblTimeToFinish.TLabel', anchor='w', font=('宋体',9))
        self.lblTimeToFinish = Label(self.frmLog, text='预计剩余时间：00:00:00', style='TlblTimeToFinish.TLabel')
        self.lblTimeToFinish.place(relx=0.51, rely=0.778, relwidth=0.446, relheight=0.052)

        self.style.configure('TlblQueueCmdNum.TLabel', anchor='w', font=('宋体',9))
        self.lblQueueCmdNum = Label(self.frmLog, text='剩余命令：0', style='TlblQueueCmdNum.TLabel')
        self.lblQueueCmdNum.place(relx=0.044, rely=0.778, relwidth=0.38, relheight=0.052)

        self.style.configure('TcmdCloseSerial.TButton', font=('宋体',9))
        self.cmdCloseSerial = Button(self.frmSerial, text='关闭', state='disabled', command=self.cmdCloseSerial_Cmd, style='TcmdCloseSerial.TButton')
        self.cmdCloseSerial.place(relx=0.687, rely=0.539, relwidth=0.202, relheight=0.281)

        self.cmbTimeOutList = ['1s x 10','1s x 30','1s x 60','1s x 120','3s x 5','3s x 10','3s x 30','3s x 60',]
        self.cmbTimeOutVar = StringVar(value='1s x 10')
        self.cmbTimeOut = Combobox(self.frmSerial, state='readonly', text='1s x 10', textvariable=self.cmbTimeOutVar, values=self.cmbTimeOutList, font=('宋体',9))
        self.cmbTimeOut.place(relx=0.244, rely=0.539, relwidth=0.38)

        self.style.configure('TcmdOpenSerial.TButton', font=('宋体',9))
        self.cmdOpenSerial = Button(self.frmSerial, text='打开', command=self.cmdOpenSerial_Cmd, style='TcmdOpenSerial.TButton')
        self.cmdOpenSerial.place(relx=0.687, rely=0.18, relwidth=0.202, relheight=0.281)

        self.cmbSerialList = ['COM1','COM2','COM3','COM4','COM5','COM6','COM6','COM7','COM8','COM9',]
        self.cmbSerialVar = StringVar(value='COM1')
        self.cmbSerial = Combobox(self.frmSerial, text='COM1', textvariable=self.cmbSerialVar, values=self.cmbSerialList, font=('宋体',9))
        self.cmbSerial.place(relx=0.244, rely=0.18, relwidth=0.38)

        self.style.configure('TlblTimeOut.TLabel', anchor='e', font=('宋体',9))
        self.lblTimeOut = Label(self.frmSerial, text='超时时间', style='TlblTimeOut.TLabel')
        self.lblTimeOut.place(relx=0.044, rely=0.539, relwidth=0.158, relheight=0.191)

        self.style.configure('TlblPortNo.TLabel', anchor='e', font=('宋体',9))
        self.lblPortNo = Label(self.frmSerial, text='端口号', style='TlblPortNo.TLabel')
        self.lblPortNo.place(relx=0.044, rely=0.18, relwidth=0.158, relheight=0.191)

class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        self.master.title('PrinterCnc Controller %s - https://github.com/cdhigh' % __Version__)
        self.cmbSerial.current(0)
        self.cmbTimeOut.current(3)
        self.cmbTimeOutVar.set('1s x 120')
        self.cmbKeepLogNum.current(1)
        self.cmbKeepLogNumVar.set('500')
        self.shiftX = self.shiftY = 0.0 #用于平移整个图案
        self.allowedMinX = self.allowedMinY = 3000.0 #如果存在小于此值的坐标，则全部坐标加上此值
        self.getConfigFromFile()
        self.txtSourceFile.focus_set()
        self.simulator = None
        self.ser = None
        self.serTimeout = 1 #为了更快的界面响应时间和需要的超时时间，总超时 timeout * cnt
        self.serTimeoutCnt = 120
        self.cmdQueue = Queue(0) #命令队列，不限大小
        self.evExit = Event()
        self.evExit.clear()
        self.evPause = Event()
        self.evPause.clear()
        self.evStop = Event()
        self.evStop.set()
        self.thread = Thread(target=self.threadSendCommand, 
            args=(self.evStop, self.evExit, self.evPause, self.cmdQueue,))
        self.thread.start()
        if self.shiftX != 0.0 or self.shiftY != 0.0:
            ret = askyesno('友情提醒', '告知：配置文件中的ShiftX/ShiftY设置值不等于零。\n\n如果不是每次绘图都需要平移整个图案，则建议设置为0.0\n\n现在需要恢复为0.0吗？')
            if ret:
                self.shiftX = self.shiftY = 0.0
        
    def getConfigFromFile(self):
        config = configparser.SafeConfigParser()
        cfgFilename = os.path.join(os.path.dirname(__file__), CFG_FILE)
        config.read(cfgFilename)
        try: #需要兼容2.x/3.x，API有些不一样，没办法，就需要那么多try/except
            timeout = config.get('Main', 'SerialTimeout')
        except:
            timeout = '1s x 120'
        if timeout in self.cmbTimeOutList:
            timeout = '1s x 120'
        self.cmbTimeOut.current(self.cmbTimeOutList.index(timeout))
        self.cmbTimeOutVar.set(timeout)
        
        try:
            self.txtXSpeedVar.set(config.get('Main', 'XAxisSpeed'))
        except:
            pass
        try:
            self.txtYSpeedVar.set(config.get('Main', 'YAxisSpeed'))
        except:
            pass
        try:
            self.txtZSpeedVar.set(config.get('Main', 'ZAxisSpeed'))
        except:
            pass
        try:
            self.txtZLiftStepsVar.set(config.get('Main', 'ZLiftSteps'))
        except:
            pass
        try:
            self.txtPenWidthVar.set(config.get('Main', 'PenDiameter'))
        except:
            pass
        try:
            self.cmbKeepLogNumVar.set(config.get('Main', 'KeepLogNum'))
        except:
            pass
        try:
            self.allowedMinX = config.getfloat('Main', 'MinimumX')
        except:
            pass
        try:
            self.allowedMinY = config.getfloat('Main', 'MinimumY')
        except:
            pass
        try:
            self.shiftX = config.getfloat('Main', 'ShiftX')
        except:
            pass
        try:
            self.shiftY = config.getfloat('Main', 'ShiftY')
        except:
            pass
        try:
            self.simulatorWidth = config.get('Simulator', 'Width')
        except:
            self.simulatorWidth = '200'
            
        if self.allowedMinX < 0.0:
            self.allowedMinX = 0.0
        if self.allowedMinY < 0.0:
            self.allowedMinY = 0.0
        
    def saveConfigToFile(self):
        cfgFilename = os.path.join(os.path.dirname(__file__), CFG_FILE)
        config = configparser.SafeConfigParser()
        config.add_section('Main')
        config.add_section('Simulator')
        config.set('Main', 'SerialTimeout', self.cmbTimeOutVar.get())
        config.set('Main', 'XAxisSpeed', self.txtXSpeedVar.get())
        config.set('Main', 'YAxisSpeed', self.txtYSpeedVar.get())
        config.set('Main', 'ZAxisSpeed', self.txtZSpeedVar.get())
        config.set('Main', 'ZLiftSteps', self.txtZLiftStepsVar.get())
        config.set('Main', 'PenDiameter', self.txtPenWidthVar.get())
        config.set('Main', 'KeepLogNum', self.cmbKeepLogNumVar.get())
        config.set('Main', 'MinimumX', '%.1f' % self.allowedMinX)
        config.set('Main', 'MinimumY', '%.1f' % self.allowedMinY)
        config.set('Main', 'ShiftX', '%.1f' % self.shiftX)
        config.set('Main', 'ShiftY', '%.1f' % self.shiftY)
        config.set('Simulator', 'Width', self.simulatorWidth)
        
        try:
            with open(cfgFilename, 'w') as configFile:
                config.write(configFile)
        except:
            pass
            
    #安全清理现场，优雅退出：在窗口关闭前先保证线程退出
    def EV_WM_DELETE_WINDOW(self, event=None):
        self.saveConfigToFile()
        self.evExit.set()
        self.evStop.set()
        self.cmdQueue.put_nowait('') #让队列醒来，以便线程优雅的自己退出
        self.cmdCloseSerial_Cmd()
        self.thread.join()
        self.master.destroy()
    
    #在手动下发命令文本框中按下了回车，则等效于按“发送”按钮
    def txtManualCommand_Return(self, event):
        self.cmdSendCommand_Cmd()
    
    def cmdChooseFile_Cmd(self, event=None):
        sf = tkFileDialog.askopenfilename(initialfile=self.txtSourceFileVar.get(), 
            filetypes=GerberFileMask())
        if sf:
            self.txtSourceFileVar.set(sf)
        
        #清除文件的XY最大值最小值信息
        self.txtMinXVar.set('')
        self.txtMaxXVar.set('')
        self.txtMinYVar.set('')
        self.txtMaxYVar.set('')
        
    def cmdStart_Cmd(self, event=None):
        #在开始前先设定当前位置为原点
        filename = self.txtSourceFileVar.get()
        if not filename:
            showinfo('注意啦', '你是不是好像忘了选择输入文件了？')
            return
        
        if not self.ser and not self.hasSimulator():
            showinfo('注意啦', '请先打开串口或模拟器！')
            return
            
        if isGerberFile(filename):
            self.cmdPause.focus_set()
            self.ProcessGerberFile(filename)
        else:
            showinfo('小弟不才', '暂不支持此类文件！')
    
    def cmdStartSimulator_Cmd(self, event=None):
        if not self.StartSimulator():
            showinfo('出错啦', '启动模拟器失败，请确认CncSimulator.py是否存在。')
            
    def cmdPause_Cmd(self, event=None):
        if (self.evPause.is_set()):
            self.evPause.clear()
            self.cmdPause['text'] = '暂停(P)'
        else:
            self.evPause.set()
            self.cmdPause['text'] = '恢复(P)'
        
    def cmdStop_Cmd(self, event=None):
        self.evPause.clear()
        self.evStop.set()
    
    def cmdZDown_Cmd(self, event=None):
        try:
            zLiftSteps = int(self.txtZLiftStepsVar.get())
        except:
            zLiftSteps = 0
        
        if not (0 < zLiftSteps <= 255):
            showinfo('出错啦', 'Z轴步进设置有误，要求为1-255的正整数')
            return
            
        self.SendCommand(('@z+%04d' % zLiftSteps).encode())
        
    def cmdZUp_Cmd(self, event=None):
        try:
            zLiftSteps = int(self.txtZLiftStepsVar.get())
        except:
            zLiftSteps = 0
        
        if not (0 < zLiftSteps <= 255):
            showinfo('出错啦', 'Z轴步进设置有误，要求为1-255的正整数')
            return
            
        self.SendCommand(('@z-%04d' % zLiftSteps).encode())
    
    def cmdZMicroUp_Cmd(self, event=None):
        self.SendCommand(b'@z-0020')
    
    def cmdZMicroDown_Cmd(self, event=None):
        self.SendCommand(b'@z+0020')
    
    def cmdXRight_Cmd(self, event=None):
        self.SendCommand(b'@x+1886')

    def cmdXLeft_Cmd(self, event=None):
        self.SendCommand(b'@x-1886')

    def cmdYDown_Cmd(self, event=None):
        self.SendCommand(b'@y+1886')

    def cmdYUp_Cmd(self, event=None):
        self.SendCommand(b'@y-1886')
    
    #打开串口
    def cmdOpenSerial_Cmd(self, event=None):
        try:
            timeout, timeoutCnt = self.cmbTimeOutVar.get().split('x')
            self.serTimeout = int(timeout.replace('s', '').strip())
            self.serTimeoutCnt = int(timeoutCnt.strip())
        except:
            self.serTimeout = 3
            self.serTimeoutCnt = 10
        
        try:
            self.ser = serial.Serial(self.cmbSerialVar.get(), 9600, timeout=self.serTimeout)
        except Exception as e:
            showerror('出错啦', str(e))
            self.ser = None
            self.cmdCloseSerial.config(state='disabled')
        else:
            self.cmdCloseSerial.config(state='normal')
            self.cmdOpenSerial.config(state='disabled')
    
    #关闭串口
    def cmdCloseSerial_Cmd(self, event=None):
        if self.ser:
            self.ser.close()
            self.ser = None
            self.cmdCloseSerial.config(state='disabled')
            self.cmdOpenSerial.config(state='normal')

    def cmdSendCommand_Cmd(self, event=None):
        cmd = self.txtManualCommandVar.get()
        if cmd:
            self.SendCommand(cmd.encode())
        
    def cmdClearLog_Cmd(self, event=None):
        self.lstLog.delete(0, END)
        
    def cmdSaveLog_Cmd(self, event=None):
        sf = tkFileDialog.asksaveasfilename(filetypes=[("Log File","*.log"),("Text File","*.txt"),("All Files", "*")])
        if sf:
            self.saveLogToFile(sf)
    
    def cmdResetX_Cmd(self, event=None):
        self.SendCommand(b'@reposx')

    def cmdResetY_Cmd(self, event=None):
        self.SendCommand(b'@reposy')

    def cmdResetZ_Cmd(self, event=None):
        self.SendCommand(b'@reposz')
    
    def cmdResetXYZ_Cmd(self, event=None):
        if not self.ser and not self.hasSimulator():
            showinfo('注意啦', '请先打开串口或模拟器然后再执行命令')
            return False
            
        self.cmdResetX_Cmd()
        self.cmdResetY_Cmd()
        self.cmdResetZ_Cmd()
        
    #设置控制板的XYZ轴运动速度，值越小运动越快，注意速度太快则扭矩下降，并有可能啸叫和丢步
    def cmdApplyAxisSpeed_Cmd(self, event=None):
        if not self.ser and not self.hasSimulator():
            showinfo('注意啦', '请先打开串口或模拟器然后再执行命令')
            return False
            
        xSpeed = self.txtXSpeedVar.get()
        ySpeed = self.txtYSpeedVar.get()
        zSpeed = self.txtZSpeedVar.get()
        zLiftSteps = self.txtZLiftStepsVar.get()
        try:
            xSpeed = int(xSpeed)
            ySpeed = int(ySpeed)
            zSpeed = int(zSpeed)
            zLiftSteps = int(zLiftSteps)
        except Exception as e:
            showinfo('出错啦', str(e))
            return
        
        if not (0 < zLiftSteps <= 255):
            showinfo('出错啦', 'Z轴步进要求为1-255的正整数')
            self.txtZLiftSteps.focus_set()
            return
        
        self.SendCommand(('@X%04d' % xSpeed).encode())
        self.SendCommand(('@Y%04d' % ySpeed).encode())
        self.SendCommand(('@Z%04d' % zSpeed).encode())
        self.SendCommand(('@ZL%03d' % zLiftSteps).encode())
    
    #分析文件，获取最小值和最大值
    def cmdUpdateMinMax_Cmd(self, event=None):
        filename = self.txtSourceFileVar.get()
        if not filename:
            showinfo('注意啦', '你不是好像忘了选择输入文件了？')
            return
        
        if isGerberFile(filename):
            gerber = self.ParseGerberFile(filename)
            if gerber:
                self.txtMinXVar.set('%06d' % gerber['minX'])
                self.txtMaxXVar.set('%06d' % gerber['maxX'])
                self.txtMinYVar.set('%06d' % gerber['minY'])
                self.txtMaxYVar.set('%06d' % gerber['maxY'])
            else:
                self.txtMinXVar.set('')
                self.txtMaxXVar.set('')
                self.txtMinYVar.set('')
                self.txtMaxYVar.set('')
        else:
            showinfo('小弟不才', '暂不支持此类文件！')
            
    #移动至左上角，用于确定打印区域
    def cmdMoveToLeftUp_Cmd(self, event=None):
        try:
            x = int(self.txtMinXVar.get())
            y = int(self.txtMinYVar.get())
        except:
            showinfo('出错啦', '请先更新文件信息。')
            return
        
        self.SendCommand(('x%06dy%06dz2' % (x, y)).encode())
        
    #移动至右上角，用于确定打印区域
    def cmdMoveToRightUp_Cmd(self, event=None):
        try:
            x = int(self.txtMaxXVar.get())
            y = int(self.txtMinYVar.get())
        except:
            showinfo('出错啦', '请先更新文件信息。')
            return
        
        self.SendCommand(('x%06dy%06dz2' % (x, y)).encode())
    
    #移动至左下角，用于确定打印区域
    def cmdMoveToLeftBottom_Cmd(self, event=None):
        try:
            x = int(self.txtMinXVar.get())
            y = int(self.txtMaxYVar.get())
        except:
            showinfo('出错啦', '请先更新文件信息。')
            return
        
        self.SendCommand(('x%06dy%06dz2' % (x, y)).encode())
    
    #移动至右上角，用于确定打印区域
    def cmdMoveToRightBottom_Cmd(self, event=None):
        try:
            x = int(self.txtMaxXVar.get())
            y = int(self.txtMaxYVar.get())
        except:
            showinfo('出错啦', '请先更新文件信息。')
            return
        
        self.SendCommand(('x%06dy%06dz2' % (x, y)).encode())
    
    #将命令压到队列中以供另一个线程取用，出错返回False
    def SendCommand(self, cmd, penWidth=None):
        self.evStop.clear()
        self.evPause.clear()
        try:
            state = self.simulator.state()
        except: #模拟器不存在则发送到实际控制板
            if self.ser:
                self.cmdQueue.put(cmd, block=True)
            else:
                showinfo('注意啦', '请先打开串口然后再执行命令')
                return False
        else:
            response = self.simulator.putDrawCmd(cmd, penWidth)
            self.AddCommandLog(cmd + b' -> sim')
            self.lstLog.update_idletasks()
            if response != b'*':
                if not askyesno('命令出错', '模拟器返回命令出错标识，是否继续下发其他命令？'):
                    return False
        
        return True
        
    def AddCommandLog(self, cmd, isResponse=False):
        if isResponse:
            self.lstLog.insert(END, b'                           ' + cmd)
        else:
            self.lstLog.insert(END, cmd)
        
        #删掉旧的数据，避免listbox速度更新缓慢
        try:
            keepNum = int(self.cmbKeepLogNumVar.get())
        except:
            keepNum = 1000
        
        #为了ListBox的操作效率，每超过期望保留的记录数的10%再统一删除一次老数据，并且多删10%
        #这样在ListBox中的数据条数就维持在期望数的正负10%之内
        tolerance = int(keepNum / 10)
        logNum = self.lstLog.size()
        if logNum > keepNum + tolerance:
            self.lstLog.delete(0, tolerance * 2)
        
        #ListBox界面刷新效率比较低，为效率考虑，每隔3行刷新一次
        if logNum % 3 == 0:
            self.lstLog.see(END)
            #self.lstLog.update_idletasks()
        
    #将命令和控制板的答复记录保存到文本文件
    def saveLogToFile(self, filename):
        try:
            with open(filename, 'w') as f:
                size = self.lstLog.size()
                for index in range(0, size):
                    txt =  self.lstLog.get(index)
                    f.write(txt + '\n')
        except Exception as e:
            showinfo('注意啦', '出错啦：\n\n%s' % str(e))
    
    #分析GERBER文件，获取文件头信息，将绘图命令行转换为浮点数，返回一个字典：出错返回None
    #{'header':{'xInteger':xx,'xDecimal':xx,'yInteger':xx,'yDecimal':xx,'zeroSuppress':xx,
    # 'unit':xx,'apertures':{}}, 'lines':[], 'minX':0.0, 'maxX':0.0, 'minY':0.0, 'maxY':0.0}
    def ParseGerberFile(self, filename):
        try:
            with open(filename, 'r') as f1:
                lines = [word.strip() for word in f1.read().split('\n') if word.strip()]
        except Exception as e:
            showerror('出错啦',str(e))
            return None
        
        if self.evExit.is_set():
            return None
        
        dictRet = {}
        #先读取gerber文件头的一些内嵌信息
        gerberInfo = {'xInteger':2,'xDecimal':5,'yInteger':2,'yDecimal':5,
            'zeroSuppress':'L', 'unit':'inch', 'apertures':{}, }
        for line in lines[:50]: #在前面50行获取元信息，一般足够了
            if line.startswith('G04'): #注释行
                continue
                
            #数字格式设定
            mat = re.match(r'^%FS([LTD]).*?X(\d\d)Y(\d\d).*', line)
            if mat:
                gerberInfo['zeroSuppress'] = mat.group(1)
                xFormat = mat.group(2)
                yFormat = mat.group(3)
                gerberInfo['xInteger'] = int(xFormat[0])
                gerberInfo['xDecimal'] = int(xFormat[-1])
                gerberInfo['yInteger'] = int(yFormat[0])
                gerberInfo['yDecimal'] = int(yFormat[-1])
            
            #单位设定
            if line.startswith('%MOIN*%'):
                gerberInfo['unit'] = 'inch'
            elif line.startswith('%MOMM*%'):
                gerberInfo['unit'] = 'mm'
            
            #Aperture定义
            apt = Aperture.GenAperture(line, gerberInfo['unit'])
            if apt:
                gerberInfo['apertures'][apt.name] = apt
        
        dictRet['header'] = gerberInfo
        
        #预处理文件内容，将绘图行转换为单位为微米的浮点数元祖，以便后续处理
        #并且如果需要，则经过数学处理去掉负数坐标和平移图案
        minX, maxX, minY, maxY = self.PreProcess(lines, gerberInfo)
        dictRet['lines'] = lines
        dictRet['minX'] = minX
        dictRet['maxX'] = maxX
        dictRet['minY'] = minY
        dictRet['maxY'] = maxY
        return dictRet
        
    #分析Gerber文件，将其中的绘图命令转换成CNC合法的命令发送
    def ProcessGerberFile(self, filename):
        gerber = self.ParseGerberFile(filename)
        
        if self.evExit.is_set() or gerber is None:
            return
        
        self.evStop.clear()
        self.evPause.clear()
        self.cmdPause['text'] = '暂停(P)'
        while (True): #清空队列
            try:
                tmp = self.cmdQueue.get_nowait()
            except Exception as e:
                break
            
        #获取笔尖宽度，界面上的单位是毫米，软件需要转换为微米
        try:
            penWidth = float(self.txtPenWidthVar.get()) * 1000.0
        except:
            penWidth = 1000.0 #默认1毫米
        if penWidth < 100: #太小没意思，默认最小为0.1mm
            penWidth = 100
        
        #开始逐行处理文件
        grblApt = re.compile(r'^.*?D(\d+?)\*') #aperture切换行
        x = y = prevX = prevY = 0.0
        curAperture = defAperture = Aperture() #新建一个默认大小的Aperture
        lines = gerber['lines']
        
        self.cmdApplyAxisSpeed_Cmd() #更新控制板的各轴速度和Z轴步进
        
        for lineNo, line in enumerate(lines, 1):
            if self.evExit.is_set():
                return
            
            if type(line) is tuple: #坐标行
                x, y, z = line
                
                #如果需要，可能需要画多根细线组成粗线
                #返回一个元组列表[(x1,y1,z1),(x2,y2,z2),...]
                if z == '2': #直接移动绘图笔的命令
                    lines2draw = [(x, y, z)]
                elif curAperture:
                    lines2draw = curAperture.Render(prevX, prevY, x, y, z, penWidth)
                else:
                    showinfo('出错啦', 'Gerber文件有错，还没有设置Aperture就开始绘图了[第 %d 行]！' % lineNo)
                    return
                    
                for x, y, z in lines2draw:
                    #一条斜线，雕刻机不支持直接画斜线，要用一系列的横线竖线逼近
                    if (z == '1') and (x != prevX) and (y != prevY):
                        for point in self.SplitInclined(prevX, prevY, x, y):
                            out = 'x%06.0fy%06.0fz%s' % (point[0], point[1], z)
                            ret = self.SendCommand(out.encode(), penWidth)
                            if not ret:
                                return
                    else:
                        out = 'x%06.0fy%06.0fz%s' % (x, y, z)
                        ret = self.SendCommand(out.encode(), penWidth)
                        if not ret:
                            return
                    
                    prevX = x
                    prevY = y
            elif not line.startswith('G04'): #跳过注释行
                mat = grblApt.match(line)
                if mat: #aperture切换行
                    try:
                        aptNum = int(mat.group(1))
                    except:
                        showinfo('出错啦', '解读文件时出现aperture编号出错的情况 [第 %d 行]' % lineNo)
                        return
                    
                    if aptNum == 3: #在当前点绘aperture命令
                        if not curAperture:
                            showinfo('出错啦', '没有设置aperture就开始绘图！ [第 %d 行]' % lineNo)
                            continue #忽略好了，不用退出
                        
                        lines2draw = curAperture.Render(prevX, prevY, prevX, prevY, '3', penWidth)
                        for x, y, z in lines2draw:
                            #一条斜线，雕刻机不支持直接画斜线，要用一系列的横线竖线逼近
                            if (z == '1') and (x != prevX) and (y != prevY):
                                for point in self.SplitInclined(prevX, prevY, x, y):
                                    out = 'x%06.0fy%06.0fz%s' % (point[0], point[1], z)
                                    ret = self.SendCommand(out.encode(), penWidth)
                                    if not ret:
                                        return
                            else:
                                out = 'x%06.0fy%06.0fz%s' % (x, y, z)
                                ret = self.SendCommand(out.encode(), penWidth)
                                if not ret:
                                    return
                            prevX = x
                            prevY = y
                        
                    elif aptNum >= 10: #切换当前的aperture    
                        aptName = 'D%d' % aptNum
                        curAperture = gerber['header']['apertures'].get(aptName, defAperture)
        
                
        self.SendCommand(b'x000000y000000z2', penWidth) #归位
        
        #完成后尝试发声提醒
        SoundNotify(False)
        
    
    #将RS274X坐标字符串格式的xy转换成浮点型（单位为微米），支持正负数，返回转换后的(x,y)元组
    def XY2Float(self, x, y, gerberInfo):
        xIsNegative = False
        yIsNegative = False
        
        #先去零
        #if (gerberInfo['zeroSuppress'] == 'L'): #忽略前导零
        #    x = x.lstrip('0 ')
        #    y = y.lstrip('0 ')
        if (gerberInfo['zeroSuppress'] == 'T'): #忽略后导零
            x = x.rstrip('0 ')
            y = y.rstrip('0 ')
        
        try:
            x = int(x)
            y = int(y)
        except:
            return (None, None)
        
        #加小数点
        x /= pow(10, gerberInfo['xDecimal'])
        y /= pow(10, gerberInfo['yDecimal'])
        
        #转换成微米
        if gerberInfo['unit'] == 'inch':
            x = float(x) * 25.4 * 1000
            y = float(y) * 25.4 * 1000
        else: #mm
            x = float(x) * 1000
            y = float(y) * 1000
        
        return (x, y)
        
    
    #因为PIC控制板不支持负的坐标，为此，预处理文件，如果文件中有负坐标，
    #则所有坐标都加上一个最小的负数，把所有坐标都变成正数
    #即使没有负数，如果有太小的值，也可以考虑加上一个固定的值，避免运算过程中出现负数
    #经过预处理后的文件行列表直接在lines中返回，同时函数返回最大最小值（可以用于定框）
    def PreProcess(self, lines, gerberInfo):
        minX = minY = maxX = maxY = 0.0
        
        #开始逐行处理文件，
        #要遍历两次文件内容，第一遍用于确定是否有负数，最小负数是多少，第二遍改写文件内容
        linesNum = [] #存储中间结果的列表，每个元素为(x,y,z)或原始字符串
        grblExp = re.compile(r'^X([+-]{0,1}\d+?)Y([+-]{0,1}\d+?)D0([123])\*')
        firstLine = True
        for line in lines:
            line = line.strip()
            if line.startswith('G04'): #注释行
                continue
                
            mat = grblExp.match(line)
            if mat: #坐标绘图行
                x, y = self.XY2Float(mat.group(1), mat.group(2), gerberInfo)
                z = mat.group(3)
                
                if x is None or y is None:
                    continue
                    
                #平移整个图案
                x += self.shiftX
                y += self.shiftY
                
                if firstLine:
                    minX = maxX = x
                    minY = maxY = y
                    firstLine = False
                else:
                    if x < minX:
                        minX = x
                    if x > maxX:
                        maxX = x
                    if y < minY:
                        minY = y
                    if y > maxY:
                        maxY = y
                
                linesNum.append((x, y, z))
            else:
                linesNum.append(line)
        
        
        #进行第二遍处理，为了避免画粗线或焊盘时越限，可允许的最小值有限制
        minXforCal = self.allowedMinX - minX if minX < self.allowedMinX else 0.0
        minYforCal = self.allowedMinY - minY if minY < self.allowedMinY else 0.0
        
        for idx, line in enumerate(linesNum):
            if type(line) is tuple: #坐标行，则将坐标转换为不小于3mm的正浮点数
                lines[idx] = (line[0] + minXforCal, line[1] + minYforCal, line[2])
            else:
                lines[idx] = line
                
        return (minX + minXforCal, maxX + minXforCal, minY + minYforCal, maxY + minYforCal)
        
    #将斜线分解转换成很多段的水平线和垂直线序列，因为雕刻机仅支持画水平线或垂直线
    #函数直接返回一个元祖列表[(x1,y1),(x2,y2),...]
    #参数坐标单位为微米，(x1,y1)为起始点，(x2,y2)为结束点
    def SplitInclined(self, x1, y1, x2, y2):
        if x1 == x2 or y1 == y2:
            return [(x2,y2)]
        
        x_half = abs(x1 - x2) / 2
        y_half = abs(y1 - y2) / 2
        xm = min(x1, x2) + x_half
        ym = min(y1, y2) + y_half
        if (x_half < 100) or (y_half < 100): #逼近的精度取100微米即可，够平滑了，太多了也没必要
            if (x_half < y_half): #根据斜率决定先向哪个方向逼近
                return [(x1,ym),(x2,ym),(x2,y2)]
            else:
                return [(xm,y1),(xm,y2),(x2,y2)]
        else: #递归二分法逼近
            return self.SplitInclined(x1, y1, xm, ym) + self.SplitInclined(xm, ym, x2, y2)
        
    #单独的一个线程，在队列中取命令，然后发送给CNC控制板，并且等待控制板的答复
    def threadSendCommand(self, evStop, evExit, evPause, cmdQueue):
        #时间单位为毫秒
        timeToFinish = timeForLast100 = avgForLast100 = sumedCmdNum = 0
        cmdStartTime = cmdEndTime = None
        remainedCmd = 0
        
        while (True):
            if evExit.is_set():
                return
            elif evPause.is_set(): #暂停后暂时不到队列中取命令
                time.sleep(0.1) #睡0.1s先
                continue
            
            try:
                cmd = cmdQueue.get(block=True)
            except Exception as e:
                cmd = None
            
            if evExit.is_set():
                return
            
            remainedCmd = self.cmdQueue.qsize()
            self.lblQueueCmdNum['text'] = '剩余命令：%d' % remainedCmd
            
            if not cmd:
                time.sleep(0.1) #出错了或队列空，睡0.1s先
                continue
            elif evStop.is_set(): #按停止键后需要清空队列
                cmdQueue.queue.clear()
                self.lblQueueCmdNum['text'] = '剩余命令：0'
                self.lblTimeToFinish['text'] = '预计剩余时间：00:00:00'
                continue
            
            cmdStartTime = datetime.datetime.now()
            try:
                self.ser.write(cmd)
            except Exception as e:
                self.AddCommandLog(('Err Write: %s' % cmd).encode())
                
            self.AddCommandLog(cmd)
            
            cnt = 0
            while (cnt < self.serTimeoutCnt):
                response = b''
                try:
                    response = self.ser.read()
                except Exception as e:
                    pass
                
                if evExit.is_set():
                    return #退出线程，线程销毁
                    
                cnt += 1
                if ((response == b'*') or (response == b'#')):
                    break
                
                if evPause.is_set() or evStop.is_set():
                    break
            
            if evPause.is_set() or evStop.is_set():
                continue
                
            if response:
                self.AddCommandLog(response, True)
                if response == b'#':
                    ignore = askyesno('命令错', '控制板返回命令执行出错标识，是否继续下发其他命令？')
                    if not ignore:
                        evStop.set()
                    
            else:
                self.AddCommandLog(b'Timeout', True)
                SoundNotify()
                ignore = askyesno('答复超时', '控制板未响应，是否继续下发其他命令？')
                if not ignore:
                    evStop.set()
                    
            #确定此命令的执行时间，统计最近100个命令的执行时间，用于预计剩余时间
            cmdEndTime = datetime.datetime.now()
            delta = cmdEndTime - cmdStartTime
            delta = delta.seconds * 1000 + delta.microseconds / 1000 #转换成毫秒
            if sumedCmdNum < 100:
                timeForLast100 += delta
                sumedCmdNum += 1
                self.lblTimeToFinish['text'] = '预计剩余时间：00:00:00'
            else:
                if avgForLast100 == 0:
                    avgForLast100 = timeForLast100 / 100
                
                timeForLast100 = timeForLast100 + delta - avgForLast100
                avgForLast100 = timeForLast100 / 100
                timeToFinish = avgForLast100 * remainedCmd
                
                #毫秒转换为 小时:分钟:秒 格式
                hours = int(timeToFinish / 3600000)
                odd = int(timeToFinish % 3600000)
                minutes = int(odd / 60000) 
                seconds = int(int((odd % 60000) / 1000) / 10) * 10 #圆整为10整数倍，避免界面刷新太多
                
                self.lblTimeToFinish['text'] = '预计剩余时间：%02d:%02d:%02d' % (hours, minutes, seconds)
    
    #启动模拟器，返回启动是否成功的标志
    def StartSimulator(self):
        try:
            import CncSimulator
        except ImportError:
            return False
        
        hasSim = False
        state = None
        if self.simulator:
            try:
                state = self.simulator.state()
            except:
                pass
            else:
                hasSim = True
            
            if state == 'iconic' or state == 'withdrawn':
                self.simulator.deiconify()
        
        if not hasSim:
            self.simulator = CncSimulator.Application(Toplevel())
            self.simulator.setSimulatorWidth(self.simulatorWidth)
            self.simulator.mainloop()
        
        return True
    
    #判断模拟器是否有效
    def hasSimulator(self):
        try:
            state = self.simulator.state()
        except:
            return False
        else:
            return True
        
#一个Gerber的Aperture定义，用于画粗线或焊盘等信息
class Aperture:
    Circle = 0
    Rectangle = 1
    Obround = 2
    Polygon = 3
    def __init__(self):
        self.name = '' #类似D10
        self.type_ = self.Circle
        self.outerEdge1 = 0.0 #对于圆来说，outerEdge2==0
        self.outerEdge2 = 0.0
        self.innerEdge1 = 0.0 #如果innerEdge1==0，则是实心的，否则innerEdge2==0表明是圆
        self.innerEdge2 = 0.0
        self.angle = 0.0
    
    #判断行是否是aperture定义，如果是，则返回一个aperture实例，否则返回none
    @classmethod
    def GenAperture(cls, line, unit):
        #Aperture定义
        mat = re.match(r'^%AD(D\d+?)([CROP]) *?, *?(.*?)\*%', line)
        if mat:
            inst = Aperture()
            inst.name = mat.group(1)
            type_ = mat.group(2)
            mod = mat.group(3)
            mods = []
            for m in mod.split('X'):
                m = m.strip()
                if not m:
                    continue
                    
                if m.startswith('.'):
                    m = '0' + m
                
                #转换成微米
                if unit == 'inch':
                    mods.append(float(m) * 25.4 * 1000)
                else:
                    mods.append(float(m) * 1000)
                
            if type_ == 'C': #圆形 %ADD10C,.025*%  ｜ %ADD10C,0.5X0.25*%  ｜ %ADD10C,0.5X0.29X0.29*%
                inst.type_ = cls.Circle
                inst.outerEdge1 = mods[0]
                if len(mods) > 2: #空心圆
                    inst.innerEdge2 = mods[2]
                if len(mods) > 1:
                    inst.innerEdge1 = mods[1]
            elif type_ == 'R': #矩形 %ADD22R,0.044X0.025*%  %ADD22R,0.044X0.025X0.019*% %ADD22R,0.044X0.025X0.024X0.013*%
                inst.type_ = cls.Rectangle
                if len(mods) < 2:
                    return None
                inst.outerEdge1 = mods[0]
                inst.outerEdge2 = mods[1]
                if len(mods) > 3:
                    inst.innerEdge2 = mods[3]
                if len(mods) > 2:
                    inst.innerEdge1 = mods[2]
            elif type_ == 'O': #矩形椭圆
                inst.type_ = cls.Obround
                inst.outerEdge1 = mods[0]
                inst.outerEdge2 = mods[1]
                if len(mods) > 3:
                    inst.innerEdge2 = mods[3]
                if len(mods) > 2:
                    inst.innerEdge1 = mods[2]
            else: #'P' 多边形
                inst.type_ = cls.Polygon
                inst.outerEdge1 = mods[0] #外切圆直径
                #多边形的边数要从微米恢复到原始数
                if unit == 'inch':
                    inst.outerEdge2 = int(mods[1] / (25.4 * 1000))
                else:
                    inst.outerEdge2 = int(mods[1] / 1000)
                if inst.outerEdge2 < 3: #多边形最少为三条边
                    return None
                    
                if len(mods) > 4:
                    inst.innerEdge2 = mods[4] #内孔边长
                if len(mods) > 3:
                    inst.innerEdge1 = mods[3] #内孔直径或边长
                if len(mods) > 2:
                    inst.angle = mods[2] #旋转角度
                
            return inst
    
    #根据当前的Aperture生成画线序列，因笔尖直径有限，所以粗线则需要画多次才行
    #返回一个元组列表[(x1,y1,z1),(x2,y2,z2),...]
    def Render(self, prevX, prevY, x, y, z, penWidth):
        lineWidth = penWidth
        if self.type_ in (self.Circle, self.Polygon):
            lineWidth = self.outerEdge1
        elif self.type_ == self.Rectangle:
            lineWidth = max(self.outerEdge1, self.outerEdge2)
        else:
            lineWidth = min(self.outerEdge1, self.outerEdge2)
        
        tmpPrevX = tmpPrevY = -1
        res = []
        if z == '2': #单纯的移动画笔
            return [(x, y, z)]
        elif z == '1': #画线命令
            if lineWidth <= penWidth: #线比较细，则走一次笔即可
                return [(x, y, z)]
                
            for line in self.RenderLine(prevX, prevY, x, y, lineWidth, penWidth):
                #优化走笔，如果上次的终点等于这次的起点，则不用升起笔了
                if tmpPrevX != line[0] or tmpPrevY != line[1]:
                    res.append((line[0], line[1], '2')) #升起笔，移动到线始点
                res.append((line[2], line[3], '1')) #降下笔，画线到线终点
                tmpPrevX = line[2]
                tmpPrevY = line[3]
            
            #因为上面的处理有优化走笔过程，在画完后有可能笔不在终点，
            #所以画完后坐标要回到原先的终点，以便下一个绘图不会移位
            res.append((x, y, '2'))
            
            return res
        else:  #==3，在当前坐标复制当前aperture形状
            for line in self.RenderMyself(x, y, penWidth):
                #优化走笔，如果上次的终点等于这次的起点，则不用升起笔了
                if tmpPrevX != line[0] or tmpPrevY != line[1]:
                    res.append((line[0], line[1], '2')) #升起笔，移动到线始点
                res.append((line[2], line[3], '1')) #降下笔，画线到线终点
                tmpPrevX = line[2]
                tmpPrevY = line[3]
            
            #画完后坐标要回到中心点，以便下一个绘图不会移位
            res.append((x, y, '2'))
            
            return res
        
    #根据x1,y1,x2,y2,wp,w生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #x1,y1,x2,y2:起点和终点坐标（微米）
    #penWidth：笔尖宽度（微米）
    #lineWidth:需要的线宽（微米）
    #画水平线和垂直线是优化的，所以建议尽量采用水平线和垂直线
    def RenderLine(self, x1, y1, x2, y2, lineWidth, penWidth):
        #水平线
        if y2 == y1:
            return self.RenderHorizontal(x1, y1, x2, y2, lineWidth, penWidth)
        elif x1 == x2: #垂直线
            return self.RenderVertical(x1, y1, x2, y2, lineWidth, penWidth)
        else: #普通斜线
            return self.RenderInclined(x1, y1, x2, y2, lineWidth, penWidth)
    
    #根据x1,y1,x2,y2,wp,w生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #处理任意宽度的水平线，从最上面一根线开始，每隔wp*2/3再画一根，一直到不超过wl为止
    def RenderHorizontal(self, x1, y1, x2, y2, lineWidth, penWidth):
        lineHalf = lineWidth / 2
        penHalf = penWidth / 2
        penStep = penWidth * 2 / 3 #为了尽量不要留隙，两次之间的间隔稍小于笔宽
        yStart = y1 - lineHalf + penHalf
        yEnd = y1 + lineHalf - penHalf
        alphaStep = ANGLE_PER_SIDE
        if x1 < x2:
            #如果线太短，短于笔尖直径，则点一个点即可
            if x2 - x1 <= penWidth:
                meio = int(x1 + (x2 - x1) / 2)
                return [(meio, y1, meio, y2)]
                
            xStart = xLeft = x1 + penHalf
            xEnd = xRight = x2 - penHalf
            alphaStart = 0.0 #定义顺时针角度增加，垂直向上为0度
        else:
            #如果线太短，短于笔尖直径，则点一个点即可
            if x1 - x2 <= penWidth:
                meio = int(x2 + (x1 - x2) / 2)
                return [(meio, y1, meio, y2)]
                
            xStart = xRight = x1 - penHalf
            xEnd = xLeft = x2 + penHalf
            alphaStart = math.pi * 2
            alphaStep = -alphaStep
        
        radius = lineHalf - penHalf
        
        #先画外框
        #第一根线
        res = [(xStart, yStart, xEnd, yStart),]
        #半圆
        tmpPrevX = xEnd
        tmpPrevY = yStart
        if self.type_ != self.Rectangle:
            if radius <= penHalf: #半径太小了，则仅在端点点一个点即可
                res.append((xEnd, y1, xEnd, y2))
            else:
                alpha = alphaStart
                while abs(alpha - alphaStart) <= math.pi:
                    deltaX = radius * math.sin(alpha)
                    deltaY = radius * math.cos(alpha)
                    currX = xEnd + deltaX
                    currY = y1 - deltaY
                    res.append((tmpPrevX, tmpPrevY, currX, currY))
                    tmpPrevX = currX
                    tmpPrevY = currY
                    alpha += alphaStep
                res.append((tmpPrevX, tmpPrevY, xEnd, yEnd))
        else: #如果Aperture是矩形，则不画两端的半圆
            res.append((xEnd, yStart, xEnd, yEnd))
        
        res.append((xEnd, yEnd, xStart, yEnd)) #第二根线
        #另一个半圆
        if self.type_ != self.Rectangle:
            if radius <= penHalf: #半径太小了，则仅在端点点一个点即可
                res.append((xStart, y1, xStart, y2))
            else:
                tmpPrevX = xStart
                tmpPrevY = yEnd
                while abs(alpha - alphaStart) <= math.pi * 2:
                    deltaX = radius * math.sin(alpha)
                    deltaY = radius * math.cos(alpha)
                    currX = xStart + deltaX
                    currY = y1 - deltaY
                    res.append((tmpPrevX, tmpPrevY, currX, currY))
                    tmpPrevX = currX
                    tmpPrevY = currY
                    alpha += alphaStep
                res.append((tmpPrevX, tmpPrevY, xStart, yStart))
        else:
            res.append((xStart, yEnd, xStart, yStart))
        
        if radius <= penHalf: #半径太小则不需要填充内部
            return res
            
        #填充内部
        left2right = 1 #用于优化走笔路线
        y = yStart + penStep
        if self.type_ != self.Rectangle:
            if radius > penHalf:
                radius -= penHalf
            while (y < yEnd): #填充内部
                cosDeltaY = (radius + penHalf - (y - yStart)) / radius
                alpha = math.acos(cosDeltaY if cosDeltaY > -1.0 else -1.0) #避免浮点计算误差
                deltaX = radius * math.sin(alpha)
                if xStart < xEnd: #从左至右的直线
                    currX1 = xStart - deltaX
                    currX2 = xEnd + deltaX
                else:
                    currX1 = xStart + deltaX
                    currX2 = xEnd - deltaX
                if left2right:
                    res.append((currX1, y, currX2, y))
                    left2right = 0
                else:
                    res.append((currX2, y, currX1, y))
                    left2right = 1
                y += penStep
        else:
            while (y < yEnd): #填充内部
                if left2right:
                    res.append((xStart, y, xEnd, y))
                    left2right = 0
                else:
                    res.append((xEnd, y, xStart, y))
                    left2right = 1
                y += penStep
            
        return res
    
    #根据x1,y1,x2,y2,lineWidth,penWidth生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #处理任意宽度的垂直线，从最左边一根线画起，每隔wp*2/3再画一根，一直到不超过wl为止
    def RenderVertical(self, x1, y1, x2, y2, lineWidth, penWidth):
        lineHalf = lineWidth / 2
        penHalf = penWidth / 2
        penStep = penWidth * 2 / 3 #为了尽量不要留隙，两次之间的间隔稍小于笔宽
        xStart = x1 - lineHalf + penHalf
        xEnd = x1 + lineHalf - penHalf
        alphaStep = ANGLE_PER_SIDE
        if y1 < y2: #从上至下
            #如果线太短，短于笔尖直径，则点一个点即可
            if y2 - y1 < penWidth:
                meio = int(y1 + (y2 - y1) / 2)
                return [(x1, meio, x2, meio)]
                
            yStart = yTop = y1 + penHalf
            yEnd = yBottom = y2 - penHalf
            alphaStart = 0.0 #定义逆时针角度增加，水平向左为0度
        else:
            #如果线太短，短于笔尖直径，则点一个点即可
            if y1 - y2 < penWidth:
                meio = int(y2 + (y1 - y2) / 2)
                return [(x1, meio, x2, meio)]
                
            yStart = yBottom = y1 - penHalf
            yEnd = yTop = y2 + penHalf
            alphaStart = math.pi * 2
            alphaStep = -alphaStep #顺时针
        
        radius = lineHalf - penHalf
        
        #先画外框
        #第一根线
        res = [(xStart, yStart, xStart, yEnd),]
        
        #半圆
        tmpPrevX = xStart
        tmpPrevY = yEnd
        if self.type_ != self.Rectangle:
            if radius <= penHalf: #半径太小了，则仅在端点点一个点即可
                res.append((x1, yEnd, x2, yEnd))
            else:
                alpha = alphaStart
                while abs(alpha - alphaStart) <= math.pi:
                    deltaX = radius * math.cos(alpha)
                    deltaY = radius * math.sin(alpha)
                    currX = x1 - deltaX
                    currY = yEnd + deltaY
                    res.append((tmpPrevX, tmpPrevY, currX, currY))
                    tmpPrevX = currX
                    tmpPrevY = currY
                    alpha += alphaStep
                res.append((tmpPrevX, tmpPrevY, xEnd, yEnd))
        else:
            res.append((xStart, yEnd, xEnd, yEnd))
        
        res.append((xEnd, yEnd, xEnd, yStart)) #第二根线
        #另一个半圆
        if self.type_ != self.Rectangle:
            if radius <= penHalf: #半径太小了，则仅在端点点一个点即可
                res.append((x1, yStart, x2, yStart))
            else:
                tmpPrevX = xEnd
                tmpPrevY = yStart
                while abs(alpha - alphaStart) <= math.pi * 2:
                    deltaX = radius * math.cos(alpha)
                    deltaY = radius * math.sin(alpha)
                    currX = x1 - deltaX
                    currY = yStart + deltaY
                    res.append((tmpPrevX, tmpPrevY, currX, currY))
                    tmpPrevX = currX
                    tmpPrevY = currY
                    alpha += alphaStep
                res.append((tmpPrevX, tmpPrevY, xStart, yStart))
            
        else:
            res.append((xEnd, yStart, xStart, yStart))
        
        if radius <= penHalf: #半径太小，两根线已经重叠，不需要填充内部了
            return res
        
        #填充内部
        top2bottom = 1 #用于优化走笔路线
        x = xStart + penStep
        if self.type_ != self.Rectangle:
            if radius > penHalf:
                radius -= penHalf
            while (x < xEnd): #填充内部
                sinDeltaX = (radius + penHalf - (x - xStart)) / radius
                alpha = math.asin(sinDeltaX if sinDeltaX > -1.0 else -1.0) #避免浮点计算误差
                deltaY = radius * math.cos(alpha)
                if yStart < yEnd: #从上至下的直线
                    currY1 = yStart - deltaY
                    currY2 = yEnd + deltaY
                else:
                    currY1 = yStart + deltaY
                    currY2 = yEnd - deltaY
                if top2bottom:
                    res.append((x, currY1, x, currY2))
                    top2bottom = 0
                else:
                    res.append((x, currY2, x, currY1))
                    top2bottom = 1
                x += penStep
        else:
            while (x < xEnd):
                if top2bottom:
                    res.append((x, yStart, x, yEnd))
                    top2bottom = 0
                else:
                    res.append((x, yEnd, x, yStart))
                    top2bottom = 1
                x += penStep
                
        return res
    
    #根据x1,y1,x2,y2,wp,w生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #处理任意宽度的斜线，要使用到简单三角函数
    #因为斜线一般都是和另一根水平线、垂直线或焊盘相连，所以不需要再画两端的半圆了。
    def RenderInclined(self, x1, y1, x2, y2, wl, wp):
        wl_half = wl / 2
        wp_half = wp / 2
        res = []
        
        #判断向左倾还是向右倾
        inclined_right = 0
        if ((x2 > x1) and (y2 > y1)) or ((x2 < x1) and (y2 < y1)):
            inclined_right = 1
            
        #斜线和水平的夹角(弧度)
        alpha = math.atan(abs(y2 - y1) / abs(x2 - x1))
        sin_alpha = math.sin(alpha)
        cos_alpha = math.cos(alpha)
        delta_x = sin_alpha * (wl_half - wp_half)
        delta_y = cos_alpha * (wl_half - wp_half)
        x1p = x1p_start = x1 - delta_x
        x2p = x2p_start = x2 - delta_x
        if inclined_right:
            y1p = y1p_start = y1 + delta_y
            y2p = y2p_start = y2 + delta_y
        else:
            y1p = y1p_start = y1 - delta_y if y1 - delta_y > 0 else 0
            y2p = y2p_start = y2 - delta_y if y2 - delta_y > 0 else 0
        wp_sin_alpha = (wp * 2 / 3) * sin_alpha #斜线的X步进
        wp_cos_alpha = (wp * 2 / 3) * cos_alpha #斜线的Y步进
        left2right = 1
        while  (x1p - x1p_start <= (wl - wp) * sin_alpha):
            if left2right:
                res.append((x1p, y1p, x2p, y2p))
                left2right = 0
            else:
                res.append((x2p, y2p, x1p, y1p))
                left2right = 1
            
            x1p += wp_sin_alpha
            x2p += wp_sin_alpha
            if inclined_right: #步进要分左倾斜线还是右倾斜线
                y1p -= wp_cos_alpha
                y2p -= wp_cos_alpha
                if y1p <= 0:
                    y1p = 0
                if y2p <= 0:
                    y2p = 0
            else:
                y1p += wp_cos_alpha
                y2p += wp_cos_alpha
                
        return res
    
    #在特定点上画一个aperture（焊盘或特殊形状）
    #根据x,y,penWidth生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #x,y:要画Aperture坐标（微米）
    #penWidth：笔尖宽度（微米）
    def RenderMyself(self, x, y, penWidth):
        if self.type_ == self.Circle: #画圆形
            return self.RenderCircle(x, y, penWidth)
        elif self.type_ == self.Rectangle: #画矩形
            return self.RenderRectangle(x, y, penWidth)
        elif self.type_ == self.Obround: #画矩形椭圆（长条型）
            return self.RenderObround(x, y, penWidth)
        elif self.type_ == self.Polygon: #多边形
            return self.RenderPolygon(x, y, penWidth)
        else:
            return []
    
    #在特定点上画一个圆形（可能为实心圆，或空心圆）
    #根据x,y,penWidth生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #x,y:要画圆的圆心坐标（微米）
    #penWidth：笔尖宽度（微米）
    #当前暂不支持外圆内方焊盘
    def RenderCircle(self, x, y, penWidth):
        #画圆的方法实际上是将圆微分成和圆内切的正多边形处理，如果边数够多，正多边形就是"圆"了。
        #从外圆开始画起，每隔penWidth * 2 /3 逐步缩小，一直画到内圆或直径小于penWidth / 2为止
        if self.outerEdge1 <= penWidth: #直径太小，笔太粗，简直没法画了，只能下降笔，点到为止
            return [(x, y, x, y)]
            
        penHalf = penWidth / 2
        radius = self.outerEdge1 / 2 - penHalf
        innerRadius = self.innerEdge1 / 2 + penHalf
        radiusStep = penWidth * 2 / 3
        res = []
        pi2 = math.pi * 2
        while (radius >= innerRadius):
            #开始点，从最左端开始，绕圆心一周
            prevX = currX = x - radius
            prevY = currY = y
            alpha = 0.0 #和左水平线的弧度
            while (alpha <= pi2):
                currX = x - radius * math.cos(alpha)
                currY = y - radius * math.sin(alpha)
                
                res.append((prevX, prevY, currX, currY))
                alpha += ANGLE_PER_SIDE
                prevX = currX
                prevY = currY
                
            res.append((prevX, prevY, x - radius, y)) #封口
            radius -= radiusStep
        
        return res
        
    #在特定点上画一个矩形（可能为实心，或空心）
    #根据x,y,penWidth生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #x,y:要画矩形的坐标（微米）
    #penWidth：笔尖宽度（微米）
    def RenderRectangle(self, x, y, penWidth):
        penHalf = penWidth / 2
        fillStep = penWidth * 2 / 3
        xEdgeHalf = self.outerEdge1 / 2 - penHalf
        yEdgeHalf = self.outerEdge2 / 2 - penHalf
        xEdgeLeft = x - xEdgeHalf
        xEdgeRight = x + xEdgeHalf
        yEdgeTop = y - yEdgeHalf
        yEdgeBottom = y + yEdgeHalf
        
        #先画一个外框
        res = [(xEdgeLeft, yEdgeTop, xEdgeRight, yEdgeTop),
                (xEdgeRight, yEdgeTop, xEdgeRight, yEdgeBottom),
                (xEdgeRight, yEdgeBottom, xEdgeLeft, yEdgeBottom),
                (xEdgeLeft, yEdgeBottom, xEdgeLeft, yEdgeTop),]
        
        #填充
        left2right = 1
        yFill = yEdgeTop + fillStep
        if self.innerEdge1 == 0.0: #实心矩形
            while yFill < yEdgeBottom:
                if left2right:
                    res.append((xEdgeLeft, yFill, xEdgeRight, yFill))
                    left2right = 0
                else:
                    res.append((xEdgeRight, yFill, xEdgeLeft, yFill))
                    left2right = 1
                yFill += fillStep
        elif self.innerEdge2 == 0.0: #外方内圆
            while yFill < y - self.innerEdge1 / 2 - penHalf: #上半部
                if left2right:
                    res.append((xEdgeLeft, yFill, xEdgeRight, yFill))
                    left2right = 0
                else:
                    res.append((xEdgeRight, yFill, xEdgeLeft, yFill))
                    left2right = 1
                yFill += fillStep
            r = self.innerEdge1 / 2 + penHalf
            while yFill < y + self.innerEdge1 / 2: #中间部分要分成左右两半
                deltaX = math.sqrt(math.pow(r, 2) - math.pow(abs(y - yFill)))
                if left2right:
                    res.append((xEdgeLeft, yFill, x - deltaX, yFill))
                    res.append((x + deltaX, yFill, xEdgeRight, yFill))
                    left2right = 0
                else:
                    res.append((xEdgeRight, yFill, x + deltaX, yFill))
                    res.append((x - deltaX, yFill, xEdgeLeft, yFill))
                    left2right = 1
                yFill += fillStep
            while yFill < yEdgeBottom: #下半部
                if left2right:
                    res.append((xEdgeLeft, yFill, xEdgeRight, yFill))
                    left2right = 0
                else:
                    res.append((xEdgeRight, yFill, xEdgeLeft, yFill))
                    left2right = 1
                yFill += fillStep
        else: #外方内方
            while yFill < y - self.innerEdge2 / 2 - penHalf: #上半部
                if left2right:
                    res.append((xEdgeLeft, yFill, xEdgeRight, yFill))
                    left2right = 0
                else:
                    res.append((xEdgeRight, yFill, xEdgeLeft, yFill))
                    left2right = 1
                yFill += fillStep
            while yFill < y + self.innerEdge2 / 2: #中间部分要分成左右两半
                if left2right:
                    res.append((xEdgeLeft, yFill, x - self.innerEdge1 / 2 - penHalf, yFill))
                    res.append((x + self.innerEdge1 / 2 + penHalf, yFill, xEdgeRight, yFill))
                    left2right = 0
                else:
                    res.append((xEdgeRight, yFill, x + self.innerEdge1 / 2 + penHalf, yFill))
                    res.append((x - self.innerEdge1 / 2 - penHalf, yFill, xEdgeLeft, yFill))
                    left2right = 1
                yFill += fillStep
            while yFill < yEdgeBottom: #下半部
                if left2right:
                    res.append((xEdgeLeft, yFill, xEdgeRight, yFill))
                    left2right = 0
                else:
                    res.append((xEdgeRight, yFill, xEdgeLeft, yFill))
                    left2right = 1
                yFill += fillStep
                
        return res
    
    #在特定点上画一个矩形椭圆（可能为实心，或空心）
    #根据x,y,penWidth生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #x,y:要画矩形椭圆的坐标（微米）
    #penWidth：笔尖宽度（微米）
    #不支持内部孔洞
    def RenderObround(self, x, y, penWidth):
        if self.outerEdge1 == self.outerEdge2:
            return self.RenderCircle(x, y, penWidth)
            
        penHalf = penWidth / 2
        fillStep = penWidth * 2 / 3
        minEdge = min(self.outerEdge1, self.outerEdge2)
        xLeft = x - self.outerEdge1 / 2
        xRight = x + self.outerEdge1 / 2
        yTop = y - self.outerEdge2 / 2
        yBottom = y + self.outerEdge2 / 2
        
        #新建一个实例用于等效绘图
        inst = Aperture()
        inst.type_ = self.Circle
        
        #横的长条，等效为Aperture为圆时的一条短横线
        if self.outerEdge1 > self.outerEdge2:
            inst.outerEdge1 = self.outerEdge2
            return inst.RenderLine(xLeft, y, xRight, y, self.outerEdge2, penWidth)
        else: #竖的长条，等效为Aperture为圆时的一条短竖线
            inst.outerEdge1 = self.outerEdge1
            return inst.RenderLine(x, yTop, x, yBottom, self.outerEdge1, penWidth)
    
    #在特定点上画一个多边形（可能为实心，或空心）
    #根据x,y,penWidth生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #x,y:要画多边形的坐标（微米）
    #penWidth：笔尖宽度（微米）
    def RenderPolygon(self, x, y, penWidth):
        penHalf = penWidth / 2
        radiusStep = penWidth * 2 / 3
        sideNum = self.outerEdge2
        radius = self.outerEdge1 / 2 - penHalf
        #根据边数设定第一个顶点位置
        if sideNum in (3, 5, 7, 9, 11) or sideNum > 12:
            firstX = tmpPrevX = x #圆最上方的点
            firstY = tmpPrevY = y - radius
            firstAlpha = math.pi / 2 #和水平线的夹角
        elif sideNum == 4: #四边形
            deltaXY = radius * math.sin(math.pi / 4)
            firstX = tmpPrevX = x - deltaXY
            firstY = tmpPrevY = y - deltaXY
            firstAlpha = math.pi / 4
        else: #其他多边形的第一个顶点设定在水平线最左端
            firstX = tmpPrevX = x - radius
            firstY = tmpPrevY = y
            firstAlpha = 0.0
        
        res = []
        #将圆分成n等分，然后从第一个顶点开始连线则形成一个多边形
        alphaStep = math.pi * 2 / sideNum
        pi2 = math.pi * 2
        print(self.innerEdge1 + penHalf)
        while radius > self.innerEdge1 + penHalf: #近似形成内圆即可
            alpha = firstAlpha + alphaStep
            while alpha - firstAlpha <= pi2:
                deltaX = radius * math.cos(alpha)
                deltaY = radius * math.sin(alpha)
                currX = x - deltaX
                currY = y - deltaY
                res.append((tmpPrevX, tmpPrevY, currX, currY))
                tmpPrevX = currX
                tmpPrevY = currY
                alpha += alphaStep
            
            res.append((tmpPrevX, tmpPrevY, firstX, firstY)) #封口
            radius -= radiusStep
        return res
        
        
#发出声音提醒
def SoundNotify(single=True):
    if winsound:
        if single:
            winsound.Beep(800, 500)
        else:
            winsound.Beep(659, 1000)
            winsound.Beep(500, 1000)
    
if __name__ == "__main__":
    top = Tk()
    Application(top).mainloop()

