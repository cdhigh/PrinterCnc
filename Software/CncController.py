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
    GUI界面采用Python内置的Tkinter标准库，使用作者自己的TkinterDesigner工具自动生成界面代码。
    <https://github.com/cdhigh/tkinter-designer>
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

__Version__ = 'v1.2'

import os, sys, re, time, datetime, math
if sys.version_info[0] == 2:
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
    from tkinter import *
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
    
from operator import itemgetter
from threading import Thread, Event
import serial
from serial.tools import list_ports

CFG_FILE = 'CncController.ini'
ANGLE_PER_SIDE = 0.017453293 * 10 #用多边形逼近圆形时的步进角度，值越小越圆，但数据量越大
END_CMD = b'@END'

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
           ("All Files", "*.*")]
           
#用于设定在打开钻孔文件中的文件后缀
def ExcellonFileMask():
    return [('Excellon Drill Files', '*.drl'),('All Files', '*.*')]
    
class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('PrinterCnc Controller - <https://github.com/cdhigh>')
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
            AAAAAAAAAAAAAAAAAAAAACH5BAEAANgALAAAAAAYARcBAAj/ALEJHEiwoMGDCBMqXMiw
            ocOHECNKnEixosWLGDNq3Mixo8ePIEOKHEmypMmTKFOqXMmypcuXMGPKnEkTJJ06mT7p
            3Mmzp8+fQIMKHUq0qNGjSJMqXcq0qdNPmerQkUjn07CrWLNq3cq1q9evYMOKHUu2rNmz
            aNOqXcv101SHdNjKnUu3rt27ePOqfbswrt6/gAMLHkw4Ld+EVgsrXsy4seOyn/o+nky5
            suW/hw3Wucy5s+fPXesozAS6tOnTjDMpTIy6tevXciMjhk27tu2vshGyvs27t+vcB3f7
            Hk6cM3CDwosrX774eMHkzKNLz+ucIPTp2LOrrT7wuvbv4MFy/xfoPTxWOujTq1/Pvr37
            9/Djy99sXut4bOXrA9jPv7///wAGKOCABBb4RH32rYagVwU26OCDEAZ44IJX3ZefeRFm
            qOGG/U1IoYUUcsXhiCQaGOIwIJ6YVYkstsifhwumqOJVLtZIIowIyjijjTxqiGN9OqrY
            45AP/mhekCcSqSSBRoaHZIhLRglgk+A9SaGUWL54opULZpklld9xiaCXWIKpnZj6kRml
            mdmhiaGaS7KJnZvhwRnnlgrOSKOdRMo5HZ3g8dknnrPpOYygQ/opHaDfIdqjotExqp2j
            PELKnKTZUWqjpcthip2mNXKqnKfTgeqiqMWRKp2pLaJKnKrRsf/KoqvDwcqcrCXS6put
            y+F6I6G6GXqorxzq2huvyhFbLLDBCavshsbyhmxxz/rILHLOVhthtLdNS5y22177XLbg
            Ositbd4OV26R4lpH7rpMttvdu/AKeG5t6fpWr4kh5tvbvvH2m6eeAA94L23+8lawvfKS
            R+/CWgpcKMEQ/3cwbAnfVrHFDeP3cMUXv5axbRv7F/JvA+9YcsQfpizkyvud3NrItcEc
            c8cX+pbJEyX07PPPPtu8H9BEl+BXpC5HVwcJQrcIxZ9JM7d00yw+vWjUy01NNYlWIz3x
            dFpvzWHXl2KtXNhia0h2p2YXh3baEa49atvEvQ33g3KnSvdwdt//3WDer+7tW99+Ewh4
            rYL3RnjhAh6+a+K8Lc44gI4fC/ltkk/uX+XSXm5b5przx3m3ntcGeugAjI5u6bSdHrrq
            +LIOm+uaw46w7K/RPrntGOPumu6M8y6y760BX7jwKH8tnfF+Iz8z8agxf7fzqNFsmfRw
            U3+a9ZVhn7b2pnFPmfdig1+a+JORv7X5oKH/mPpUs/+Z+47B37T8ntHfmP1C49+Z/ozh
            n838ZxzonUaAMCPgZQC4GASuTIGWYaBiHFgyCFZGgoWh4MYsSBkMEkaDFePgZDw4GBBC
            TISPIaFgTLgwFDpGhYFhYcFc2BgYAkaGAKMhY2z4FxzuS4fNMaBp/zIBhScY8YhIPKLQ
            SJDEJj7haGVTXqSMIrQnFAVqUoSSzWRWPSGqa4s4+xjEuLg9L+oLjBILlqGqGMY1orFl
            WbzSG2Nkxn/NMUd1VNgdgZRHje3xSH0k2R+dFMiaDbJKhaQNG9PYLDfCjIzhSyRsFglH
            NVLskW285MogeT5JvoaSdIxjlw4ZJk+6pmioTCXTSpTKVqYSiPkzJXgyMaISQCFnwhKP
            LL9DSw3ZkjS5jM0utdNLCD0Rl8EMCw+HU8wGHTOZdVmmzhwEhTroBJrRHGZ2mimhqnjn
            mtiEjDaxw83+/DIsdXgCfcI5Fmn2ppwAsOWFoEICEqyTncoc53S4uf+CqojlE1Bgmj3x
            2U59SqeY/QSmMqHAn4ESNJ+ifKhWaKlOZGZiBf1xqES94k5pWdOiGM3oPTe6lY5WiQ4A
            0ihJS2pQFblllf5R6UqzYtJtMjRAMp1phVoao50NKKc6ral06FACAgF1pvepiUduaZlM
            FNWoI9UpipSKEoU+hg4w/WlUg0rVk1g1NTdt0FFXmtSubuSrhYFKSB00VpKW1awZQSth
            6LBWtm4VqXAliVwFg9UMtXWjb82rRfb6F7c8NUJ/lWhgBUsRwlInrBkqgWMBy9iQTDaa
            F+WQZKXK0sp+5LJ0IWqxkEnQxXoWIqCNTVbjllrFntYjrV0LPBtkNNL/PtS0r21IbNUy
            W6P6k7NdwW1uF7LbtPRWQJsFLkeHe9bBHBdAK7CtW5mrkeKi5bkmsy5lFQKF7nr3u+AN
            r3jHS97ymre7D5HudR0kT+VC1JIIywxCoAgY7MYzJ+59byNro5qGqHe9BFoBfvOry4ia
            xiF3zctzV0DgghoYNPJFiGKOy9R//jeXQu1KfxmiXePitMLKRI97M9xZhsByGPCsbTsZ
            emKvwbd6Ed4vYcr5hNY6dT8tjuKLTxNjg9DXuSYDqehGzFNxOqTDvO3Pb8WC0v7kmG0P
            jiAUENyYXqr4n5DFMZGjXJkeYys18VwyWIhIuS3veH4P+fGM1UmWzJZZ/7kkBqhDQNwc
            ZIo2QE+eG5ev+hAkE8awA8qz3vZcw4cIesUFOjTiCN2cJ6QXNT5NtJll/D8vF0TN/6tr
            oCf95c9s2L/hoyveOD2u+U0ZLqE+7N9I7a7PnPrI5wto3Fg9r1j2+XxPUButHfY/iFgR
            NDfWNZyLbJ9XNwTTI3SzhpC93TO/DyJijmBfNxRtrjIaMLj1M14AquoIVdvazt6hsU2c
            vyxDyJ4XDqYN3RKRdCu42w8ScIOnem0FR0TbeAl23NydTBgKF9jwTjS/+01sS/sY4BC6
            8rzpHe4/S2Tg+Q44Tr+dXxIKF9/vNleCK85TgxeEzp3Rt8EgHk4PerwgGP/P+IAUvnCa
            GlS4FG+qxIcW83lLkN3tPo3I/ZPcMaeckZ2eIFUgLfF+imVnzHZtveUyEZLrZecxy9mN
            Ff24pa/l5AT5+dPhDQXQBpvqlrO6YSbiGpEbfaFO3rXH0jqRpF9G3z3HTZbB3jmxm0XO
            Eak5Z4JdY2Uqe8jDtntZsJ7119y47+jM9X/oTjrBj+XThnZ6ffuZs2kvXu2SDy7hB6J1
            bA8YN3d+M3DRt3mBuN02kW4c5gUjXF6PKvWqD3zD59J6bJyeNqHftOwpjZfSY+PXo6rD
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
        x = (ws / 2) - (748 / 2)
        y = (hs / 2) - (584 / 2)
        self.master.geometry('%dx%d+%d+%d' % (748,584,x,y))
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.frmStatus = LabelFrame(self.top, text='')
        self.frmStatus.place(relx=0.011, rely=0.767, relwidth=0.483, relheight=0.111)

        self.tabMachine = Notebook(self.top)
        self.tabMachine.place(relx=0.011, rely=0.137, relwidth=0.483, relheight=0.303)

        self.tabMachine__Tab1 = Frame(self.tabMachine)
        self.cmdApplyAxisSpeed = Button(self.tabMachine__Tab1, text='应用', command=self.cmdApplyAxisSpeed_Cmd)
        self.cmdApplyAxisSpeed.place(relx=0.288, rely=0.745, relwidth=0.402, relheight=0.155)
        self.txtAccelerationVar = StringVar(value='100')
        self.txtAcceleration = Entry(self.tabMachine__Tab1, textvariable=self.txtAccelerationVar)
        self.txtAcceleration.place(relx=0.731, rely=0.497, relwidth=0.224, relheight=0.155)
        self.txtXMaxSpeedVar = StringVar(value='50')
        self.txtXMaxSpeed = Entry(self.tabMachine__Tab1, textvariable=self.txtXMaxSpeedVar)
        self.txtXMaxSpeed.place(relx=0.731, rely=0.099, relwidth=0.224, relheight=0.155)
        self.txtYMaxSpeedVar = StringVar(value='50')
        self.txtYMaxSpeed = Entry(self.tabMachine__Tab1, textvariable=self.txtYMaxSpeedVar)
        self.txtYMaxSpeed.place(relx=0.731, rely=0.298, relwidth=0.224, relheight=0.155)
        self.txtXSpeedVar = StringVar(value='100')
        self.txtXSpeed = Entry(self.tabMachine__Tab1, textvariable=self.txtXSpeedVar)
        self.txtXSpeed.place(relx=0.244, rely=0.099, relwidth=0.224, relheight=0.155)
        self.txtYSpeedVar = StringVar(value='120')
        self.txtYSpeed = Entry(self.tabMachine__Tab1, textvariable=self.txtYSpeedVar)
        self.txtYSpeed.place(relx=0.244, rely=0.298, relwidth=0.224, relheight=0.155)
        self.txtZSpeedVar = StringVar(value='80')
        self.txtZSpeed = Entry(self.tabMachine__Tab1, textvariable=self.txtZSpeedVar)
        self.txtZSpeed.place(relx=0.244, rely=0.497, relwidth=0.224, relheight=0.155)
        self.style.configure('TlblAcceleration.TLabel', anchor='e')
        self.lblAcceleration = Label(self.tabMachine__Tab1, text='加速度', style='TlblAcceleration.TLabel')
        self.lblAcceleration.place(relx=0.51, rely=0.497, relwidth=0.18, relheight=0.106)
        self.style.configure('TlblXMaxSpeed.TLabel', anchor='e')
        self.lblXMaxSpeed = Label(self.tabMachine__Tab1, text='X轴最快', style='TlblXMaxSpeed.TLabel')
        self.lblXMaxSpeed.place(relx=0.51, rely=0.099, relwidth=0.18, relheight=0.106)
        self.style.configure('TlblYMaxSpeed.TLabel', anchor='e')
        self.lblYMaxSpeed = Label(self.tabMachine__Tab1, text='Y轴最快', style='TlblYMaxSpeed.TLabel')
        self.lblYMaxSpeed.place(relx=0.51, rely=0.298, relwidth=0.18, relheight=0.106)
        self.style.configure('TlblXSpeed.TLabel', anchor='e')
        self.lblXSpeed = Label(self.tabMachine__Tab1, text='X轴速度', style='TlblXSpeed.TLabel')
        self.lblXSpeed.place(relx=0.022, rely=0.099, relwidth=0.18, relheight=0.106)
        self.style.configure('TlblYSpeed.TLabel', anchor='e')
        self.lblYSpeed = Label(self.tabMachine__Tab1, text='Y轴速度', style='TlblYSpeed.TLabel')
        self.lblYSpeed.place(relx=0.022, rely=0.298, relwidth=0.18, relheight=0.106)
        self.style.configure('TlblZSpeed.TLabel', anchor='e')
        self.lblZSpeed = Label(self.tabMachine__Tab1, text='Z轴速度', style='TlblZSpeed.TLabel')
        self.lblZSpeed.place(relx=0.022, rely=0.497, relwidth=0.18, relheight=0.106)
        self.tabMachine.add(self.tabMachine__Tab1, text='轴速度（越小越快）')

        self.tabMachine__Tab2 = Frame(self.tabMachine)
        self.txtPenWidthVar = StringVar(value='0.6')
        self.txtPenWidth = Entry(self.tabMachine__Tab2, textvariable=self.txtPenWidthVar)
        self.txtPenWidth.place(relx=0.776, rely=0.298, relwidth=0.18, relheight=0.155)
        self.txtZLiftStepsVar = StringVar(value='130')
        self.txtZLiftSteps = Entry(self.tabMachine__Tab2, textvariable=self.txtZLiftStepsVar)
        self.txtZLiftSteps.place(relx=0.776, rely=0.099, relwidth=0.18, relheight=0.155)
        self.txtYBacklashVar = StringVar(value='0')
        self.txtYBacklash = Entry(self.tabMachine__Tab2, textvariable=self.txtYBacklashVar)
        self.txtYBacklash.place(relx=0.355, rely=0.696, relwidth=0.18, relheight=0.155)
        self.txtYStepsPerCmVar = StringVar(value='1886')
        self.txtYStepsPerCm = Entry(self.tabMachine__Tab2, textvariable=self.txtYStepsPerCmVar)
        self.txtYStepsPerCm.place(relx=0.355, rely=0.497, relwidth=0.18, relheight=0.155)
        self.txtXBacklashVar = StringVar(value='94')
        self.txtXBacklash = Entry(self.tabMachine__Tab2, textvariable=self.txtXBacklashVar)
        self.txtXBacklash.place(relx=0.355, rely=0.298, relwidth=0.18, relheight=0.155)
        self.txtXStepsPerCmVar = StringVar(value='1886')
        self.txtXStepsPerCm = Entry(self.tabMachine__Tab2, textvariable=self.txtXStepsPerCmVar)
        self.txtXStepsPerCm.place(relx=0.355, rely=0.099, relwidth=0.18, relheight=0.155)
        self.style.configure('TlblPenWidth.TLabel', anchor='e')
        self.lblPenWidth = Label(self.tabMachine__Tab2, text='笔尖直径', style='TlblPenWidth.TLabel')
        self.lblPenWidth.place(relx=0.576, rely=0.298, relwidth=0.158, relheight=0.106)
        self.style.configure('TlblZLiftSteps.TLabel', anchor='e')
        self.lblZLiftSteps = Label(self.tabMachine__Tab2, text='Z轴升起', style='TlblZLiftSteps.TLabel')
        self.lblZLiftSteps.place(relx=0.576, rely=0.099, relwidth=0.158, relheight=0.106)
        self.style.configure('TlblYBacklash.TLabel', anchor='e')
        self.lblYBacklash = Label(self.tabMachine__Tab2, text='Y轴回差', style='TlblYBacklash.TLabel')
        self.lblYBacklash.place(relx=0.066, rely=0.696, relwidth=0.269, relheight=0.106)
        self.style.configure('TlblYStepsPerCm.TLabel', anchor='e')
        self.lblYStepsPerCm = Label(self.tabMachine__Tab2, text='Y轴每CM步进数', style='TlblYStepsPerCm.TLabel')
        self.lblYStepsPerCm.place(relx=0.066, rely=0.497, relwidth=0.269, relheight=0.106)
        self.style.configure('TlblXBacklash.TLabel', anchor='e')
        self.lblXBacklash = Label(self.tabMachine__Tab2, text='X轴回差', style='TlblXBacklash.TLabel')
        self.lblXBacklash.place(relx=0.066, rely=0.298, relwidth=0.269, relheight=0.106)
        self.style.configure('TlblXStepsPerCm.TLabel', anchor='e')
        self.lblXStepsPerCm = Label(self.tabMachine__Tab2, text='X轴每CM步进数', style='TlblXStepsPerCm.TLabel')
        self.lblXStepsPerCm.place(relx=0.066, rely=0.099, relwidth=0.269, relheight=0.106)
        self.tabMachine.add(self.tabMachine__Tab2, text='控制板参数')

        self.tabPosition = Notebook(self.top)
        self.tabPosition.place(relx=0.011, rely=0.452, relwidth=0.483, relheight=0.303)

        self.tabPosition__Tab1 = Frame(self.tabPosition)
        self.cmdZMicroUp = Button(self.tabPosition__Tab1, text='→', command=self.cmdZMicroUp_Cmd)
        self.cmdZMicroUp.place(relx=0.576, rely=0.298, relwidth=0.091, relheight=0.205)
        self.cmdZMicroDown = Button(self.tabPosition__Tab1, text='←', command=self.cmdZMicroDown_Cmd)
        self.cmdZMicroDown.place(relx=0.399, rely=0.298, relwidth=0.091, relheight=0.205)
        self.cmdYUp = Button(self.tabPosition__Tab1, text='↑', command=self.cmdYUp_Cmd)
        self.cmdYUp.place(relx=0.177, rely=0.099, relwidth=0.091, relheight=0.205)
        self.cmdYDown = Button(self.tabPosition__Tab1, text='↓', command=self.cmdYDown_Cmd)
        self.cmdYDown.place(relx=0.177, rely=0.497, relwidth=0.091, relheight=0.205)
        self.cmdXLeft = Button(self.tabPosition__Tab1, text='←', command=self.cmdXLeft_Cmd)
        self.cmdXLeft.place(relx=0.089, rely=0.298, relwidth=0.091, relheight=0.205)
        self.cmdXRight = Button(self.tabPosition__Tab1, text='→', command=self.cmdXRight_Cmd)
        self.cmdXRight.place(relx=0.266, rely=0.298, relwidth=0.091, relheight=0.205)
        self.cmdZUp = Button(self.tabPosition__Tab1, text='↑', command=self.cmdZUp_Cmd)
        self.cmdZUp.place(relx=0.488, rely=0.099, relwidth=0.091, relheight=0.205)
        self.cmdZDown = Button(self.tabPosition__Tab1, text='↓', command=self.cmdZDown_Cmd)
        self.cmdZDown.place(relx=0.488, rely=0.497, relwidth=0.091, relheight=0.205)
        self.cmdResetX = Button(self.tabPosition__Tab1, text='X清零', command=self.cmdResetX_Cmd)
        self.cmdResetX.place(relx=0.731, rely=0.099, relwidth=0.202, relheight=0.155)
        self.cmdResetY = Button(self.tabPosition__Tab1, text='Y清零', command=self.cmdResetY_Cmd)
        self.cmdResetY.place(relx=0.731, rely=0.298, relwidth=0.202, relheight=0.155)
        self.cmdResetZ = Button(self.tabPosition__Tab1, text='Z清零', command=self.cmdResetZ_Cmd)
        self.cmdResetZ.place(relx=0.731, rely=0.497, relwidth=0.202, relheight=0.155)
        self.cmdResetXYZ = Button(self.tabPosition__Tab1, text='全部清零', command=self.cmdResetXYZ_Cmd)
        self.cmdResetXYZ.place(relx=0.731, rely=0.696, relwidth=0.202, relheight=0.155)
        self.style.configure('TlblXY.TLabel', anchor='center')
        self.lblXY = Label(self.tabPosition__Tab1, text='XY', style='TlblXY.TLabel')
        self.lblXY.place(relx=0.177, rely=0.795, relwidth=0.08, relheight=0.124)
        self.style.configure('TlblZ.TLabel', anchor='center')
        self.lblZ = Label(self.tabPosition__Tab1, text='Z', style='TlblZ.TLabel')
        self.lblZ.place(relx=0.488, rely=0.795, relwidth=0.091, relheight=0.106)
        self.tabPosition.add(self.tabPosition__Tab1, text='设定原点')

        self.tabPosition__Tab2 = Frame(self.tabPosition)
        self.cmdMoveToRightBottom = Button(self.tabPosition__Tab2, text='右下角', command=self.cmdMoveToRightBottom_Cmd)
        self.cmdMoveToRightBottom.place(relx=0.643, rely=0.795, relwidth=0.247, relheight=0.124)
        self.cmdMoveToLeftBottom = Button(self.tabPosition__Tab2, text='左下角', command=self.cmdMoveToLeftBottom_Cmd)
        self.cmdMoveToLeftBottom.place(relx=0.643, rely=0.621, relwidth=0.247, relheight=0.124)
        self.cmdMoveToRightUp = Button(self.tabPosition__Tab2, text='右上角', command=self.cmdMoveToRightUp_Cmd)
        self.cmdMoveToRightUp.place(relx=0.643, rely=0.447, relwidth=0.247, relheight=0.124)
        self.cmdMoveToLeftUp = Button(self.tabPosition__Tab2, text='左上角', command=self.cmdMoveToLeftUp_Cmd)
        self.cmdMoveToLeftUp.place(relx=0.643, rely=0.273, relwidth=0.247, relheight=0.124)
        self.cmdUpdateMinMax = Button(self.tabPosition__Tab2, text='分析', command=self.cmdUpdateMinMax_Cmd)
        self.cmdUpdateMinMax.place(relx=0.643, rely=0.099, relwidth=0.247, relheight=0.124)
        self.txtMaxYVar = StringVar(value='')
        self.txtMaxY = Entry(self.tabPosition__Tab2, state='readonly', textvariable=self.txtMaxYVar)
        self.txtMaxY.place(relx=0.288, rely=0.795, relwidth=0.202, relheight=0.112)
        self.txtMinYVar = StringVar(value='')
        self.txtMinY = Entry(self.tabPosition__Tab2, state='readonly', textvariable=self.txtMinYVar)
        self.txtMinY.place(relx=0.288, rely=0.578, relwidth=0.202, relheight=0.112)
        self.txtMaxXVar = StringVar(value='')
        self.txtMaxX = Entry(self.tabPosition__Tab2, state='readonly', textvariable=self.txtMaxXVar)
        self.txtMaxX.place(relx=0.288, rely=0.366, relwidth=0.202, relheight=0.112)
        self.txtMinXVar = StringVar(value='')
        self.txtMinX = Entry(self.tabPosition__Tab2, state='readonly', textvariable=self.txtMinXVar)
        self.txtMinX.place(relx=0.288, rely=0.149, relwidth=0.202, relheight=0.112)
        self.style.configure('TlblMaxY.TLabel', anchor='e')
        self.lblMaxY = Label(self.tabPosition__Tab2, text='Y最大', style='TlblMaxY.TLabel')
        self.lblMaxY.place(relx=0.133, rely=0.795, relwidth=0.114, relheight=0.106)
        self.style.configure('TlblMinY.TLabel', anchor='e')
        self.lblMinY = Label(self.tabPosition__Tab2, text='Y最小', style='TlblMinY.TLabel')
        self.lblMinY.place(relx=0.133, rely=0.578, relwidth=0.114, relheight=0.106)
        self.style.configure('TlblMaxX.TLabel', anchor='e')
        self.lblMaxX = Label(self.tabPosition__Tab2, text='X最大', style='TlblMaxX.TLabel')
        self.lblMaxX.place(relx=0.133, rely=0.366, relwidth=0.114, relheight=0.106)
        self.style.configure('TlblMinX.TLabel', anchor='e')
        self.lblMinX = Label(self.tabPosition__Tab2, text='X最小', style='TlblMinX.TLabel')
        self.lblMinX.place(relx=0.133, rely=0.149, relwidth=0.114, relheight=0.106)
        self.tabPosition.add(self.tabPosition__Tab2, text='打印区域定位')

        self.tabPosition__Tab3 = Frame(self.tabPosition)
        self.chkSortCommandsVar = IntVar(value=1)
        self.chkSortCommands = Checkbutton(self.tabPosition__Tab3, text='排序绘图命令', variable=self.chkSortCommandsVar)
        self.chkSortCommands.place(relx=0.066, rely=0.547, relwidth=0.38, relheight=0.106)
        self.chkOmitRegionCmdVar = IntVar(value=0)
        self.chkOmitRegionCmd = Checkbutton(self.tabPosition__Tab3, text='忽略区域绘图命令', variable=self.chkOmitRegionCmdVar)
        self.chkOmitRegionCmd.place(relx=0.066, rely=0.348, relwidth=0.38, relheight=0.106)
        self.chkForceHoleVar = IntVar(value=0)
        self.chkForceHole = Checkbutton(self.tabPosition__Tab3, text='强制所有焊盘开孔', variable=self.chkForceHoleVar)
        self.chkForceHole.place(relx=0.066, rely=0.149, relwidth=0.402, relheight=0.106)
        self.txtMinHoleVar = StringVar(value='0.8')
        self.txtMinHole = Entry(self.tabPosition__Tab3, textvariable=self.txtMinHoleVar)
        self.txtMinHole.place(relx=0.753, rely=0.149, relwidth=0.18, relheight=0.112)
        self.style.configure('TlblMinHole.TLabel', anchor='e')
        self.lblMinHole = Label(self.tabPosition__Tab3, text='最小开孔(mm)', style='TlblMinHole.TLabel')
        self.lblMinHole.place(relx=0.465, rely=0.149, relwidth=0.269, relheight=0.106)
        self.tabPosition.add(self.tabPosition__Tab3, text='其他配置')

        self.cmdStartSimulator = Button(self.top, text='打开模拟器(E)', underline=6, command=self.cmdStartSimulator_Cmd)
        self.cmdStartSimulator.place(relx=0.032, rely=0.904, relwidth=0.162, relheight=0.07)
        self.top.bind_all('<Alt-E>', lambda e: self.cmdStartSimulator.focus_set() or self.cmdStartSimulator.invoke())
        self.top.bind_all('<Alt-e>', lambda e: self.cmdStartSimulator.focus_set() or self.cmdStartSimulator.invoke())

        self.cmdPause = Button(self.top, text='暂停(P)', underline=3, command=self.cmdPause_Cmd)
        self.cmdPause.place(relx=0.545, rely=0.904, relwidth=0.162, relheight=0.07)
        self.top.bind_all('<Alt-P>', lambda e: self.cmdPause.focus_set() or self.cmdPause.invoke())
        self.top.bind_all('<Alt-p>', lambda e: self.cmdPause.focus_set() or self.cmdPause.invoke())

        self.style.configure('TcmdStop.TButton', background='#ECE9D8')
        self.cmdStop = Button(self.top, text='停止(T)', underline=3, command=self.cmdStop_Cmd, style='TcmdStop.TButton')
        self.cmdStop.place(relx=0.802, rely=0.904, relwidth=0.162, relheight=0.07)
        self.top.bind_all('<Alt-T>', lambda e: self.cmdStop.focus_set() or self.cmdStop.invoke())
        self.top.bind_all('<Alt-t>', lambda e: self.cmdStop.focus_set() or self.cmdStop.invoke())

        self.frmManualCmd = LabelFrame(self.top, text='手动执行命令')
        self.frmManualCmd.place(relx=0.503, rely=0.767, relwidth=0.483, relheight=0.111)

        self.frmLog = LabelFrame(self.top, text='收发数据')
        self.frmLog.place(relx=0.503, rely=0.301, relwidth=0.483, relheight=0.454)

        self.frmSerial = LabelFrame(self.top, text='端口设置')
        self.frmSerial.place(relx=0.503, rely=0.137, relwidth=0.483, relheight=0.152)

        self.cmdStart = Button(self.top, text='启动(S)', underline=3, command=self.cmdStart_Cmd)
        self.cmdStart.place(relx=0.289, rely=0.904, relwidth=0.162, relheight=0.07)
        self.top.bind_all('<Alt-S>', lambda e: self.cmdStart.focus_set() or self.cmdStart.invoke())
        self.top.bind_all('<Alt-s>', lambda e: self.cmdStart.focus_set() or self.cmdStart.invoke())

        self.cmdChooseFile = Button(self.top, text='...', command=self.cmdChooseFile_Cmd)
        self.cmdChooseFile.place(relx=0.93, rely=0.014, relwidth=0.055, relheight=0.043)

        self.txtSourceFileVar = StringVar(value='')
        self.txtSourceFile = Entry(self.top, textvariable=self.txtSourceFileVar)
        self.txtSourceFile.place(relx=0.171, rely=0.014, relwidth=0.75, relheight=0.043)

        self.style.configure('TlblSourceFile.TLabel', anchor='e')
        self.lblSourceFile = Label(self.top, text='输入文件', style='TlblSourceFile.TLabel')
        self.lblSourceFile.place(relx=0.011, rely=0.014, relwidth=0.151, relheight=0.043)

        self.cmdExcellonFile = Button(self.top, text='...', command=self.cmdExcellonFile_Cmd)
        self.cmdExcellonFile.place(relx=0.93, rely=0.068, relwidth=0.055, relheight=0.043)

        self.txtExcellonFileVar = StringVar(value='')
        self.txtExcellonFile = Entry(self.top, textvariable=self.txtExcellonFileVar)
        self.txtExcellonFile.place(relx=0.171, rely=0.068, relwidth=0.75, relheight=0.043)

        self.style.configure('TlblDrillFile.TLabel', anchor='e')
        self.lblDrillFile = Label(self.top, text='Excellon文件(可选)', style='TlblDrillFile.TLabel')
        self.lblDrillFile.place(relx=0.011, rely=0.068, relwidth=0.151, relheight=0.043)

        self.scrVLog = Scrollbar(self.frmLog, orient='vertical')
        self.scrVLog.place(relx=0.909, rely=0.06, relwidth=0.047, relheight=0.728)

        self.style.configure('TlblKeepLogNum.TLabel', anchor='w')
        self.lblKeepLogNum = Label(self.frmLog, text='保留条目', style='TlblKeepLogNum.TLabel')
        self.lblKeepLogNum.place(relx=0.044, rely=0.875, relwidth=0.158, relheight=0.064)

        self.style.configure('TlblTimeToFinish.TLabel', anchor='w')
        self.lblTimeToFinish = Label(self.frmStatus, text='预计剩余时间：00:00:00', style='TlblTimeToFinish.TLabel')
        self.lblTimeToFinish.place(relx=0.488, rely=0.246, relwidth=0.446, relheight=0.385)

        self.cmdCloseSerial = Button(self.frmSerial, text='关闭', state='disabled', command=self.cmdCloseSerial_Cmd)
        self.cmdCloseSerial.place(relx=0.687, rely=0.539, relwidth=0.202, relheight=0.281)

        self.cmbTimeOutList = ['1s x 10','1s x 30','1s x 60','1s x 120','3s x 5','3s x 10','3s x 30','3s x 60',]
        self.cmbTimeOutVar = StringVar(value='1s x 10')
        self.cmbTimeOut = Combobox(self.frmSerial, state='readonly', text='1s x 10', textvariable=self.cmbTimeOutVar, values=self.cmbTimeOutList)
        self.cmbTimeOut.place(relx=0.244, rely=0.539, relwidth=0.38)

        self.cmdOpenSerial = Button(self.frmSerial, text='打开', command=self.cmdOpenSerial_Cmd)
        self.cmdOpenSerial.place(relx=0.687, rely=0.18, relwidth=0.202, relheight=0.281)

        self.cmbSerialList = ['COM1','COM2','COM3','COM4','COM5','COM6','COM6','COM7','COM8','COM9',]
        self.cmbSerialVar = StringVar(value='COM1')
        self.cmbSerial = Combobox(self.frmSerial, text='COM1', textvariable=self.cmbSerialVar, values=self.cmbSerialList)
        self.cmbSerial.place(relx=0.244, rely=0.18, relwidth=0.38)

        self.style.configure('TlblTimeOut.TLabel', anchor='e')
        self.lblTimeOut = Label(self.frmSerial, text='超时时间', style='TlblTimeOut.TLabel')
        self.lblTimeOut.place(relx=0.044, rely=0.539, relwidth=0.158, relheight=0.191)

        self.style.configure('TlblPortNo.TLabel', anchor='e')
        self.lblPortNo = Label(self.frmSerial, text='端口号', style='TlblPortNo.TLabel')
        self.lblPortNo.place(relx=0.044, rely=0.18, relwidth=0.158, relheight=0.191)

        self.cmdSendCommand = Button(self.frmManualCmd, text='执行', command=self.cmdSendCommand_Cmd)
        self.cmdSendCommand.place(relx=0.842, rely=0.231, relwidth=0.136, relheight=0.523)

        self.txtManualCommandVar = StringVar(value='')
        self.txtManualCommand = Entry(self.frmManualCmd, textvariable=self.txtManualCommandVar, font=('Courier New',12))
        self.txtManualCommand.place(relx=0.044, rely=0.231, relwidth=0.778, relheight=0.523)
        self.txtManualCommand.bind('<Return>', self.txtManualCommand_Return)

        self.style.configure('TlblQueueCmdNum.TLabel', anchor='w')
        self.lblQueueCmdNum = Label(self.frmStatus, text='剩余命令：0', style='TlblQueueCmdNum.TLabel')
        self.lblQueueCmdNum.place(relx=0.066, rely=0.246, relwidth=0.38, relheight=0.385)

        self.cmbKeepLogNumList = ['100','500','1000','2000','3000','4000','5000','8000','10000','20000',]
        self.cmbKeepLogNumVar = StringVar(value='100')
        self.cmbKeepLogNum = Combobox(self.frmLog, state='readonly', text='100', textvariable=self.cmbKeepLogNumVar, values=self.cmbKeepLogNumList)
        self.cmbKeepLogNum.place(relx=0.244, rely=0.875, relwidth=0.269)

        self.cmdSaveLog = Button(self.frmLog, text='保存', command=self.cmdSaveLog_Cmd)
        self.cmdSaveLog.place(relx=0.576, rely=0.875, relwidth=0.18, relheight=0.075)

        self.lstLogVar = StringVar(value='')
        self.lstLogFont = Font(font=('宋体',12))
        self.lstLog = Listbox(self.frmLog, listvariable=self.lstLogVar, yscrollcommand=self.scrVLog.set, font=self.lstLogFont)
        self.lstLog.place(relx=0.044, rely=0.06, relwidth=0.867, relheight=0.74)
        self.scrVLog['command'] = self.lstLog.yview

        self.cmdClearLog = Button(self.frmLog, text='清空', command=self.cmdClearLog_Cmd)
        self.cmdClearLog.place(relx=0.776, rely=0.875, relwidth=0.18, relheight=0.075)

