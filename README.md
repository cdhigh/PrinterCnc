# PrinterCnc
<div align="justify">这个项目源于(https://themrleon/OpenCdNC)，只是因为光驱行程太小，不好玩，我没有兴趣采用光驱制作，为此，使用了一个废打印机框架和扫描仪组件改成了一个超低成本的大行程雕刻机。</div>

## 特性
* 请参考(https://themrleon/OpenCdNC)
* 除此之外，我这个项目最大的特点就是行程大，实际行程超过一张A4纸。
* 原项目的上位机为C++写的命令行程序，而且仅支持RS274X-24格式，我使用python改进了其上位机，增加GUI界面，方便控制雕刻机，并支持其他格式的RS274X文件，适应面更广，也同时支持了在雕刻机上画斜线和焊盘功能，基本上可以直接在各种软件中直接排版PCB，然后输出为gerber文件则可以为上位机支持。

## 材料清单
### 硬件
* 1x Microchip PIC16F628A（连晶振都不需要）
* 3x Easy Driver v4.4 Step Motor Driver
* 如果是笔记本电脑，还需要一个USB转串口适配器
* 一个打印机底座、墨车、导轨
* 一个打印机扫描仪一体机的扫描仪组件
* 一个扫描仪组件的步进电机和齿轮组
* 一块密度板做底座

### 软件
* Microsoft Windows 7
* Microchip MPlab X
* Cadsoft Eagle PCB
* Microsoft Paint
* Python and pyserial

## 协议和工作细节
### 协议
真正的绘图命令就一条‘x000000y000000z1` - X轴和Y轴坐标的单位为微米，Z轴 1为绘图笔下降，2为绘图笔上升。(原项目的xy坐标为5位数字，我的项目行程加大了，5位不够，特扩展为6位。)

### 上位机
<div align="justify">上位机由Python写成，用于解析Gerber文件并通过串口发送给控制板。</div>

### Eagle
<div align="justify">Eagle为PCB设计软件，其可以输出Gerber RS274X文件，可以导入位图文件到Eagle然后导出Gerber，或直接在Eagle中排版绘图，然后输出Gerber文件。</div>

## 如何打印位图
<div align="justify">第一步转换位图为单色位图，然后运行此项目所附的“import_bmp_as_wire.ulp”，导入图像到Eagle后选择“文件”|“CAM处理器”，导出为GERBER_RS274X格式即可，细节可以参考原项目。</div>

## License
See [LICENSE](https://github.com/themrleon/OpenCdNC/blob/master/LICENSE)
