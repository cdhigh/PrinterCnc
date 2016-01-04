#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
将 sortcommands.pyx 通过cython编译为 sortcommands.pyd
在同一个目录下执行命令即可：
python.exe pyxsetup.py build_ext --inplace
"""

from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = 'SortCommands',
    ext_modules = cythonize("*.pyx")
)