class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        self.master.title('PrinterCnc Controller %s - https://github.com/cdhigh' % __Version__)
        #将计算机的串口列出来
        srls = []
        for srl in list_ports.comports():
            try:
                if sys.version_info[0] == 2:
                    srlDesc = srl[1].decode('gbk')
                else:
                    srlDesc = srl[1].encode('gbk').decode('utf-8')
                srls.append('%s [%s]' % (srl[0], srlDesc))
            except:
                srls.append('%s' % srl[0])
        if srls:
            srls.sort()
            self.cmbSerialList = srls
            self.cmbSerial['values'] = self.cmbSerialList
        if self.cmbSerialList:
            self.cmbSerial.current(0)
        self.cmbTimeOut.current(3)
        self.cmbTimeOutVar.set('1s x 120')
        self.cmbKeepLogNum.current(1)
        self.cmbKeepLogNumVar.set('500')
        self.shiftX = self.shiftY = 0.0 #用于平移整个图案
        self.allowedMinX = self.allowedMinY = 3000.0 #如果存在小于此值的坐标，则全部坐标加上此值
        self.cnc = CncMachine(self)
        self.RestoreConfig()
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
        
    def RestoreConfig(self):
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
            self.chkForceHoleVar.set(1 if config.getboolean('Main', 'ForceHole') else 0)
        except:
            pass
        try:
            self.txtMinHoleVar.set(config.get('Main', 'MinimumHole'))
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
            self.chkOmitRegionCmdVar.set(1 if config.getboolean('Main', 'OmitRegionCmd') else 0)
        except:
            pass
        try:
            self.chkSortCommandsVar.set(1 if config.getboolean('Main', 'SortCommands') else 0)
        except:
            pass
        try:
            self.simulatorWidth = config.get('Simulator', 'Width')
        except:
            self.simulatorWidth = '200'
        
        self.cnc.RestoreConfig(config)
        
        if self.allowedMinX < 0.0:
            self.allowedMinX = 0.0
        if self.allowedMinY < 0.0:
            self.allowedMinY = 0.0
        
    def saveConfig(self):
        cfgFilename = os.path.join(os.path.dirname(__file__), CFG_FILE)
        config = configparser.SafeConfigParser()
        config.add_section('Main')
        config.add_section('Simulator')
        config.set('Main', 'SerialTimeout', self.cmbTimeOutVar.get())
        config.set('Main', 'ForceHole', str(self.chkForceHoleVar.get()))
        config.set('Main', 'MinimumHole', self.txtMinHoleVar.get())
        config.set('Main', 'KeepLogNum', self.cmbKeepLogNumVar.get())
        config.set('Main', 'MinimumX', '%.1f' % self.allowedMinX)
        config.set('Main', 'MinimumY', '%.1f' % self.allowedMinY)
        config.set('Main', 'ShiftX', '%.1f' % self.shiftX)
        config.set('Main', 'ShiftY', '%.1f' % self.shiftY)
        config.set('Main', 'OmitRegionCmd', str(self.chkOmitRegionCmdVar.get()))
        config.set('Main', 'SortCommands', str(self.chkSortCommandsVar.get()))
        config.set('Simulator', 'Width', self.simulatorWidth)
        self.cnc.SaveConfig(config)
        
        try:
            with open(cfgFilename, 'w') as configFile:
                config.write(configFile)
        except:
            pass
            
    #安全清理现场，优雅退出：在窗口关闭前先保证线程退出
    def EV_WM_DELETE_WINDOW(self, event=None):
        self.saveConfig()
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
    
    def cmdExcellonFile_Cmd(self, event=None):
        sf = tkFileDialog.askopenfilename(initialfile=self.txtExcellonFileVar.get(), 
            filetypes=ExcellonFileMask())
        if sf:
            self.txtExcellonFileVar.set(sf)
        
    def cmdStart_Cmd(self, event=None):
        #在开始前先设定当前位置为原点
        filename = self.txtSourceFileVar.get()
        if not filename:
            showinfo('注意啦', '你是不是好像忘了选择输入文件了？')
            return
        
        drillFile = self.txtExcellonFileVar.get().strip()
        
        if not self.ser and not self.hasSimulator():
            showinfo('注意啦', '请先打开串口或模拟器！')
            return
            
        if isGerberFile(filename):
            self.cmdPause.focus_set()
            self.ProcessGerberFile(filename, drillFile)
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
            showinfo('出错啦', 'Z轴步进设置有误，要求为1-255的正整数。')
            return
            
        self.SendCommand('z+%05d' % zLiftSteps)
        
    def cmdZUp_Cmd(self, event=None):
        try:
            zLiftSteps = int(self.txtZLiftStepsVar.get())
        except:
            zLiftSteps = 0
        
        if not (0 < zLiftSteps <= 255):
            showinfo('出错啦', 'Z轴步进设置有误，要求为1-255的正整数。')
            return
            
        self.SendCommand('z-%05d' % zLiftSteps)
    
    def cmdZMicroUp_Cmd(self, event=None):
        self.SendCommand('z-00020')
    
    def cmdZMicroDown_Cmd(self, event=None):
        self.SendCommand('z+00020')
    
    def cmdXRight_Cmd(self, event=None):
        xStepsPerCm = self.txtXStepsPerCmVar.get()
        self.SendCommand('x+' + xStepsPerCm.zfill(5))

    def cmdXLeft_Cmd(self, event=None):
        xStepsPerCm = self.txtXStepsPerCmVar.get()
        self.SendCommand('x-' + xStepsPerCm.zfill(5))

    def cmdYDown_Cmd(self, event=None):
        yStepsPerCm = self.txtYStepsPerCmVar.get()
        self.SendCommand('y+' + yStepsPerCm.zfill(5))

    def cmdYUp_Cmd(self, event=None):
        yStepsPerCm = self.txtYStepsPerCmVar.get()
        self.SendCommand('y-' + yStepsPerCm.zfill(5))
    
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
            self.ser = serial.Serial(self.cmbSerialVar.get().split()[0], 9600, timeout=self.serTimeout)
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
            if cmd.startswith('$'): #调试命令，需要上位机解析和转换
                cmd = cmd[1:]
                
            self.SendCommand(cmd)
        
    def cmdClearLog_Cmd(self, event=None):
        self.lstLog.delete(0, END)
        
    def cmdSaveLog_Cmd(self, event=None):
        sf = tkFileDialog.asksaveasfilename(filetypes=[("Log File","*.log"),("Text File","*.txt"),("All Files", "*")])
        if sf:
            self.saveLogToFile(sf)
    
    def cmdResetX_Cmd(self, event=None):
        self.AddCommandLog(b'@resetx') #虚拟命令，实际上没有下发到控制板
        self.cnc.Reset(x=True)
        if self.hasSimulator():
            self.simulator.Reset(x=True)
    
    def cmdResetY_Cmd(self, event=None):
        self.AddCommandLog(b'@resety') #虚拟命令，实际上没有下发到控制板
        self.cnc.Reset(y=True)
        if self.hasSimulator():
            self.simulator.Reset(y=True)
    
    def cmdResetZ_Cmd(self, event=None):
        self.AddCommandLog(b'@resetz') #虚拟命令，实际上没有下发到控制板
        self.cnc.Reset(z=True)
        if self.hasSimulator():
            self.simulator.Reset(z=True)
    
    def cmdResetXYZ_Cmd(self, event=None):
        if not self.ser and not self.hasSimulator():
            showinfo('注意啦', '请先打开串口或模拟器然后再执行命令。')
            return False
            
        self.cmdResetX_Cmd()
        self.cmdResetY_Cmd()
        self.cmdResetZ_Cmd()
        
    #设置控制板的XYZ轴运动速度，值越小运动越快，注意速度太快则扭矩下降，并有可能啸叫和丢步
    def cmdApplyAxisSpeed_Cmd(self, event=None):
        if not self.ser and not self.hasSimulator():
            showinfo('注意啦', '请先打开串口或模拟器然后再执行命令。')
            return False
            
        xSpeed = self.txtXSpeedVar.get()
        xMaxSpeed = self.txtXMaxSpeedVar.get()
        ySpeed = self.txtYSpeedVar.get()
        yMaxSpeed = self.txtYMaxSpeedVar.get()
        zSpeed = self.txtZSpeedVar.get()
        speedAcceleration = self.txtAccelerationVar.get()
        try:
            xSpeed = int(xSpeed)
            xMaxSpeed = int(xMaxSpeed)
            ySpeed = int(ySpeed)
            yMaxSpeed = int(yMaxSpeed)
            zSpeed = int(zSpeed)
            speedAcceleration = int(speedAcceleration)
        except Exception as e:
            showinfo('出错啦', str(e))
            return
        
        if ((not (0 < xSpeed < 1000)) or (not (0 < xMaxSpeed < 1000)) or (not (0 < ySpeed < 1000))
            or (not (0 < yMaxSpeed < 1000)) or (not (0 < zSpeed < 1000)) or (not (0 < speedAcceleration < 10000))):
            showinfo('注意啦', '部分参数设置错误，需要为小于999的正整数。')
            return
            
        self.SendCommand('XS%03d' % xSpeed)
        self.SendCommand('XE%03d' % xMaxSpeed)
        self.SendCommand('YS%03d' % ySpeed)
        self.SendCommand('YE%03d' % yMaxSpeed)
        self.SendCommand('Z%03d' % zSpeed)
        self.SendCommand('A%04d' % speedAcceleration)
    
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
            
        self.cnc.UpdateProperties()
        for cmd in self.cnc.TranslateCmd(x, y, '2'):
            self.SendCommand(cmd)
        
    #移动至右上角，用于确定打印区域
    def cmdMoveToRightUp_Cmd(self, event=None):
        try:
            x = int(self.txtMaxXVar.get())
            y = int(self.txtMinYVar.get())
        except:
            showinfo('出错啦', '请先更新文件信息。')
            return
        
        self.cnc.UpdateProperties()
        for cmd in self.cnc.TranslateCmd(x, y, '2'):
            self.SendCommand(cmd)
        
    #移动至左下角，用于确定打印区域
    def cmdMoveToLeftBottom_Cmd(self, event=None):
        try:
            x = int(self.txtMinXVar.get())
            y = int(self.txtMaxYVar.get())
        except:
            showinfo('出错啦', '请先更新文件信息。')
            return
        
        self.cnc.UpdateProperties()
        for cmd in self.cnc.TranslateCmd(x, y, '2'):
            self.SendCommand(cmd)
    
    #移动至右上角，用于确定打印区域
    def cmdMoveToRightBottom_Cmd(self, event=None):
        try:
            x = int(self.txtMaxXVar.get())
            y = int(self.txtMaxYVar.get())
        except:
            showinfo('出错啦', '请先更新文件信息。')
            return
        
        self.cnc.UpdateProperties()
        for cmd in self.cnc.TranslateCmd(x, y, '2'):
            self.SendCommand(cmd)
    
    #将命令压到队列中以供另一个线程取用，出错返回False
    def SendCommand(self, cmd, penWidth=None):
        if not cmd:
            return True
        
        try:
            cmd = cmd.encode()
        except:
            pass
            
        self.evStop.clear()
        self.evPause.clear()
        try:
            state = self.simulator.state()
        except: #模拟器不存在则发送到实际控制板
            if self.ser:
                self.cmdQueue.put(cmd, block=True)
            else:
                showinfo('注意啦', '请先打开串口然后再执行命令。')
                return False
        else: #有模拟器
            response = self.simulator.putDrawCmd(cmd, penWidth)
            self.AddCommandLog(cmd + b' -> sim')
            self.lstLog.update_idletasks()
            if response != b'*':
                if not askyesno('命令出错', '模拟器返回命令出错标识，是否继续下发其他命令？'):
                    return False
        
        return True
        
    def AddCommandLog(self, cmd, isResponse=False, forceUpdateNum=0):
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
        
        #ListBox界面刷新效率比较低，为效率考虑，每隔一定的行数再刷新一次
        if forceUpdateNum > 0:
            if logNum % forceUpdateNum == 0:
                self.lstLog.see(END)
                #self.lstLog.update_idletasks()
        else: #马上刷新
            self.lstLog.see(END)
        
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
        
        forceHole = bool(self.chkForceHoleVar.get())
        try: #获取用户要求的最小孔径(mm)
            minHole = float(self.txtMinHoleVar.get())
        except:
            self.txtMinHoleVar.set('0.8')
            minHole = 0.8
        
        for line in lines[:200]: #在前面200行获取元信息，一般足够了
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
            apt = Aperture.GenAperture(line, gerberInfo['unit'], forceHole, minHole)
            if apt:
                gerberInfo['apertures'][apt.name] = apt
        
        dictRet['header'] = gerberInfo
        
        #预处理文件内容，将绘图行转换为单位为微米的浮点数元祖，以便后续处理
        #并且如果需要，则经过数学处理去掉负数坐标和平移图案
        minX, maxX, minY, maxY, xShifted, yShifted = self.PreProcess(lines, gerberInfo)
        dictRet['lines'] = lines
        dictRet['minX'] = minX
        dictRet['maxX'] = maxX
        dictRet['minY'] = minY
        dictRet['maxY'] = maxY
        dictRet['xShifted'] = xShifted
        dictRet['yShifted'] = yShifted
        return dictRet
        
    #分析Gerber文件，将其中的绘图命令转换成CNC合法的命令发送
    def ProcessGerberFile(self, filename, drillFile):
        #预处理文件，提取元信息和进行单位转换
        gerber = self.ParseGerberFile(filename)
        
        #再遍历一次文件，提取所有的钻孔信息，保存到一个列表中
        holes = self.GatherHoles(gerber, drillFile)
        
        if self.evExit.is_set() or gerber is None:
            return
        
        self.evStop.clear()
        self.evPause.clear()
        self.cmdPause['text'] = '暂停(P)'
        #清空队列
        self.cmdQueue.queue.clear()
        
        #获取笔尖宽度，界面上的单位是毫米，软件需要转换为微米
        try:
            penWidth = float(self.txtPenWidthVar.get()) * 1000.0
        except:
            penWidth = 1000.0 #默认1毫米
        if penWidth < 100: #假定笔不会太小，默认最小为0.1mm
            penWidth = 100
        
        #开始逐行处理文件
        grblApt = re.compile(r'^.*?D(\d+?)\*') #aperture切换行
        x = y = prevX = prevY = prevX4Holes = prevY4Holes = 0.0
        regionModeOn = False
        curAperture = defAperture = Aperture() #新建一个默认大小的Aperture
        lines = gerber['lines']
        
        self.cnc.UpdateProperties() #将界面参数更新到cnc属性
        self.cmdApplyAxisSpeed_Cmd() #更新控制板的各轴速度
        self.cnc.Reset(x=True, y=True) #设定当前点为原点
        
        if self.hasSimulator(): #使用模拟器
            self.simulator.Reset(x=True, y=True)
            self.simulator.UpdateProperties()
        
        commands = [] #保存最终将要画的线条命令，每个元素为一个（x,y,z）
        for lineNo, line in enumerate(lines, 1):
            if self.evExit.is_set():
                return
            
            if type(line) is tuple: #坐标行
                xInFile, yInFile, zInFile = line
                
                #如果需要，可能需要画多根细线组成粗线
                #返回一个元组列表[(x1,y1,z1),(x2,y2,z2),...]
                if zInFile == '2': #直接移动绘图笔的命令
                    lines2draw = [(xInFile, yInFile, zInFile)]
                elif regionModeOn:
                    if self.chkOmitRegionCmdVar.get():
                        continue #如果设置忽略区域命令，则区域模式打开后跳过所有中间的绘图命令
                    else: #区域模式打开后线条宽度为0
                        lines2draw = defAperture.Render(prevX, prevY, xInFile, yInFile, zInFile, penWidth)
                else:
                    if not curAperture:
                        curAperture = defAperture
                    lines2draw = curAperture.Render(prevX, prevY, xInFile, yInFile, zInFile, penWidth)
                    
                for x, y, z in lines2draw:
                    #绘图指令用直线逼近斜线精度为0.1mm，移动时1mm足够，再大还是可以
                    splitThreshold = 100 if z == '1' else 1000
                    
                    #一条斜线，雕刻机不支持直接画斜线，要用一系列的横线竖线逼近
                    if (x != prevX) and (y != prevY):
                        #第一步：斜线转成直线集合
                        for point in self.SplitInclined(prevX, prevY, x, y, splitThreshold):
                            if zInFile == '1':
                                #第二步：如果直线遇到钻孔，则跳过孔位
                                for out in self.KeepAwayFromHoles(holes, prevX4Holes, prevY4Holes, 
                                                    point[0], point[1], z, penWidth):
                                    commands.append(out)
                                    #第三步：转换成雕刻机步进电机运行指令
                                    #for cmd in self.cnc.TranslateCmd(out[0], out[1], out[2]):
                                    #    ret = self.SendCommand(cmd, penWidth)
                                    #    if not ret:
                                    #        return
                                prevX4Holes = point[0]
                                prevY4Holes = point[1]                                
                            else: # '2' or '3'，不用管钻孔的事
                                commands.append((point[0], point[1], z))
                                #for cmd in self.cnc.TranslateCmd(point[0], point[1], z):
                                #    ret = self.SendCommand(cmd, penWidth)
                                #    if not ret:
                                #        return
                    else:
                        if zInFile == '1':
                            #跳过钻孔区域
                            for out in self.KeepAwayFromHoles(holes, prevX4Holes, prevY4Holes, x, y, z, penWidth):
                                commands.append(out)
                                #for cmd in self.cnc.TranslateCmd(out[0], out[1], out[2]):
                                #    ret = self.SendCommand(cmd, penWidth)
                                #    if not ret:
                                #        return
                        else: # 2 or 3
                            commands.append((x, y, z))
                            #for cmd in self.cnc.TranslateCmd(x, y, z):
                            #    ret = self.SendCommand(cmd, penWidth)
                            #    if not ret:
                            #        return
                                
                    prevX = prevX4Holes = x
                    prevY = prevY4Holes = y
            elif not line.startswith('G04'): #跳过注释行
                mat = grblApt.match(line)
                if mat: #aperture切换行
                    try:
                        aptNum = int(mat.group(1))
                    except:
                        showinfo('出错啦', '解读文件时出现aperture编号出错的情况 [第 %d 行]！' % lineNo)
                        return
                    
                    if aptNum == 3: #在当前点绘aperture命令
                        if not curAperture:
                            showinfo('出错啦', '没有设置aperture就开始绘图！ [第 %d 行]！' % lineNo)
                            continue #忽略好了，不用退出
                        
                        lines2draw = curAperture.Render(prevX, prevY, prevX, prevY, '3', penWidth)
                        for x, y, z in lines2draw:
                            #一条斜线，雕刻机不支持直接画斜线，要用一系列的横线竖线逼近
                            if (z == '1') and (x != prevX) and (y != prevY):
                                for point in self.SplitInclined(prevX, prevY, x, y):
                                    commands.append((point[0], point[1], z))
                                    #for cmd in self.cnc.TranslateCmd(point[0], point[1], z):
                                    #    ret = self.SendCommand(cmd, penWidth)
                                    #    if not ret:
                                    #        return
                            else:
                                commands.append((x, y, z))
                                #for cmd in self.cnc.TranslateCmd(x, y, z):
                                #    ret = self.SendCommand(cmd, penWidth)
                                #    if not ret:
                                #        return
                            prevX = prevX4Holes = x
                            prevY = prevY4Holes = y
                        
                    elif aptNum >= 10: #切换当前的aperture    
                        aptName = 'D%d' % aptNum
                        curAperture = gerber['header']['apertures'].get(aptName, defAperture)
                elif 'G36*' in line: #区域模式开始
                    regionModeOn = True
                elif 'G37*' in line: #区域模式关闭
                    regionModeOn = False
        
        if self.chkSortCommandsVar.get():
            self.SortCommands(commands) #命令排序，为了减少雕刻笔移动距离，提高雕刻速度
        
        for x, y, z in commands:
            for cmd in self.cnc.TranslateCmd(x, y, z):
                ret = self.SendCommand(cmd, penWidth)
                if not ret:
                    return
        
        #归位，为了更快，也走斜线路径回零位，逼近精度为1000(1mm)
        if (prevX != 0.0) and (prevY != 0.0):
            for point in self.SplitInclined(prevX, prevY, 0.0, 0.0, 1000):
                for cmd in self.cnc.TranslateCmd(point[0], point[1], '2'):
                    self.SendCommand(cmd, penWidth)
        else:
            for cmd in self.cnc.TranslateCmd(0.0, 0.0, '2'):
                self.SendCommand(cmd, penWidth)
        
        #用于最后响铃提醒用
        self.SendCommand(END_CMD, None)
    
    #命令排序，为了减少雕刻笔移动距离，提高雕刻速度
    def SortCommands(self, commands):
        #将坐标点转换为线条列表
        lines = []
        prevX = prevY = 0.0
        for x, y, z in commands: #这里z只有1、2
            if z == '1':
                lines.append((prevX, prevY, x, y))
            prevX = x
            prevY = y
        
        if not lines:
            return
            
        #找出离原点最近的一根线
        minDis = 99999999.0
        minIdx = 0
        for (x1,y1,x2,y2), idx in enumerate(lines):
            dis = DistanceDotToDot(x1, y1, 0.0, 0.0)
            if dis < minDis:
                minDis = dis
                minIdx = idx
        
        #从第一根线起，一直寻找离前一跟线终点最近的另一根线
        newLines = []
        while lines:
            line1 = lines.pop(minIdx)
            newLines.append(line1)
            
            minDis = 99999999.0
            minIdx = 0
            prevX = line1[2]
            prevY = line1[3]
            for (x1,y1,x2,y2), idx in enumerate(lines):
                dis = DistanceDotToDot(x1, y1, prevX, prevY)
                if dis < minDis:
                    minDis = dis
                    minIdx = idx
        
        #将线段重新转换为坐标点列表
        commands[:] = []
        prevX = prevY = 0.0
        for x1, y1, x2, y2 in newLines:
            if x1 != prevX or y1 != prevY:
                commands.append((x1, y1, '2'))
            commands.append((x2, y2, '1'))
            prevX = x2
            prevY = y2
        
        return
        
    #判断此直线是否经过了焊盘钻孔区域，如果是，则适当处理跳过之，返回一个(x,y,z)列表
    def KeepAwayFromHoles(self, holes, x1, y1, x2, y2, z, penWidth):
        #return [(x2, y2, z)]
        if z != '1': #不是绘图指令
            return [(x2, y2, z)]
        elif x1 == x2 and y1 == y2:
            return [(x2, y2, z)]
            
        xLeft = min(x1, x2)
        xRight = max(x1, x2)
        yTop = min(y1, y2)
        yBottom = max(y1, y2)
        
        #开始时仅一条直线，如果碰到焊孔，则可能会拆分成几条直线
        res = [(xLeft, yTop, xRight, yBottom)]
        
        penHalf = penWidth / 2
        
        prevX = prevY = 0
        conflited = True
        
        #因为都是垂直线或水平线，所以比较好处理，而且为了更简化，将圆孔当做方孔处理
        if y1 == y2: #水平线
            while 1:
                conflited = False
                for idx, (x_1, y_1, x_2, y_2) in enumerate(res):
                    for xHole, yHole, diaHole in holes: #x,y,diameter
                        radius = diaHole / 2
                        #判断直线是否经过此孔
                        if y_1 - penHalf - radius <= yHole <= y_1 + penHalf + radius:
                            if (abs(xHole - x_1) <= radius + penHalf) and (abs(x_2 - xHole) <= radius + penHalf): #线全部在焊孔内
                                conflited = True #直接丢弃此线
                                break
                            elif x_1 - penHalf - radius < xHole <= x_1 + penHalf + radius: #左端重叠，左端截短
                                res.append((xHole + radius + penHalf, y_1, x_2, y_2))
                                conflited = True
                                break
                            elif x_2 - penHalf - radius <= xHole < x_2 + penHalf + radius: #右端重叠
                                res.append((x_1, y_1, xHole - radius - penHalf, y_2))
                                conflited = True
                                break
                            elif x_1 + penHalf + radius < xHole < x_2 - penHalf - radius: #在中间
                                res.append((x_1, y_1, xHole - radius - penHalf, y_2))
                                res.append((xHole + radius + penHalf, y_1, x_2, y_2))
                                conflited = True
                                break
                            
                    #对应的一根线和某个过孔冲突
                    if conflited:
                        res.pop(idx) #去掉有冲突的那根线
                        break #从头开始重新搜索
                
                #找完了，没有冲突
                if not conflited:
                    break
        else: #垂直线
            while 1:
                conflited = False
                for idx, (x_1, y_1, x_2, y_2) in enumerate(res):
                    for xHole, yHole, diaHole in holes: #x,y,diameter
                        radius = diaHole / 2
                        #判断直线是否经过此孔
                        if x_1 - penHalf - radius <= xHole <= x_1 + penHalf + radius:
                            if (abs(yHole - y_1) <= radius + penHalf) and (abs(y_2 - yHole) <= radius + penHalf): #线全部在焊孔内
                                conflited = True #直接丢弃此线
                                break
                            elif y_1 - penHalf - radius < yHole <= y_1 + penHalf + radius: #上端重叠，上端截短
                                res.append((x_1, yHole + radius + penHalf, x_2, y_2))
                                conflited = True
                                break
                            elif y_2 - penHalf - radius <= yHole < y_2 + penHalf + radius: #下端重叠
                                res.append((x_1, y_1, x_2, yHole - radius - penHalf))
                                conflited = True
                                break
                            elif y_1 + penHalf + radius < yHole < y_2 - penHalf - radius: #在中间
                                res.append((x_1, y_1, x_1, yHole - radius - penHalf))
                                res.append((x_1, yHole + radius + penHalf, x_1, y_2))
                                conflited = True
                                break
                            
                    #对应的一根线和某个过孔冲突
                    if conflited:
                        res.pop(idx) #去掉有冲突的那根线
                        break #从头开始重新搜索
                
                #找完了，没有冲突
                if not conflited:
                    break
        
        #根据原来的方向进行线段排序
        if y1 == y2: #水平线
            if x1 < x2: #从左至右
                resSorted = sorted(res, key=itemgetter(0))
            else: #从右至左
                resTmp = []
                for x_1, y_1, x_2, y_2 in res:
                    resTmp.append((x_2, y_2, x_1, y_1))
                resSorted = sorted(resTmp, key=itemgetter(0), reverse=True)
        else: #垂直线
            if y1 < y2: #从上到下
                resSorted = sorted(res, key=itemgetter(1))
            else:
                resTmp = []
                for x_1, y_1, x_2, y_2 in res:
                    resTmp.append((x_1, y_2, x_2, y_1))
                resSorted = sorted(resTmp, key=itemgetter(1), reverse=True)
        
        #开始输出一个逐点列表
        res = []
        prevX = x1
        prevY = y1
        for x_1, y_1, x_2, y_2 in resSorted:
            if x_1 != prevX or y_1 != prevY:
                res.append((x_1, y_1, '2'))
            res.append((x_2, y_2, '1'))
            prevX = x_2
            prevY = y_2
        
        if prevX != x2 or prevY != y2:
            res.append((x2, y2, '2'))
        
        return res
    
    #将RS274X坐标字符串格式的xy转换成浮点型（单位为微米），支持正负数，返回转换后的(x,y)元组
    def XY2Float(self, x, y, gerberInfo):
        #先去零
        #if (gerberInfo['zeroSuppress'] == 'L'): #忽略前导零
        #    x = x.lstrip('0 ')
        #    y = y.lstrip('0 ')
        #if (gerberInfo['zeroSuppress'] == 'T'): #忽略后导零
        #    x = x.rstrip('0 ')
        #    y = y.rstrip('0 ')
        
        try:
            x = int(x)
            y = int(y)
        except:
            return (None, None)
        
        #加小数点
        x /= pow(10, gerberInfo['xDecimal'])
        y /= pow(10, gerberInfo['yDecimal'])
        
        #将坐标数值统一转换成微米
        if gerberInfo['unit'] == 'inch':
            x = float(x) * 25.4 * 1000
            y = float(y) * 25.4 * 1000
        else: #mm
            x = float(x) * 1000
            y = float(y) * 1000
            
        #一个容错吧，控制板最长支持6位数(999 mm)
        if x > 999999.0:
            x = 999999.0
        if y > 999999.0:
            y = 999999.0
            
        return (x, y)
        
    
    #预处理文件，如果文件中有负坐标，则所有坐标都加上一个最小的负数，把所有坐标都变成正数
    #即使没有负数，如果有太小的值，也可以考虑加上一个固定的值，避免后续运算过程中出现负数
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
                linesNum.append(line)
                continue
                
            mat = grblExp.match(line)
            if mat: #当前行为坐标绘图行，则转换为浮点数，方便后续分析处理
                x, y = self.XY2Float(mat.group(1), mat.group(2), gerberInfo)
                z = mat.group(3)
                
                if x is None or y is None:
                    continue
                    
                #如果需要，整个图案平移
                x += self.shiftX
                y += self.shiftY
                
                #更新最大最小值，后续用于定框
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
            if type(line) is tuple: #坐标行
                lines[idx] = (line[0] + minXforCal, line[1] + minYforCal, line[2])
            else:
                lines[idx] = line
        
        #minX, maxX, minY, maxY, xShifted, yShifted
        return (minX + minXforCal, maxX + minXforCal, minY + minYforCal, maxY + minYforCal,
            self.shiftX + minXforCal, self.shiftY + minYforCal)
        
    #分析Gerber文件，提取里面的焊盘钻孔信息(x, y，直径)，为了简化，所有的钻孔都当做圆孔处理
    #考虑钻孔信息分布的复杂性，要模拟走一遍才能全部提取到所有信息
    def GatherHoles(self, gerber, drillFile):
        if self.evExit.is_set() or gerber is None:
            return
        
        #开始逐行处理文件
        grblApt = re.compile(r'^.*?D(\d+?)\*') #aperture切换行
        x = y = 0.0
        curAperture = defAperture = Aperture() #新建一个默认大小的Aperture
        lines = gerber['lines']
        holes = [] #(x, y, 直径) 单位为微米
        
        for lineNo, line in enumerate(lines, 1):
            if self.evExit.is_set():
                return
            
            if type(line) is tuple: #坐标行
                x, y, z = line
                if z == '3' and curAperture and curAperture.innerEdge1 > 0.0: #有钻孔的焊盘
                    holes.append((x, y, curAperture.innerEdge1))
                    
            elif not line.startswith('G04'): #跳过注释行
                mat = grblApt.match(line)
                if mat: #aperture切换行
                    try:
                        aptNum = int(mat.group(1))
                    except:
                        showinfo('出错啦', '解读文件时出现aperture编号出错的情况 [第 %d 行]！' % lineNo)
                        return
                    
                    if aptNum == 3: #在当前点绘aperture命令
                        if not curAperture:
                            showinfo('出错啦', '没有设置aperture就开始绘图！ [第 %d 行]！' % lineNo)
                            continue #忽略好了，不用退出
                        elif curAperture.innerEdge1 > 0.0:
                            holes.append((x, y, curAperture.innerEdge1))
                            
                    elif aptNum >= 10: #切换当前的aperture    
                        aptName = 'D%d' % aptNum
                        curAperture = gerber['header']['apertures'].get(aptName, defAperture)
        
        #如果额外的提供了钻孔文件，则将钻孔文件的数据合入
        if drillFile:
            try:
                with open(drillFile, 'r') as fd:
                    drillLines = [line.strip() for line in fd.read().split('\n')]
            except Exception as e:
                showinfo('出错啦', '无法打开钻孔文件，软件将忽略此错误，此文件中的数据将无效。\n%s' % str(e))
                return holes
            
            unit = 'INCH'
            tools = {} #钻头信息表
            curDiameter = 0.0
            xShifted = gerber['xShifted']
            yShifted = gerber['yShifted']
            toolDefineExpr = re.compile(r'^T(\d{1,4}).*?C([.0-9]+).*')
            toolChooseExpr = re.compile(r'^T(\d{1,2})')
            holeExpr = re.compile(r'^X(\d+)Y(\d+)')
            for line in drillLines:
                if not line or line.startswith(';'):
                    continue
                if line in ('INCH', 'METRIC'):
                    unit = line
                    continue
                    
                mat = toolDefineExpr.match(line)
                if mat: #tool定义行
                    toolNum = mat.group(1)
                    if len(toolNum) > 2: #后面两位是补偿量，忽略
                        toolNum = toolNum[:2]
                    toolDia = mat.group(2)
                    try:
                        toolDia = float(toolDia if toolDia[0] != '.' else '0' + toolDia)
                    except:
                        continue
                    #转换成微米
                    if unit == 'INCH':
                        toolDia = toolDia * 25.4 * 1000
                    else:
                        toolDia = toolDia * 1000
                        
                    tools[toolNum] = toolDia
                    continue
                
                mat = toolChooseExpr.match(line)
                if mat: #钻头选择行
                    curDiameter = tools.get(str(mat.group(1)), 0.0)
                    continue
                
                mat = holeExpr.match(line)
                if mat: #钻孔信息行
                    x = mat.group(1)
                    y = mat.group(2)
                    
                    #转换为微米
                    try:
                        if unit == 'INCH': #00.0000格式
                            x = float(x) / 10000 * 25.4 * 1000
                            y = float(y) / 10000 * 25.4 * 1000
                        else:
                            if len(x) == 5: #000.00格式
                                x = float(x) / 100 * 1000
                            else: #有两种格式：0000.00，000.000，仅使用3.3格式
                                x = float(x)
                            if len(y) == 5:
                                y = float(y) / 100 * 1000
                            else:
                                y = float(y)
                    except:
                        continue
                    
                    #如果图案已经整体平移了，则也要同步修正钻孔位置
                    x += xShifted
                    y += yShifted
                    
                    if curDiameter > 0.0:
                        holes.append((x, y, curDiameter))
                        #print('Add hole : (%.0f, %.0f, %.0f)' % (x, y, curDiameter))
                    
        return holes
        
    #将斜线分解转换成很多段的水平线和垂直线序列，因为雕刻机仅支持画水平线或垂直线
    #函数直接返回一个元祖列表[(x1,y1),(x2,y2),...]
    #参数坐标单位为微米，(x1,y1)为起始点，(x2,y2)为结束点
    #threshold为逼近的门限值，单位为微米
    def SplitInclined(self, x1, y1, x2, y2, threshold=100):
        if x1 == x2 or y1 == y2:
            return [(x2,y2)]
        
        x_half = abs(x1 - x2) / 2
        y_half = abs(y1 - y2) / 2
        xm = min(x1, x2) + x_half
        ym = min(y1, y2) + y_half
        if (x_half < threshold) or (y_half < threshold): #低于门限，直接返回
            if (x_half < y_half): #根据斜率决定先向哪个方向逼近
                return [(x1,ym),(x2,ym),(x2,y2)]
            else:
                return [(xm,y1),(xm,y2),(x2,y2)]
        else: #递归二分法逼近
            return self.SplitInclined(x1, y1, xm, ym, threshold) + self.SplitInclined(xm, ym, x2, y2, threshold)
        
    #单独的一个线程，在队列中取命令，然后发送给CNC控制板，并且等待控制板的答复
    def threadSendCommand(self, evStop, evExit, evPause, cmdQueue):
        #时间单位为毫秒
        timeToFinish = timeInLastCmds = avgForLastCmds = sumedCmdNum = 0
        cmdStartTime = cmdEndTime = None
        remainedCmd = 0
        forceUpdateNum = 10
        accuCmdNumForCalculate = 500 #统计过去500个命令用于预计剩下的时间
        
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
            if remainedCmd > 500:
                forceUpdateNum = 20
            elif remainedCmd > 50:
                forceUpdateNum = 5
            elif remainedCmd > 10:
                forceUpdateNum = 2
            else:
                forceUpdateNum = 0
                
            if not cmd:
                time.sleep(0.1) #出错了或队列空，睡0.1s先
                continue
            elif evStop.is_set(): #按停止键后需要清空队列
                cmdQueue.queue.clear()
                self.lblQueueCmdNum['text'] = '剩余命令：0'
                self.lblTimeToFinish['text'] = '预计剩余时间：00:00:00'
                continue
            
            if cmd == END_CMD:
                SoundNotify(False)
                continue
                
            cmdStartTime = datetime.datetime.now()
            try:
                self.ser.write(cmd)
            except Exception as e:
                self.AddCommandLog(('Err Write: %s' % cmd).encode(), forceUpdateNum=0)
                
            self.AddCommandLog(cmd, forceUpdateNum=forceUpdateNum)
            
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
                self.AddCommandLog(response, True, forceUpdateNum=forceUpdateNum)
                if response == b'#':
                    ignore = askyesno('命令错', '控制板返回命令执行出错标识，是否继续下发其他命令？')
                    if not ignore:
                        evStop.set()
                    
            else:
                self.AddCommandLog(b'Timeout', True, forceUpdateNum=0)
                SoundNotify()
                ignore = askyesno('答复超时', '控制板未响应，是否继续下发其他命令？')
                if not ignore:
                    evStop.set()
                    
            #确定此命令的执行时间，统计最近若干个命令的执行时间，用于预计剩余时间
            cmdEndTime = datetime.datetime.now()
            delta = cmdEndTime - cmdStartTime
            delta = delta.seconds * 1000 + delta.microseconds / 1000 #转换成毫秒
            timeInLastCmds += delta
            if sumedCmdNum < accuCmdNumForCalculate:
                sumedCmdNum += 1
                avgForLastCmds = timeInLastCmds / sumedCmdNum
                self.lblTimeToFinish['text'] = '预计剩余时间：00:00:00'
            else:
                timeInLastCmds = timeInLastCmds - avgForLastCmds #扣除平均值（近似前第501个数据）
                avgForLastCmds = timeInLastCmds / accuCmdNumForCalculate
                timeToFinish = avgForLastCmds * remainedCmd
                
                #毫秒转换为 ‘小时:分钟:秒’ 格式
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
            #懒了，直接跨类写属性
            try:
                self.simulator.xBacklash = int(self.txtXBacklashVar.get())
                self.simulator.yBacklash = int(self.txtYBacklashVar.get())
                self.simulator.xStepsPerCm = int(self.txtXStepsPerCmVar.get())
                self.simulator.yStepsPerCm = int(self.txtYStepsPerCmVar.get())
            except:
                showinfo('出错啦', '控制板参数配置错误，请确认回差值等参数是否配置正确。')
                return False
                
            self.simulator.mainloop()
        
        return True
    
    #判断模拟器是否有效
    def hasSimulator(self):
        try:
            state = self.simulator.state()
        except:
            return False
        else:
            self.simulatorWidth = self.simulator.simulatorWidth() #取巧的数据同步而已
            return True
            
