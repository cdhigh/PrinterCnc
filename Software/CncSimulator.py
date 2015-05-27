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
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.cmdClear = Button(self.top, text='全部清除', command=self.cmdClear_Cmd)
        self.cmdClear.place(relx=0.854, rely=0.679, relwidth=0.125, relheight=0.045)

        self.txtXWidthVar = StringVar(value='200')
        self.txtXWidth = Entry(self.top, textvariable=self.txtXWidthVar)
        self.txtXWidth.place(relx=0.854, rely=0.13, relwidth=0.125, relheight=0.045)
        self.txtXWidthVar.trace('w', self.txtXWidth_Change)

        self.cavSim = Canvas(self.top, bg='#FFFFFF', takefocus=1)
        self.cavSim.place(relx=0.012, rely=0.014, relwidth=0.826, relheight=0.963)
        self.cavSim.bind('<Motion>', self.cavSim_Motion)

        self.style.configure('TlblYOrd.TLabel', anchor='w')
        self.lblYOrd = Label(self.top, style='TlblYOrd.TLabel')
        self.lblYOrd.place(relx=0.854, rely=0.549, relwidth=0.125, relheight=0.045)

        self.style.configure('TlblYOrdNotify.TLabel', anchor='w')
        self.lblYOrdNotify = Label(self.top, text='Y坐标(mm)', style='TlblYOrdNotify.TLabel')
        self.lblYOrdNotify.place(relx=0.854, rely=0.505, relwidth=0.125, relheight=0.031)

        self.style.configure('TlblXOrd.TLabel', anchor='w')
        self.lblXOrd = Label(self.top, style='TlblXOrd.TLabel')
        self.lblXOrd.place(relx=0.854, rely=0.433, relwidth=0.125, relheight=0.045)

        self.style.configure('TlblXYOrdNotify.TLabel', anchor='w')
        self.lblXYOrdNotify = Label(self.top, text='X坐标(mm)', style='TlblXYOrdNotify.TLabel')
        self.lblXYOrdNotify.place(relx=0.854, rely=0.39, relwidth=0.125, relheight=0.031)

        self.style.configure('TlblXWidth.TLabel', anchor='e')
        self.lblXWidth = Label(self.top, text='X宽度（mm）', style='TlblXWidth.TLabel')
        self.lblXWidth.place(relx=0.854, rely=0.087, relwidth=0.125, relheight=0.031)

        self.txtYHeightVar = StringVar(value='200')
        self.txtYHeight = Entry(self.top, state='readonly', textvariable=self.txtYHeightVar)
        self.txtYHeight.place(relx=0.854, rely=0.245, relwidth=0.125, relheight=0.045)

        self.style.configure('TlblYHeight.TLabel', anchor='e')
        self.lblYHeight = Label(self.top, text='Y高度（mm）', style='TlblYHeight.TLabel')
        self.lblYHeight.place(relx=0.854, rely=0.202, relwidth=0.125, relheight=0.031)

class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        self.zPrevPos = '1' #'1' = down, '2' = up
        self.xPrevPos = 0
        self.yPrevPos = 0
    
    def setSimulatorWidth(self, width):
        self.txtXWidthVar.set(width)
    
    #X宽度更新后刷新Y高度
    def txtXWidth_Change(self, *args):
        try:
            xWidth = int(self.txtXWidthVar.get())
        except:
            xWidth = 0
        
        if xWidth <= 0:
            #showinfo('出错啦', 'X宽度设置值非法，请设置为一个正整数值')
            return
        
        cavW = int(self.cavSim.winfo_width())
        cavH = int(self.cavSim.winfo_height())
        xHeight = cavH / cavW * xWidth
        self.txtYHeightVar.set('%d' % xHeight)
        
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
        try:
            simW = int(self.txtXWidthVar.get())
        except:
            return
        simH = cavH / cavW * simW
        if self.txtYHeightVar.get() != '%d' % simH:
            self.txtYHeightVar.set('%d' % simH)
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
            simW = int(self.txtXWidthVar.get()) * 1000 #转换为微米
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
