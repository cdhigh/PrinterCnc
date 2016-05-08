#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""命令排序，为了减少雕刻笔移动距离，提高雕刻速度"""
#import math

#计算两个点的距离（为了速度考虑，实际返回的是距离的平方）
cdef inline float DistanceDotToDot(float x1, float y1, float x2, float y2):
    #return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    #return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)
    return abs(x1 - x2) + abs(y1 - y2)
    
cpdef object SortCommands(list commands):
    #将坐标点转换为线条列表
    cdef list lines, newLines
    cdef tuple line1
    cdef float lastX = 0.0
    cdef float lastY = 0.0
    cdef float x1, y1, x2, y2
    cdef float minDis, dis
    cdef int minIdx, idx
    cdef str z
    
    lines = []
    for line1 in commands: #这里z只有1、2
        x1 = line1[0]
        y1 = line1[1]
        z = line1[2]
        if z == "1":
            lines.append((lastX, lastY, x1, y1))
        lastX = x1
        lastY = y1
    
    if not lines:
        return None
        
    #找出离原点最近的一根线
    line1 = lines[0]
    minDis = DistanceDotToDot(line1[0], line1[1], 0.0, 0.0)
    minIdx = 0
    for idx, (x1,y1,x2,y2) in enumerate(lines):
        dis = DistanceDotToDot(x1, y1, 0.0, 0.0)
        if dis < minDis:
            minDis = dis
            minIdx = idx
    
    #从第一根线起，一直寻找离前一根线终点最近的另一根线
    newLines = []
    while lines:
        line1 = lines.pop(minIdx)
        newLines.append(line1)
        
        if not lines:
            break
            
        minIdx = 0
        lastX = line1[2]
        lastY = line1[3]
        x1, y1, x2, y2 = lines[0]
        minDis = DistanceDotToDot(x1, y1, lastX, lastY)
        for idx, (x1,y1,x2,y2) in enumerate(lines):
            #if (abs(x1 - lastX) <= minDis) and (abs(y1 - lastY) <= minDis):
            dis = DistanceDotToDot(x1, y1, lastX, lastY)
            if dis < minDis:
                minDis = dis
                minIdx = idx
    
    #将线段重新转换为坐标点列表
    commands[:] = []
    lastX = lastY = 0.0
    for x1, y1, x2, y2 in newLines:
        if x1 != lastX or y1 != lastY:
            commands.append((x1, y1, "2"))
        commands.append((x2, y2, "1"))
        lastX = x2
        lastY = y2
    
    return None
