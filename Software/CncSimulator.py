#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
废喷墨打印机改装的大行程数控雕刻机的PC控制端程序的模拟器
因为我的PC控制端程序并不支持所有的RS274X标准，所以此模拟器是有必要的，
可以在实际输出到控制板之前先查看实际结果，避免不必要的时间和物料浪费。
当然，因为python直接绘图，效率是比较低的，速度是比较慢的，如果图像稍大，使用要有点耐心。

Author：
    cdhigh <https://github.com/cdhigh>
License:
    The MIT License (MIT)
第一版完成日期：
    2015-05-14
"""

__Version__ = 'v0.1'

#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys
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
    #import tkFileDialog
    #import tkSimpleDialog
else:  #Python 3.x
    PythonVersion = 3
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    #import tkinter.filedialog as tkFileDialog
    #import tkinter.simpledialog as tkSimpleDialog    #askstring()


if getattr(sys, 'frozen', False): #在cxFreeze打包后
    __file__ = sys.executable
    
class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('PrinterCnc模拟器 【绘图时比较慢，请耐心等候】')
        self.master.geometry('646x554')
        self.master.resizable(0,0)
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.cmdClear = Button(self.top, text='全部清除', command=self.cmdClear_Cmd)
        self.cmdClear.place(relx=0.854, rely=0.231, relwidth=0.125, relheight=0.045)

        self.txtXYWidthVar = StringVar(value='200')
        self.txtXYWidth = Entry(self.top, textvariable=self.txtXYWidthVar)
        self.txtXYWidth.place(relx=0.854, rely=0.13, relwidth=0.125, relheight=0.045)

        self.cavSim = Canvas(self.top, bg='#FFFFFF', takefocus=1)
        self.cavSim.place(relx=0.012, rely=0.014, relwidth=0.826, relheight=0.963)
        self.cavSim.bind('<Motion>', self.cavSim_Motion)

        self.style.configure('TlblXYWidth.TLabel', anchor='e')
        self.lblXYWidth = Label(self.top, text='X/Y宽度（mm）', style='TlblXYWidth.TLabel')
        self.lblXYWidth.place(relx=0.854, rely=0.087, relwidth=0.125, relheight=0.031)

        self.style.configure('TlblXYOrdNotify.TLabel', anchor='w')
        self.lblXYOrdNotify = Label(self.top, text='X坐标(mm)', style='TlblXYOrdNotify.TLabel')
        self.lblXYOrdNotify.place(relx=0.854, rely=0.39, relwidth=0.125, relheight=0.031)

        self.style.configure('TlblXOrd.TLabel', anchor='w')
        self.lblXOrd = Label(self.top, style='TlblXOrd.TLabel')
        self.lblXOrd.place(relx=0.854, rely=0.433, relwidth=0.125, relheight=0.045)

        self.style.configure('TlblYOrdNotify.TLabel', anchor='w')
        self.lblYOrdNotify = Label(self.top, text='Y坐标(mm)', style='TlblYOrdNotify.TLabel')
        self.lblYOrdNotify.place(relx=0.854, rely=0.505, relwidth=0.125, relheight=0.031)

        self.style.configure('TlblYOrd.TLabel', anchor='w')
        self.lblYOrd = Label(self.top, style='TlblYOrd.TLabel')
        self.lblYOrd.place(relx=0.854, rely=0.549, relwidth=0.125, relheight=0.045)

class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        self.zPrevPos = '1' #'1' = down, '2' = up
        self.xPrevPos = 0
        self.yPrevPos = 0
    
    def setSimulatorWidth(self, width):
        self.txtXYWidthVar.set(width)
        
    def cmdClear_Cmd(self, event=None):
        idlst = self.cavSim.find_all()
        for o in idlst:
            self.cavSim.delete(o)
    
    #移动鼠标时显示坐标
    def cavSim_Motion(self, event=None):
        if not event:
            return
        #坐标转换
        cavW = int(self.cavSim.winfo_width())
        cavH = int(self.cavSim.winfo_height())
        print(cavW)
        print(cavH)
        try:
            simW = int(self.txtXYWidthVar.get())
        except:
            return
        MmPerPixel = simW / cavW #每像素多少mm
        x = event.x * MmPerPixel
        y = event.y * MmPerPixel
        self.lblXOrd['text'] = '%.1f' % x
        self.lblYOrd['text'] = '%.1f' % y
    
    #接收绘图命令，仿真控制板的处理
    def putDrawCmd(self, cmd, penWidth):
        cmd = cmd.decode()
        
        if cmd.startswith('@'):
            return self.specialCmd(cmd[1:])
        else:
            return self.drawCmd(cmd, penWidth)
    
    def specialCmd(self, cmd):
        if cmd == 'reposx':
            self.xPrevPos = 0
        elif cmd == 'reposy':
            self.yPrevPos = 0
        elif cmd == 'reposz':
            self.zPrevPos = '1'
        return b'*'
        
    #绘图命令：格式：x000000y000000z1
    def drawCmd(self, cmd, penWidth):
        if not cmd.startswith('x') or len(cmd) != 16:
            return b'#'
        
        x = int(cmd[1:7])
        y = int(cmd[8:14])
        z = cmd[15]
        
        #坐标转换
        cavW = int(self.cavSim.winfo_width())
        cavH = int(self.cavSim.winfo_height())
        try:
            simW = int(self.txtXYWidthVar.get()) * 1000 #转换为微米
        except:
            showinfo('出错啦', '设置的XY宽度值无效，请更正后再继续')
            return b'#'
            
        pixelPerMircon = cavW / simW #每微米多少像素
        x = int(x * pixelPerMircon)
        y = int(y * pixelPerMircon)
        if z == '2':
            self.xPrevPos = x
            self.yPrevPos = y
            self.zPrevPos = '2'
        elif self.xPrevPos == x or self.yPrevPos == y:
            lineWidth = int(penWidth * pixelPerMircon)
            if lineWidth < 1:
                lineWidth = 1
            self.cavSim.create_line(self.xPrevPos, self.yPrevPos, x, y, width=lineWidth)
            self.xPrevPos = x
            self.yPrevPos = y
            self.zPrevPos = '1'
        else:
            return b'#'
            
        return b'*'
            
if __name__ == "__main__":
    top = Tk()
    Application(top).mainloop()
