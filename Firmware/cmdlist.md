﻿#基本命令：
   x000000y000000z1
   x/y的单位为微米，不支持负数。
   1：下降Z轴，2：上升Z轴

#调试和测试命令（都用@开头）：
   * @reposx  将X轴当前位置当做X原点
   * @reposy  将Y轴当前位置当做Y原点
   * @reposz  将Z轴当前位置当做笔下降位置
   * @reset  ZYZ轴回到最左最上位置（需要限位开关配合）
   * @x+0100 or @x-0100  将x轴单独移动特定的步数，+/-后必须带四位数字
   * @y+0100 or @y-0100  将y轴单独移动特定的步数，+/-后必须带四位数字
   * @z+0010 or @z-0010  将z轴单独移动特定的步数，+/-后必须带四位数字
   * @X0000 设定X轴的移动速度，四位数字越小运动越快
   * @Y0000 设定Y轴的移动速度，四位数字越小运动越快
   * @Z0000 设定Z轴的移动速度，四位数字越小运动越快
   * @B000  设定X轴的回差补偿步数