#一个CNC对象类，将控制板V1的部分功能转移到上位机中实现，包括单位转换和软件回差处理
class CncMachine:
    def __init__(self, app):
        self.app = app
        self.xPrevPos = 0
        self.yPrevPos = 0
        self.zPrevPos = '1' # 1:下降， 2: 上升
        self.xBacklash = 0
        self.yBacklash = 0
        self.xPrevMoveLeft = True
        self.yPrevMoveUp = True
        self.xStepsPerCm = 0
        self.yStepsPerCm = 0
        self.zLiftSteps = 0
    
    #从配置文件中恢复配置
    def RestoreConfig(self, config):
        app = self.app
        try:
            app.txtXSpeedVar.set(config.get('Machine', 'XAxisSpeed'))
        except:
            pass
        try:
            app.txtXMaxSpeedVar.set(config.get('Machine', 'XAxisMaxSpeed'))
        except:
            pass
        try:
            app.txtYSpeedVar.set(config.get('Machine', 'YAxisSpeed'))
        except:
            pass
        try:
            app.txtYMaxSpeedVar.set(config.get('Machine', 'YAxisMaxSpeed'))
        except:
            pass
        try:
            app.txtZSpeedVar.set(config.get('Machine', 'ZAxisSpeed'))
        except:
            pass
        try:
            app.txtAccelerationVar.set(config.get('Machine', 'SpeedAcceleration'))
        except:
            pass
        try:
            app.txtXStepsPerCmVar.set(config.get('Machine', 'XStepsPerCm'))
        except:
            pass
        try:
            app.txtXBacklashVar.set(config.get('Machine', 'XBacklash'))
        except:
            pass
        try:
            app.txtYStepsPerCmVar.set(config.get('Machine', 'YStepsPerCm'))
        except:
            pass
        try:
            app.txtYBacklashVar.set(config.get('Machine', 'YBacklash'))
        except:
            pass
        try:
            app.txtZLiftStepsVar.set(config.get('Main', 'ZLiftSteps'))
        except:
            pass
        try:
            app.txtPenWidthVar.set(config.get('Main', 'PenDiameter'))
        except:
            pass
            
    #将配置保存到配置文件
    def SaveConfig(self, config):
        app = self.app
        config.add_section('Machine')
        config.set('Machine', 'XAxisSpeed', app.txtXSpeedVar.get())
        config.set('Machine', 'XAxisMaxSpeed', app.txtXMaxSpeedVar.get())
        config.set('Machine', 'YAxisSpeed', app.txtYSpeedVar.get())
        config.set('Machine', 'YAxisMaxSpeed', app.txtYMaxSpeedVar.get())
        config.set('Machine', 'ZAxisSpeed', app.txtZSpeedVar.get())
        config.set('Machine', 'SpeedAcceleration', app.txtAccelerationVar.get())
        config.set('Machine', 'XStepsPerCm', app.txtXStepsPerCmVar.get())
        config.set('Machine', 'XBacklash', app.txtXBacklashVar.get())
        config.set('Machine', 'YStepsPerCm', app.txtYStepsPerCmVar.get())
        config.set('Machine', 'YBacklash', app.txtYBacklashVar.get())
        config.set('Machine', 'ZLiftSteps', app.txtZLiftStepsVar.get())
        config.set('Machine', 'PenDiameter', app.txtPenWidthVar.get())
    
    #将当前位置当做原点
    def Reset(self, x=False, y=False, z=False):
        if x:
            self.xPrevPos = 0
        if y:
            self.yPrevPos = 0
        if z:
            self.zPrevPos = '1'
    
    #将GUI界面上的参数更新到对象属性中，方便后续处理
    def UpdateProperties(self):
        app = self.app
        try:
            self.xBacklash = int(app.txtXBacklashVar.get())
            self.yBacklash = int(app.txtYBacklashVar.get())
            self.xStepsPerCm = int(app.txtXStepsPerCmVar.get())
            self.yStepsPerCm = int(app.txtYStepsPerCmVar.get())
            self.zLiftSteps = int(app.txtZLiftStepsVar.get())
        except:
            return False
        else:
            return True
    
    #返回Z抬起的命令
    def LiftZCmd(self):
        if self.zPrevPos == '1':
            self.zPrevPos = '2'
            return 'z-%05d' % self.zLiftSteps
        else:
            return ''
    
    def DownZCmd(self):
        if self.zPrevPos == '2':
            self.zPrevPos = '1'
            return 'z+%05d' % self.zLiftSteps
        else:
            return ''
        
    #将主应用程序生成的绝对微米坐标转换为雕刻机认识的按步进运行的命令
    #返回是一个命令列表
    def TranslateCmd(self, x, y, z):
        res = []
        
        if z == '1' and self.zPrevPos == '2':
            res.append(self.DownZCmd())
        elif z == '2' and self.zPrevPos == '1':
            res.append(self.LiftZCmd())
        
        if x != self.xPrevPos:
            #微米转换为步数
            steps = round(abs(x - self.xPrevPos) * self.xStepsPerCm / 10000)
            if x < self.xPrevPos: #左移
                #消回差
                if not self.xPrevMoveLeft: #前一个动作为右移，现在左移，需要做回差补偿
                    steps += self.xBacklash
                if steps > 0:
                    res.append('x-%05d' % steps)
                self.xPrevMoveLeft = True
            else:
                if self.xPrevMoveLeft: #前一个动作为左移，现在右移，需要做回差补偿
                    steps += self.xBacklash
                if steps > 0:
                    res.append('x+%05d' % steps)
                self.xPrevMoveLeft = False
            self.xPrevPos = x
        
        if y != self.yPrevPos:
            #微米转换为步数
            steps = round(abs(y - self.yPrevPos) * self.yStepsPerCm / 10000)
            if y < self.yPrevPos: #上移
                if not self.yPrevMoveUp:
                    steps += self.yBacklash
                if steps > 0:
                    res.append('y-%05d' % steps)
                self.yPrevMoveUp = True
            else:
                if self.yPrevMoveUp:
                    steps += self.yBacklash
                if steps > 0:
                    res.append('y+%05d' % steps)
                self.yPrevMoveUp = False
            self.yPrevPos = y
            
        return res
        
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
    def GenAperture(cls, line, unit, forceHole, minHole):
        minHole *= 1000 #转换为微米
        
        #Aperture定义的正则表达式
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
                if len(mods) > 2: #外圆内方
                    inst.innerEdge2 = mods[2]
                if len(mods) > 1: #开圆孔或方孔
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
            
            #强制开孔，仅针对没有孔的，或小圆孔的，如果本来是方孔则不管
            if inst.innerEdge1 > 0.0 and inst.innerEdge2 == 0.0 and inst.innerEdge1 < minHole:
                inst.innerEdge1 = minHole
            if forceHole and inst.innerEdge1 == 0.0: #强制开孔
                inst.innerEdge1 = minHole
            
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
        if innerRadius > radius:
            innerRadius = radius
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
            
            if radius == innerRadius:
                break
            radius -= radiusStep
            if radius < innerRadius:
                radius = innerRadius
            
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
        
        #优化小尺寸焊盘
        if self.outerEdge1 <= penWidth and self.outerEdge2 <= penWidth:
            return [(x,y,x,y)] #太小了，打一个点即可
        elif self.outerEdge1 <= penWidth:
            return [(x, yEdgeTop, x, yEdgeBottom)] #画一个竖线代替
        elif self.outerEdge2 <= penWidth:
            return [(xEdgeLeft, y, xEdgeRight, y)] #画一个横线代替
            
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
                deltaX = math.sqrt(math.pow(r, 2) - math.pow(abs(y - yFill), 2))
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
    def RenderObround(self, x, y, penWidth):
        if self.outerEdge1 == self.outerEdge2:
            return self.RenderCircle(x, y, penWidth)
        elif self.outerEdge1 > self.outerEdge2: #横的长条
            return self.RenderObroundHorizontal(x, y, penWidth)
        else: #竖的长条
            return self.RenderObroundVertical(x, y, penWidth)
            
    #在特定点上画一个多边形（可能为实心，或空心）
    #根据x,y,penWidth生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #x,y:要画多边形的坐标（微米）
    #penWidth：笔尖宽度（微米）
    def RenderPolygon(self, x, y, penWidth):
        if self.outerEdge1 <= penWidth:
            return [(x,y,x,y)] #太小则打一个点即可
            
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
    
    #在特定点上画一个水平的矩形椭圆（可能为实心，或空心）
    #根据x,y,penWidth生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #x,y:要画矩形椭圆的坐标（微米）
    #penWidth：笔尖宽度（微米）
    def RenderObroundHorizontal(self, x, y, penWidth):
        penHalf = penWidth / 2
        fillStep = penWidth * 2 / 3
        radius = self.outerEdge2 / 2 - penHalf
        xLeft = x - self.outerEdge1 / 2
        xRight = x + self.outerEdge1 / 2
        yTop = y - radius
        yBottom = y + radius
        alphaStep = ANGLE_PER_SIDE
        alphaStart = 0.0 #定义垂直向上为0度，顺时针增加
        
        #优化小尺寸焊盘
        if self.outerEdge2 <= penWidth:
            return [(xLeft, y, xRight, y)]
        
        #先画一个外框
        res = [(xLeft, yTop, xRight, yTop),]
        
        #右半圆
        tmpPrevX = xRight
        tmpPrevY = yTop        
        if radius <= penHalf: #半径太小了，则仅在端点点一个点即可
            res.append((xRight, y, xRight, y))
        else:
            alpha = alphaStart
            while alpha <= math.pi:
                deltaX = radius * math.sin(alpha)
                deltaY = radius * math.cos(alpha)
                currX = xRight + deltaX
                currY = y - deltaY
                res.append((tmpPrevX, tmpPrevY, currX, currY))
                tmpPrevX = currX
                tmpPrevY = currY
                alpha += alphaStep
            res.append((tmpPrevX, tmpPrevY, xRight, yBottom)) #封口
        
        res.append((xRight, yBottom, xLeft, yBottom)) #第二根线
        
        #左半圆
        if radius <= penHalf: #半径太小了，则仅在端点点一个点即可
            res.append((xLeft, y, xLeft, y))
        else:
            tmpPrevX = xLeft
            tmpPrevY = yBottom
            while alpha <= math.pi * 2:
                deltaX = radius * math.sin(alpha)
                deltaY = radius * math.cos(alpha)
                currX = xLeft + deltaX
                currY = y - deltaY
                res.append((tmpPrevX, tmpPrevY, currX, currY))
                tmpPrevX = currX
                tmpPrevY = currY
                alpha += alphaStep
            res.append((tmpPrevX, tmpPrevY, xLeft, yTop))
        
        if radius <= penHalf: #半径太小则无法填充内部
            return res
        
        #填充
        yFill = yTop + fillStep
        while yFill < yBottom:
            deltaY = y - yFill
            cosDeltaY = deltaY / radius
            alpha = math.acos(cosDeltaY if cosDeltaY > -1.0 else -1.0) #避免浮点计算误差
            deltaX = radius * math.sin(alpha)
            xFillLeft = xLeft - deltaX
            xFillRight = xRight + deltaX
            
            if self.innerEdge1 == 0.0: #实心
                res.append((xFillLeft, yFill, xFillRight, yFill))
            elif self.innerEdge2 == 0.0: #圆孔
                #上半部或下半部
                if ((yFill < y - self.innerEdge1 / 2 - penHalf) 
                    or (yFill > y + self.innerEdge1 / 2 + penHalf)):
                    res.append((xFillLeft, yFill, xFillRight, yFill))
                else: #中间分成左右两部分
                    r = self.innerEdge1 / 2 + penHalf
                    deltaX = math.sqrt(math.pow(r, 2) - math.pow(abs(y - yFill), 2))
                    res.append((xFillLeft, yFill, x - deltaX, yFill))
                    res.append((x + deltaX, yFill, xFillRight, yFill))                
            else: #方孔
                #上半部或下半部
                if ((yFill < y - self.innerEdge2 / 2 - penHalf) 
                    or (yFill > y + self.innerEdge2 / 2 + penHalf)):
                    res.append((xFillLeft, yFill, xFillRight, yFill))
                else: #中间分成左右两部分
                    deltaX = self.innerEdge1 / 2 + penHalf
                    res.append((xFillLeft, yFill, x - deltaX, yFill))
                    res.append((x + deltaX, yFill, xFillRight, yFill))
            yFill += fillStep
            
        return res
    
    #在特定点上画一个垂直的矩形椭圆（可能为实心，或空心）
    #根据x,y,penWidth生成[(x1,y1,x2,y2),(x1',y1',x2',y2'),...]画线序列
    #x,y:要画矩形椭圆的坐标（微米）
    #penWidth：笔尖宽度（微米）
    def RenderObroundVertical(self, x, y, penWidth):
        penHalf = penWidth / 2
        fillStep = penWidth * 2 / 3
        radius = self.outerEdge1 / 2 - penHalf
        xLeft = x - radius
        xRight = x + radius
        yTop = y - self.outerEdge2 / 2
        yBottom = y + self.outerEdge2 / 2
        alphaStep = ANGLE_PER_SIDE
        alphaStart = 0.0 #定义水平向左为0度，逆时针增加
        
        #优化小尺寸焊盘
        if self.outerEdge1 <= penWidth:
            return [(x, yTop, x, yBottom)]
        
        #先画一个外框
        res = [(xLeft, yTop, xLeft, yBottom),]
        
        #下半圆
        tmpPrevX = xLeft
        tmpPrevY = yBottom       
        if radius <= penHalf: #半径太小了，则仅在端点点一个点即可
            res.append((x, yBottom, x, yBottom))
        else:
            alpha = alphaStart
            while alpha <= math.pi:
                deltaX = radius * math.cos(alpha)
                deltaY = radius * math.sin(alpha)
                currX = x - deltaX
                currY = yBottom + deltaY
                res.append((tmpPrevX, tmpPrevY, currX, currY))
                tmpPrevX = currX
                tmpPrevY = currY
                alpha += alphaStep
            res.append((tmpPrevX, tmpPrevY, xRight, yBottom)) #封口
        
        res.append((xRight, yBottom, xRight, yTop)) #第二根线
        
        #左半圆
        if radius <= penHalf: #半径太小了，则仅在端点点一个点即可
            res.append((x, yTop, x, yTop))
        else:
            tmpPrevX = xRight
            tmpPrevY = yTop
            while alpha <= math.pi * 2:
                deltaX = radius * math.cos(alpha)
                deltaY = radius * math.sin(alpha)
                currX = x - deltaX
                currY = yTop + deltaY
                res.append((tmpPrevX, tmpPrevY, currX, currY))
                tmpPrevX = currX
                tmpPrevY = currY
                alpha += alphaStep
            res.append((tmpPrevX, tmpPrevY, xLeft, yTop))
        
        if radius <= penHalf: #半径太小则无法填充内部
            return res
        
        #填充
        xFill = xLeft + fillStep
        while xFill < xRight:
            deltaX = x - xFill
            cosDeltaX = deltaX / radius
            alpha = math.acos(cosDeltaX if cosDeltaX > -1.0 else -1.0) #避免浮点计算误差
            deltaY = radius * math.sin(alpha)
            yFillTop = yTop - deltaY
            yFillBottom = yBottom + deltaY
            
            if self.innerEdge1 == 0.0: #实心
                res.append((xFill, yFillTop, xFill, yFillBottom))
            elif self.innerEdge2 == 0.0: #圆孔
                #左半部或右半部
                if ((xFill < x - self.innerEdge1 / 2 - penHalf) 
                    or (xFill > x + self.innerEdge1 / 2 + penHalf)):
                    res.append((xFill, yFillTop, xFill, yFillBottom))
                else: #中间分成上下两部分
                    r = self.innerEdge1 / 2 + penHalf
                    deltaY = math.sqrt(math.pow(r, 2) - math.pow(abs(x - xFill), 2))
                    res.append((xFill, yFillTop, xFill, y - deltaY))
                    res.append((xFill, y + deltaY, xFill, yFillBottom))                
            else: #方孔
                #上半部或下半部
                if ((xFill < x - self.innerEdge2 / 2 - penHalf) 
                    or (xFill > x + self.innerEdge2 / 2 + penHalf)):
                    res.append((xFill, yFillTop, xFill, yFillBottom))
                else: #中间分成上下两部分
                    deltaY = self.innerEdge1 / 2 + penHalf
                    res.append((xFill, yFillTop, xFill, y - deltaY))
                    res.append((xFill, y + deltaY, xFill, yFillBottom))
            xFill += fillStep
            
        return res

#计算两个点的距离
def DistanceDotToDot(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
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

