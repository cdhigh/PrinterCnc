#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""废喷墨打印机改装的大行程数控雕刻机的PC控制端程序，
使用cxFreeze打包成EXE文件
请执行：python.exe bind_cxfreeze.py build 然后在build目录中生成exe文件
Author: cdhigh
"""

import sys
import os
from cx_Freeze import setup, Executable

if sys.platform == "win32":
    base = "Win32GUI"
else:
    base = None

tclPath = os.path.normpath(os.path.join(os.path.dirname(os.__file__), '../tcl/tcl8.6'))

build_exe_options = {'optimize' : 2,
                     'include_files' : [(tclPath,'tcl'),],}

exe = Executable(
    script = 'CncController.py',
    initScript = None,
    base = 'Win32GUI',
    targetName = 'CncController.exe',
    compress = True,
    appendScriptToExe = True,
    appendScriptToLibrary = True,
)

setup( name = 'CncController', 
        version = '0.1',
        description = 'CncController',
        options = {'build_exe': build_exe_options},
        executables = [Executable('CncController.py', base = base,
            icon='app_icon.ico', )])