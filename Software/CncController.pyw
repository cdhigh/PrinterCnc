#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
打印机改装的数控雕刻机PC控制端程序，理论上支持Python 2.x/3.x，但只在python 3下测试，依赖pyserial库
GUI界面采用Tkinter库，使用VisualTkinter工具自动生成界面代码<https://github.com/cdhigh/Visual-Tkinter-for-Python>
此项目参考了<https://github.com/themrleon/OpenCdNC>
并托管在<https://github.com/cdhigh/PrinterCnC>
Author: cdhigh <https://github.com/cdhigh>
"""

__Version__ = 'v0.1'

import os, sys, re, time
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
else:  #Python 3.x
    PythonVersion = 3
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    import tkinter.filedialog as tkFileDialog
    #import tkinter.simpledialog as tkSimpleDialog    #askstring()
    from queue import Queue
    

from threading import Thread, Event
import serial
#import PIL

class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('PrinterCncController [https://github.com/cdhigh/PrinterCnc]')
        self.master.resizable(0,0)
        self.master.protocol('WM_DELETE_WINDOW', self.EV_WM_DELETE_WINDOW)
        # To center the window on the screen.
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        x = (ws / 2) - (715 / 2)
        y = (hs / 2) - (529 / 2)
        self.master.geometry('%dx%d+%d+%d' % (715,529,x,y))
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.style.configure('TfrmSpeed.TLabelframe', font=('宋体',9))
        self.style.configure('TfrmSpeed.TLabelframe.Label', font=('宋体',9))
        self.frmSpeed = LabelFrame(self.top, text='进给速度（值越小越快）', style='TfrmSpeed.TLabelframe')
        self.frmSpeed.place(relx=0.011, rely=0.605, relwidth=0.46, relheight=0.259)

        self.style.configure('TcmdPause.TButton', font=('宋体',9))
        self.cmdPause = Button(self.top, text='暂停(P)', underline=3, command=self.cmdPause_Cmd, style='TcmdPause.TButton')
        self.cmdPause.place(relx=0.392, rely=0.907, relwidth=0.203, relheight=0.078)
        self.top.bind_all('<Alt-P>', lambda e: self.cmdPause.focus_set() or self.cmdPause.invoke())
        self.top.bind_all('<Alt-p>', lambda e: self.cmdPause.focus_set() or self.cmdPause.invoke())

        self.style.configure('TcmdStop.TButton', background='#F0F0F0', font=('宋体',9))
        self.cmdStop = Button(self.top, text='停止(T)', underline=3, command=self.cmdStop_Cmd, style='TcmdStop.TButton')
        self.cmdStop.place(relx=0.716, rely=0.907, relwidth=0.203, relheight=0.078)
        self.top.bind_all('<Alt-T>', lambda e: self.cmdStop.focus_set() or self.cmdStop.invoke())
        self.top.bind_all('<Alt-t>', lambda e: self.cmdStop.focus_set() or self.cmdStop.invoke())

        self.style.configure('TfrmManualCmd.TLabelframe', font=('宋体',9))
        self.style.configure('TfrmManualCmd.TLabelframe.Label', font=('宋体',9))
        self.frmManualCmd = LabelFrame(self.top, text='手动执行命令', style='TfrmManualCmd.TLabelframe')
        self.frmManualCmd.place(relx=0.481, rely=0.741, relwidth=0.505, relheight=0.123)

        self.style.configure('TfrmLog.TLabelframe', font=('宋体',9))
        self.style.configure('TfrmLog.TLabelframe.Label', font=('宋体',9))
        self.frmLog = LabelFrame(self.top, text='收发数据', style='TfrmLog.TLabelframe')
        self.frmLog.place(relx=0.481, rely=0.076, relwidth=0.505, relheight=0.652)

        self.style.configure('TfrmSerial.TLabelframe', font=('宋体',9))
        self.style.configure('TfrmSerial.TLabelframe.Label', font=('宋体',9))
        self.frmSerial = LabelFrame(self.top, text='端口设置', style='TfrmSerial.TLabelframe')
        self.frmSerial.place(relx=0.011, rely=0.076, relwidth=0.46, relheight=0.198)

        self.style.configure('TcmdStart.TButton', font=('宋体',9))
        self.cmdStart = Button(self.top, text='启动(S)', state='disabled', underline=3, command=self.cmdStart_Cmd, style='TcmdStart.TButton')
        self.cmdStart.place(relx=0.067, rely=0.907, relwidth=0.203, relheight=0.078)
        self.top.bind_all('<Alt-S>', lambda e: self.cmdStart.focus_set() or self.cmdStart.invoke())
        self.top.bind_all('<Alt-s>', lambda e: self.cmdStart.focus_set() or self.cmdStart.invoke())

        self.style.configure('TfrmSetupManual.TLabelframe', font=('宋体',9))
        self.style.configure('TfrmSetupManual.TLabelframe.Label', font=('宋体',9))
        self.frmSetupManual = LabelFrame(self.top, text='手动调整', style='TfrmSetupManual.TLabelframe')
        self.frmSetupManual.place(relx=0.011, rely=0.287, relwidth=0.46, relheight=0.304)

        self.style.configure('TcmdChoosePreview.TButton', font=('宋体',9))
        self.cmdChoosePreview = Button(self.top, text='...', command=self.cmdChoosePreview_Cmd, style='TcmdChoosePreview.TButton')
        self.cmdChoosePreview.place(relx=0.929, rely=0.015, relwidth=0.057, relheight=0.047)

        self.txtPreviewVar = StringVar(value='')
        self.txtPreview = Entry(self.top, textvariable=self.txtPreviewVar, font=('宋体',9))
        self.txtPreview.place(relx=0.112, rely=0.015, relwidth=0.807, relheight=0.047)

        self.style.configure('TlblVersion.TLabel', anchor='e', foreground='#B0B0B0', font=('Courier New',8))
        self.lblVersion = Label(self.top, text='v0.1', style='TlblVersion.TLabel')
        self.lblVersion.place(relx=0.917, rely=0.953, relwidth=0.069, relheight=0.032)

        self.style.configure('TlblPreview.TLabel', anchor='e', font=('宋体',9))
        self.lblPreview = Label(self.top, text='输入文件', style='TlblPreview.TLabel')
        self.lblPreview.place(relx=0.011, rely=0.015, relwidth=0.091, relheight=0.047)

        self.style.configure('TcmdApplyAxisSpeed.TButton', font=('宋体',9))
        self.cmdApplyAxisSpeed = Button(self.frmSpeed, text='应用', command=self.cmdApplyAxisSpeed_Cmd, style='TcmdApplyAxisSpeed.TButton')
        self.cmdApplyAxisSpeed.place(relx=0.681, rely=0.292, relwidth=0.222, relheight=0.533)

        self.txtZSpeedVar = StringVar(value='50')
        self.txtZSpeed = Entry(self.frmSpeed, textvariable=self.txtZSpeedVar, font=('宋体',9))
        self.txtZSpeed.place(relx=0.34, rely=0.701, relwidth=0.246, relheight=0.182)

        self.txtYSpeedVar = StringVar(value='30')
        self.txtYSpeed = Entry(self.frmSpeed, textvariable=self.txtYSpeedVar, font=('宋体',9))
        self.txtYSpeed.place(relx=0.34, rely=0.467, relwidth=0.246, relheight=0.182)

        self.txtXSpeedVar = StringVar(value='30')
        self.txtXSpeed = Entry(self.frmSpeed, textvariable=self.txtXSpeedVar, font=('宋体',9))
        self.txtXSpeed.place(relx=0.34, rely=0.234, relwidth=0.246, relheight=0.182)

        self.style.configure('TlblZSpeed.TLabel', anchor='e', font=('宋体',9))
        self.lblZSpeed = Label(self.frmSpeed, text='Z轴速度', style='TlblZSpeed.TLabel')
        self.lblZSpeed.place(relx=0.097, rely=0.701, relwidth=0.198, relheight=0.124)

        self.style.configure('TlblYSpeed.TLabel', anchor='e', font=('宋体',9))
        self.lblYSpeed = Label(self.frmSpeed, text='Y轴速度', style='TlblYSpeed.TLabel')
        self.lblYSpeed.place(relx=0.097, rely=0.467, relwidth=0.198, relheight=0.124)

        self.style.configure('TlblXSpeed.TLabel', anchor='e', font=('宋体',9))
        self.lblXSpeed = Label(self.frmSpeed, text='X轴速度', style='TlblXSpeed.TLabel')
        self.lblXSpeed.place(relx=0.097, rely=0.234, relwidth=0.198, relheight=0.124)

        self.style.configure('TcmdSendCommand.TButton', font=('宋体',9))
        self.cmdSendCommand = Button(self.frmManualCmd, text='执行', command=self.cmdSendCommand_Cmd, style='TcmdSendCommand.TButton')
        self.cmdSendCommand.place(relx=0.842, rely=0.369, relwidth=0.136, relheight=0.508)

        self.txtManualCommandVar = StringVar(value='')
        self.txtManualCommand = Entry(self.frmManualCmd, textvariable=self.txtManualCommandVar, font=('Courier New',12))
        self.txtManualCommand.place(relx=0.044, rely=0.369, relwidth=0.778, relheight=0.508)
        self.txtManualCommand.bind('<Return>', self.txtManualCommand_Return)

        self.style.configure('TcmdSaveLog.TButton', font=('宋体',9))
        self.cmdSaveLog = Button(self.frmLog, text='保存', command=self.cmdSaveLog_Cmd, style='TcmdSaveLog.TButton')
        self.cmdSaveLog.place(relx=0.51, rely=0.904, relwidth=0.202, relheight=0.072)

        self.scrVLog = Scrollbar(self.frmLog, orient='vertical')
        self.scrVLog.place(relx=0.909, rely=0.07, relwidth=0.047, relheight=0.814)

        self.style.configure('TcmdClearLog.TButton', font=('宋体',9))
        self.cmdClearLog = Button(self.frmLog, text='清空', command=self.cmdClearLog_Cmd, style='TcmdClearLog.TButton')
        self.cmdClearLog.place(relx=0.753, rely=0.904, relwidth=0.202, relheight=0.072)

        self.lstLogVar = StringVar(value='')
        self.lstLogFont = Font(font=('宋体',12))
        self.lstLog = Listbox(self.frmLog, listvariable=self.lstLogVar, yscrollcommand=self.scrVLog.set, font=self.lstLogFont)
        self.lstLog.place(relx=0.044, rely=0.07, relwidth=0.867, relheight=0.8)
        self.scrVLog['command'] = self.lstLog.yview

        self.style.configure('TlblQueueCmdNum.TLabel', anchor='w', font=('宋体',9))
        self.lblQueueCmdNum = Label(self.frmLog, text='剩余命令：', style='TlblQueueCmdNum.TLabel')
        self.lblQueueCmdNum.place(relx=0.044, rely=0.904, relwidth=0.446, relheight=0.072)

        self.style.configure('TcmdCloseSerial.TButton', font=('宋体',9))
        self.cmdCloseSerial = Button(self.frmSerial, text='关闭', state='disabled', command=self.cmdCloseSerial_Cmd, style='TcmdCloseSerial.TButton')
        self.cmdCloseSerial.place(relx=0.681, rely=0.533, relwidth=0.222, relheight=0.238)

        self.cmbTimeOutList = ['5s','7s','9s','11s','13s','15s','17s','19s','21s',]
        self.cmbTimeOutVar = StringVar(value='5s')
        self.cmbTimeOut = Combobox(self.frmSerial, text='5s', textvariable=self.cmbTimeOutVar, values=self.cmbTimeOutList, font=('宋体',9))
        self.cmbTimeOut.place(relx=0.267, rely=0.533, relwidth=0.343, relheight=0.19)

        self.style.configure('TcmdOpenSerial.TButton', font=('宋体',9))
        self.cmdOpenSerial = Button(self.frmSerial, text='打开', command=self.cmdOpenSerial_Cmd, style='TcmdOpenSerial.TButton')
        self.cmdOpenSerial.place(relx=0.681, rely=0.229, relwidth=0.222, relheight=0.238)

        self.cmbSerialList = ['COM1','COM2','COM3','COM4','COM5','COM6','COM6','COM7','COM8','COM9',]
        self.cmbSerialVar = StringVar(value='COM1')
        self.cmbSerial = Combobox(self.frmSerial, text='COM1', textvariable=self.cmbSerialVar, values=self.cmbSerialList, font=('宋体',9))
        self.cmbSerial.place(relx=0.267, rely=0.229, relwidth=0.343, relheight=0.19)

        self.style.configure('TLabel3.TLabel', anchor='e', font=('宋体',9))
        self.Label3 = Label(self.frmSerial, text='超时时间', style='TLabel3.TLabel')
        self.Label3.place(relx=0.049, rely=0.533, relwidth=0.173, relheight=0.162)

        self.style.configure('TLabel2.TLabel', anchor='e', font=('宋体',9))
        self.Label2 = Label(self.frmSerial, text='端口号', style='TLabel2.TLabel')
        self.Label2.place(relx=0.049, rely=0.229, relwidth=0.173, relheight=0.162)

        self.style.configure('TcmdResetXYZ.TButton', font=('宋体',9))
        self.cmdResetXYZ = Button(self.frmSetupManual, text='全部清零', command=self.cmdResetXYZ_Cmd, style='TcmdResetXYZ.TButton')
        self.cmdResetXYZ.place(relx=0.681, rely=0.745, relwidth=0.222, relheight=0.155)

        self.style.configure('TcmdResetZ.TButton', font=('宋体',9))
        self.cmdResetZ = Button(self.frmSetupManual, text='Z清零', command=self.cmdResetZ_Cmd, style='TcmdResetZ.TButton')
        self.cmdResetZ.place(relx=0.681, rely=0.547, relwidth=0.222, relheight=0.155)

        self.style.configure('TcmdResetY.TButton', font=('宋体',9))
        self.cmdResetY = Button(self.frmSetupManual, text='Y清零', command=self.cmdResetY_Cmd, style='TcmdResetY.TButton')
        self.cmdResetY.place(relx=0.681, rely=0.348, relwidth=0.222, relheight=0.155)

        self.style.configure('TcmdResetX.TButton', font=('宋体',9))
        self.cmdResetX = Button(self.frmSetupManual, text='X清零', command=self.cmdResetX_Cmd, style='TcmdResetX.TButton')
        self.cmdResetX.place(relx=0.681, rely=0.149, relwidth=0.222, relheight=0.155)

        self.style.configure('TcmdZDown.TButton', font=('宋体',9))
        self.cmdZDown = Button(self.frmSetupManual, text='↓', command=self.cmdZDown_Cmd, style='TcmdZDown.TButton')
        self.cmdZDown.place(relx=0.486, rely=0.547, relwidth=0.1, relheight=0.205)

        self.style.configure('TcmdZUp.TButton', font=('宋体',9))
        self.cmdZUp = Button(self.frmSetupManual, text='↑', command=self.cmdZUp_Cmd, style='TcmdZUp.TButton')
        self.cmdZUp.place(relx=0.486, rely=0.199, relwidth=0.1, relheight=0.205)

        self.style.configure('TcmdXRight.TButton', font=('宋体',9))
        self.cmdXRight = Button(self.frmSetupManual, text='→', command=self.cmdXRight_Cmd, style='TcmdXRight.TButton')
        self.cmdXRight.place(relx=0.243, rely=0.398, relwidth=0.1, relheight=0.205)

        self.style.configure('TcmdXLeft.TButton', font=('宋体',9))
        self.cmdXLeft = Button(self.frmSetupManual, text='←', command=self.cmdXLeft_Cmd, style='TcmdXLeft.TButton')
        self.cmdXLeft.place(relx=0.049, rely=0.398, relwidth=0.1, relheight=0.205)

        self.style.configure('TcmdYDown.TButton', font=('宋体',9))
        self.cmdYDown = Button(self.frmSetupManual, text='↓', command=self.cmdYDown_Cmd, style='TcmdYDown.TButton')
        self.cmdYDown.place(relx=0.146, rely=0.596, relwidth=0.1, relheight=0.205)

        self.style.configure('TcmdYUp.TButton', font=('宋体',9))
        self.cmdYUp = Button(self.frmSetupManual, text='↑', command=self.cmdYUp_Cmd, style='TcmdYUp.TButton')
        self.cmdYUp.place(relx=0.146, rely=0.199, relwidth=0.1, relheight=0.205)

        self.style.configure('TLabel1.TLabel', anchor='w', font=('宋体',9))
        self.Label1 = Label(self.frmSetupManual, text='XY     Z', style='TLabel1.TLabel')
        self.Label1.place(relx=0.316, rely=0.795, relwidth=0.198, relheight=0.155)

        self.style.configure('TLine2.TSeparator', background='#FFFFFF')
        self.Line2 = Separator(self.frmSetupManual, orient='vertical', style='TLine2.TSeparator')
        self.Line2.place(relx=0.389, rely=0.149, relwidth=0.003, relheight=0.547)

        self.style.configure('TLine1.TSeparator', background='#404040')
        self.Line1 = Separator(self.frmSetupManual, orient='vertical', style='TLine1.TSeparator')
        self.Line1.place(relx=0.389, rely=0.149, relwidth=0.0061, relheight=0.547)


class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        self.lblVersion['text'] = __Version__
        self.cmbSerial.current(0)
        self.cmbTimeOut.current(3)
        self.ser = None
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
    
    #安全退出，在窗口关闭前先保证线程退出
    def EV_WM_DELETE_WINDOW(self, event=None):
        self.evExit.set()
        self.evStop.set()
        self.cmdQueue.put_nowait('') #让队列醒来，以便线程优雅的自己退出
        self.thread.join()
        self.cmdCloseSerial_Cmd()
        self.master.destroy()
    
    def txtManualCommand_Return(self, event):
        self.cmdSendCommand_Cmd()
    
    def cmdChoosePreview_Cmd(self, event=None):
        sf = tkFileDialog.askopenfilename(initialfile=self.txtPreviewVar.get(), filetypes=[("Gerber File","*.txt"),("Gerber File","*.gbr"),("Gerber File","*.gerber"),('Bitmap File',"*.bmp"),("All Files", "*")])
        if sf:
            self.txtPreviewVar.set(sf)
        
    def cmdStart_Cmd(self, event=None):
        #在开始前先设定当前位置为原点
        filename = self.txtPreviewVar.get()
        if not filename:
            showinfo('注意啦', '你忘了选择输入文件了！')
            return
            
        if filename.upper().endswith(('.TXT','.GBR','.GERBER')):
            self.ProcessGerberFile(filename)
        else:
            showinfo('注意啦', '暂不支持此类文件！')
    
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
        self.SendCommand(b'@z+0020')
        
    def cmdZUp_Cmd(self, event=None):
        self.SendCommand(b'@z-0020')

    def cmdXRight_Cmd(self, event=None):
        self.SendCommand(b'@x+1886')

    def cmdXLeft_Cmd(self, event=None):
        self.SendCommand(b'@x-1886')

    def cmdYDown_Cmd(self, event=None):
        self.SendCommand(b'@y+1886')

    def cmdYUp_Cmd(self, event=None):
        self.SendCommand(b'@y-1886')

    def cmdSelfTest_Cmd(self, event=None):
        import time
        self.SendCommand(b'@x+0050')
        time.sleep(0.5)
        self.SendCommand(b'@x-0050')
        time.sleep(0.5)
        self.SendCommand(b'@y+0050')
        time.sleep(0.5)
        self.SendCommand(b'@y-0050')
        time.sleep(0.5)
        self.SendCommand(b'@z+0020')
        time.sleep(0.5)
        self.SendCommand(b'@z-0020')
        
    def cmdOpenSerial_Cmd(self, event=None):
        try:
            timeout = self.cmbTimeOutVar.get()
            timeout = int(timeout.replace('s', '').strip())
            self.ser = serial.Serial(self.cmbSerialVar.get(), 9600, timeout=timeout)
        except Exception as e:
            showerror('出错啦',str(e))
            self.ser = None
            self.cmdCloseSerial.config(state='disabled')
            self.cmdStart.config(state='disabled')
        else:
            self.cmdCloseSerial.config(state='normal')
            self.cmdOpenSerial.config(state='disabled')
            self.cmdStart.config(state='normal')
    
    def cmdCloseSerial_Cmd(self, event=None):
        if self.ser:
            self.ser.close()
            self.ser = None
            self.cmdCloseSerial.config(state='disabled')
            self.cmdOpenSerial.config(state='normal')
            self.cmdStart.config(state='disabled')

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
        self.cmdResetX_Cmd()
        self.cmdResetY_Cmd()
        self.cmdResetZ_Cmd()
    
    #设置控制板的XYZ轴运动速度，值越小运动越快，注意速度太快则扭矩下降，并有可能丢步
    def cmdApplyAxisSpeed_Cmd(self, event=None):
        xSpeed = self.txtXSpeedVar.get()
        ySpeed = self.txtYSpeedVar.get()
        zSpeed = self.txtZSpeedVar.get()
        try:
            xSpeed = int(xSpeed)
            ySpeed = int(ySpeed)
            zSpeed = int(zSpeed)
        except Exception as e:
            showinfo('出错啦', str(e))
            return
        
        self.SendCommand(('@X%04d' % xSpeed).encode())
        self.SendCommand(('@Y%04d' % ySpeed).encode())
        self.SendCommand(('@Z%04d' % zSpeed).encode())
        
    def SendCommand(self, cmd):
        if not self.ser:
            showinfo('注意啦', '请先打开串口然后再执行命令')
            return
        
        self.evStop.clear()
        self.evPause.clear()
        self.cmdQueue.put(cmd, block=True)
        
    def AddCommandLog(self, cmd, isResponse=False):
        if isResponse:
            self.lstLog.insert(END, b'                           ' + cmd)
        else:
            self.lstLog.insert(END, cmd)
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
            
    #分析Gerber文件，将其中的运动命令X...Y...D..行转换成CNC合法的命令发送
    #注意：Gerber文件中的坐标不能有负数
    def ProcessGerberFile(self, filename):
        try:
            with open(filename, 'r') as f1:
                lines = [word.strip() for word in f1.read().split('\n') if word.strip()]
        except Exception as e:
            showerror('出错啦',str(e))
            return
        
        self.evStop.clear()
        self.evPause.clear()
        self.cmdPause['text'] = '暂停(P)'
        while (True): #清空队列
            try:
                tmp = self.cmdQueue.get_nowait()
            except Exception as e:
                break
            
        #先读取gerber文件头的一些内嵌信息
        gerberInfo = {'xInteger':2,'xDecimal':5,'yInteger':2,'yDecimal':5,'zeroSuppress':'L','unit':'inch'}
        for line in lines[:20]:
            mat = re.match(r'^%FS([LTD]).*?X(\d\d)Y(\d\d).*', line)
            if mat:
                gerberInfo['zeroSuppress'] = mat.group(1)
                xFormat = mat.group(2)
                yFormat = mat.group(3)
                gerberInfo['xInteger'] = int(xFormat[0])
                gerberInfo['xDecimal'] = int(xFormat[-1])
                gerberInfo['yInteger'] = int(yFormat[0])
                gerberInfo['yDecimal'] = int(yFormat[-1])
            
            if line.startswith('%MOIN*%'):
                gerberInfo['unit'] = 'inch'
            elif line.startswith('%MOMM*%'):
                gerberInfo['unit'] = 'mm'
        
        #内嵌函数，将字符串格式的xy转换成浮点型，返回转换后的元组
        def XY2Float(x, y, gerberInfo):
            #先去零
            #if (gerberInfo['zeroSuppress'] == 'L'): #忽略前导零
            #    x = x.lstrip('0 ')
            #    y = y.lstrip('0 ')
            if (gerberInfo['zeroSuppress'] == 'T'): #忽略后导零
                x = x.rstrip('0 ')
                y = y.rstrip('0 ')
                
            #加小数点
            if (gerberInfo['xDecimal'] > 0):
                x = x[:-gerberInfo['xDecimal']] + '.' + x[-gerberInfo['xDecimal']:]
                #忽略前导零
                x = x.lstrip('0 ')
                if (x.startswith('.')):
                    x = '0' + x
            if (gerberInfo['yDecimal'] > 0):
                y = y[:-gerberInfo['yDecimal']] + '.' + y[-gerberInfo['yDecimal']:]
                #忽略前导零
                y = y.lstrip('0 ')
                if (y.startswith('.')):
                    y = '0' + y
            return (float(x),float(y))
            
        #开始逐行处理文件
        grblStr = r'^X([0-9]+?)Y([0-9]+?)D0([12])\*'
        grblExp = re.compile(grblStr)
        x = y = prevX = prevY = 0.0
        for line in lines:
            mat = grblExp.match(line.strip())
            if mat:
                x, y = XY2Float(mat.group(1), mat.group(2), gerberInfo)
                #转换成微米
                if gerberInfo['unit'] == 'inch':
                    x = x * 25.4 * 1000
                    y = y * 25.4 * 1000
                else: #mm
                    x = x * 1000
                    y = y * 1000
                z = mat.group(3)
                #一条斜线，雕刻机不支持直接画斜线，要用一系列的横线竖线逼近
                if (z == '1') and (x != prevX) and (y != prevY):
                    for point in self.SplitDiagonal(prevX, prevY, x, y):
                        out = 'x%6.0fy%6.0fz%s' % (point[0], point[1], z)
                        out = out.replace(' ', '0')
                        self.SendCommand(out.encode())
                else:
                    out = 'x%6.0fy%6.0fz%s' % (x, y, z)
                    out = out.replace(' ', '0')
                    self.SendCommand(out.encode())
                
                prevX = x
                prevY = y
        
        self.SendCommand(b'x000000y000000z2') #归位
    
    #将斜线分解转换成很多段的水平线和垂直线序列，因为雕刻机仅支持画水平线或垂直线
    #函数直接返回一个元祖列表[(x1,y1),(x2,y2),...]
    #参数坐标单位为微米，(x1,y1)为起始点，(x2,y2)为结束点
    def SplitDiagonal(self, x1, y1, x2, y2):
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
            return self.SplitDiagonal(x1, y1, xm, ym) + self.SplitDiagonal(xm, ym, x2, y2)
        
    #单独的一个线程，在队列中取命令，然后发送给CNC控制板，并且等待控制板的答复
    def threadSendCommand(self, evStop, evExit, evPause, cmdQueue):
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
            
            self.lblQueueCmdNum['text'] = '剩余命令：%d' % self.cmdQueue.qsize()
            
            if not cmd:
                time.sleep(0.1) #队列空了，睡0.1s先
                continue
            elif evStop.is_set(): #按停止键后需要迅速将队列取空
                continue
            
            try:
                self.ser.write(cmd)
            except Exception as e:
                self.AddCommandLog(b'Err Write: %s' % cmd)
                
            self.AddCommandLog(cmd)
            
            cnt = 0
            while (cnt < 3):
                try:
                    response = self.ser.read()
                except Exception as e:
                    pass
                cnt += 1
                if ((response == b'*') or (response == b'#')):
                    break
                
                if evExit.is_set() or evPause.is_set() or evStop.is_set():
                    break
                
                
            if response:
                self.AddCommandLog(response, True)
            else: #超时
                self.AddCommandLog(b'Timeout', True)
                
                
        

if __name__ == "__main__":
    top = Tk()
    Application(top).mainloop()

