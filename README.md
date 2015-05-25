# PrinterCnc
这个项目源于 [https://themrleon/OpenCdNC](https://themrleon/OpenCdNC)，只是因为光驱行程太小，不好玩，我没有兴趣采用光驱制作，为此，使用了一个废打印机框架和扫描仪组件改成了一个超低成本的大行程雕刻机。
[详细制作过程请参考此论坛文章](http://bbs.mydigit.cn/read.php?tid=1249614)

![正面](https://raw.githubusercontent.com/cdhigh/PrinterCnc/master/Photos/%E6%95%B4%E6%9C%BA%E6%AD%A3%E9%9D%A2.JPG)
![打印效果](https://raw.githubusercontent.com/cdhigh/PrinterCnc/master/Photos/%E6%89%93%E5%8D%B0%E9%BE%99%E5%AD%97.JPG)
![上位机](https://raw.githubusercontent.com/cdhigh/PrinterCnc/master/Photos/%E4%B8%8A%E4%BD%8D%E6%9C%BA.JPG)

# 特性
* 可以先参考 [https://themrleon/OpenCdNC](https://themrleon/OpenCdNC)

* 我的固件和原项目的固件差别很大，我增加了很多扩展命令，并支持软件消回差，省掉硬件消回差的麻烦。

* 我这个项目最大的特点就是行程大，实际行程超过一张A4纸。

* 另一个特点就是我写的上位机，带GUI界面，功能比较全面，能解析常用的Gerber指令代码，基本上覆盖业余DIY制作PCB的常用指令，故可以直接在各种PCB软件中直接设计PCB，然后导出RS274X\_GERBER文件即可直接使用，不需要像原项目一样先导出为图像然后再导入（用打印图像的方式打印PCB会丧失一些精度，而且也不方便）。

* 我的上位机还带了一个简单的模拟器，可以在下发到控制板之前先看看效果和排版位置什么的。为了仿真，模拟器和控制板原理都是一样的，都是用海量的水平线和垂直线组合出任意图案。也是因为此原理，所以此模拟器很慢，不过有时候还是有用的，看你的需要了。

* 当然了，也不是没有缺点，因为碍于小步进电机的性能，速度无法调的很快，调的快就容易丢步或啸叫，画图时可以调快一点，画PCB时建议调慢一点，可以得到更好的精度。

# 材料清单
### 硬件 (github仓库中有接线图安装图等资料)
* 1个 Microchip PIC16F628A（这个项目不需要外部晶振）
* 3个 Easy Driver v4.4 Step Motor Driver
* 如果是笔记本电脑，还需要一个USB转串口适配器
* 一个打印机底座、墨车、导轨
* 一个打印机扫描仪一体机的扫描仪组件
* 一个扫描仪组件的步进电机和齿轮组
* 一块密度板做底座

### 软件
* Microchip MPlab X
* Cadsoft Eagle PCB
* Microsoft Paint
* Python and pyserial

# 协议和工作细节
## 协议
* 真正的绘图命令其实就一条"x000000y000000z1" <br />
* X轴和Y轴坐标的单位为微米，Z轴=1为绘图笔下降，=2为绘图笔上升。
* 只能画水平线或垂直线。
* 除了绘图命令外，还有一些调试或定位命令，请参考 [cmdlist](https://github.com/cdhigh/PrinterCnc/blob/master/Firmware/cmdlist.md)

（原项目的xy坐标为5位数字，我的项目行程加大了，5位不够，特扩展为6位。）

## 上位机
* 从上面对协议的描述你可以看到，控制板很弱，此雕刻机的功能真正的实现大部分都在上位机上，上位机强则雕刻机强，上位机弱则雕刻机弱。
* 目前的上位机由Python写成，方便、跨平台，可以解析和翻译Gerber文件的大部分指令并通过串口发送给控制板。
* 如果你的系统是windows，可以使用cxfreeze预绑定的windows可执行文件，否则建议安装python(2.x/3.x均可)和pyserial包，则可以直接执行CncController.py文件打开上位机。

## Eagle
Eagle为PCB设计软件，其可以输出Gerber RS274X文件，可以导入位图文件到Eagle然后导出Gerber，或直接在Eagle中排版绘图，然后输出Gerber文件。</div>

## 如何打印位图
如果你要打印位图，可以参考原项目的Tutorial，这里简单说明如下：
1. 第一步转换位图为单色位图
2. 然后运行此项目所附的“import_bmp_as_wire.ulp”
3. 导入图像到Eagle后选择“文件”|“CAM处理器”，导出为GERBER_RS274X格式
4. 使用上位机打开gerber文件进行打印

## License
[MIT LICENSE](https://github.com/themrleon/OpenCdNC/blob/master/LICENSE)
