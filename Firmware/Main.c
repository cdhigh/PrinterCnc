/*The MIT License (MIT)

Copyright (c) 2014 Leonardo Ciocari

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.*/

//COMMAND EXAMPLES (With CNC at reset position "x00000y00000z1"):
//x000147y000147z1 - Invalid, can't move X and Y axis with Z down
//x000147y000147z2 - Valid, can move X and Y axis with Z up (will move X first, then Y)
//x000147y000000z1 - Valid, can move X to 00147 from actual 00000 position
//x000000y000294z1 - Valid, can move Y to 00294 from actual 00000 position


//#include <htc.h>
#include <string.h>
#include <stdlib.h>

#include "defineports.h"

__CONFIG(INTIO & WDTDIS & MCLRDIS & BORDIS & LVPDIS);

#define SERIAL_TIMEOUT 65530

unsigned int xStepDelay = 100; //X轴脉冲中的间隔时间
unsigned int yStepDelay = 120; //Y轴脉冲中的间隔时间
unsigned int zStepDelay = 80; //Z轴脉冲中的间隔时间，Z轴是软驱电机，启动频率不能太高
unsigned int xMinStepDelay = 50; //电机性能不好，速度无法提高，特使用一个加速过程
unsigned int yMinStepDelay = 60; //电机性能不好，速度无法提高，特使用一个加速过程
unsigned int stepDelayCnt = 100; //每隔多少步后开始升速，设置为0则为固定值


//延时函数，一个循环刚好10个指令，在最后加上函数调用的花销7个指令即可。
//假定4m晶体，则：
//延时0.5ms可以用：delayit(50)
//延时1ms可以用：delayit(100)
//延时10ms可以用：delayit(1000)
void delayit(unsigned int d)
{
    while(--d){;}
}

//直接移动多少步，moveLeft=1为向左，=0为向右
void Xmove(unsigned int steps, unsigned char moveLeft)
{
    unsigned int n;
    unsigned int delayNum;
    unsigned char runnedStep;
    
    if (steps == 0)
        return;
    
    if (moveLeft)
        X_DIR = 1;
    else
        X_DIR = 0;
    
    delayNum = xStepDelay; //兼顾不丢步和速度考虑，使用一个加速过程
    runnedStep = 0;
    for (n = steps; n > 0; n--)
    {
        if ((moveLeft && (X_STOP_SW_LEFT == 0)) 
            || (!moveLeft && (X_STOP_SW_RIGHT == 0)))
            break;
        
        X_STEP = 1; //上升沿启动
        delayit(delayNum);
        X_STEP = 0;
        delayit(delayNum);
        if ((stepDelayCnt > 0) && (++runnedStep >= stepDelayCnt)) //每隔一定的步数提升一次速度
        {
            runnedStep = 0;
            if (delayNum > xMinStepDelay)
                delayNum--;
        }
    }
}

//直接移动多少步，moveUp=1为向上，=0为向下
//y轴电机齿轮组基本上没有回差，不需要补偿
void Ymove(unsigned int steps, unsigned char moveUp)
{
    unsigned int n;
    unsigned int delayNum;
    unsigned char runnedStep;
    
    if (steps == 0)
        return;
    
    if (moveUp)
        Y_DIR = 0;
    else
        Y_DIR = 1;
        
    delayNum = yStepDelay; //兼顾不丢步和速度考虑，使用一个加速过程
    runnedStep = 0;
    for (n = steps; n > 0; n--)
    {
        if ((moveUp && (Y_STOP_SW_TOP == 0))
            || (!moveUp && (Y_STOP_SW_BOTTOM == 0)))
            break;
            
        Y_STEP = 1; //上升沿启动
        delayit(delayNum);
        Y_STEP = 0;
        delayit(delayNum);
        if ((stepDelayCnt > 0) && (++runnedStep >= stepDelayCnt)) //每隔一定的步数提升一次速度
        {
            runnedStep = 0;
            if (delayNum > yMinStepDelay)
                delayNum--;
        }
    }
}

//直接移动多少步，moveUp=1为向上，=0为向下
void Zmove(unsigned int steps, unsigned char moveUp)
{
    unsigned int n;
    
    if (moveUp)
        Z_DIR = 0;
    else
        Z_DIR = 1;
    
    for (n = steps; n > 0; n--)
    {
        if ((moveUp && (Z_STOP_SW_TOP == 0))
            || (!moveUp && (Z_STOP_SW_BOTTOM == 0)))
            break;
        
        Z_STEP = 1; //上升沿启动
        delayit(zStepDelay);
        Z_STEP = 0;
        delayit(zStepDelay);
    }
}

//从串口取一个字符，超时则返回0
unsigned char ReceiveOneChar()
{
    volatile unsigned int cnt = SERIAL_TIMEOUT;
    while ((RCIF != 1) && (cnt > 0))
    {
        cnt--;
    }
    
    return RCIF == 1 ? RCREG : '\0';
}

//通过串口向外发送一个字符
void SendOneChar(unsigned char ch)
{
    volatile unsigned int cnt = SERIAL_TIMEOUT;
    while ((TXIF != 1) && (cnt > 0))
    {
        cnt--;
    }
    
    if (TXIF == 1)
        TXREG = ch;
}

//获取串口命令，执行后返回回复字符
unsigned char ScanUart()
{
    unsigned char data[6], tmp, dir;
    unsigned int steps;
    
    tmp = ReceiveOneChar();
    
    //格式：x+00000, y+00000, z+00000
    if ((tmp == 'x') || (tmp == 'y') || (tmp == 'z'))
    {
        dir = ReceiveOneChar(); // + or -
        if (dir == '+')
            dir = 0;
        else if (dir == '-')
            dir = 1;
        else
            return '#';
            
        data[0] = ReceiveOneChar();
        data[1] = ReceiveOneChar();
        data[2] = ReceiveOneChar();
        data[3] = ReceiveOneChar();
        data[4] = ReceiveOneChar();
        data[5] = '\0';
        
        if ((data[0] == '\0') || (data[1] == '\0') || (data[2] == '\0')
            || (data[3] == '\0') || (data[4] == '\0'))
            return '#';
            
        steps = atoi(data);
        
        if (tmp == 'x')
            Xmove(steps, dir);
        else if (tmp == 'y')
            Ymove(steps, dir);
        else
            Zmove(steps, dir);
    }
    else if (tmp == 'X') //设置X轴步进脉冲初始延时时间和结束延时时间,XS000,XE000
    {
        tmp = ReceiveOneChar();
        if ((tmp != 'S') && (tmp != 'E'))
            return '#';
            
        data[0] = ReceiveOneChar();
        data[1] = ReceiveOneChar();
        data[2] = ReceiveOneChar();
        data[3] = '\0';
        if ((data[0] == '\0') || (data[1] == '\0') || (data[2] == '\0'))
            return '#';
            
        if (tmp == 'S')
            xStepDelay = atoi(data);
        else
            xMinStepDelay = atoi(data);
    }
    else if (tmp == 'Y') //设置Y轴步进脉冲延时时间,YS000, YE000
    {
        tmp = ReceiveOneChar();
        if ((tmp != 'S') && (tmp != 'E'))
            return '#';
            
        data[0] = ReceiveOneChar();
        data[1] = ReceiveOneChar();
        data[2] = ReceiveOneChar();
        data[3] = '\0';
        if ((data[0] == '\0') || (data[1] == '\0') || (data[2] == '\0'))
            return '#';
            
        if (tmp == 'S')
            yStepDelay = atoi(data);
        else
            yMinStepDelay = atoi(data);
    }
    else if (tmp == 'Z') //设置Z轴步进脉冲延时时间，Z000
    {
        data[0] = ReceiveOneChar();
        data[1] = ReceiveOneChar();
        data[2] = ReceiveOneChar();
        data[3] = '\0';
        if ((data[0] == '\0') || (data[1] == '\0') || (data[2] == '\0'))
            return '#';
            
        zStepDelay = atoi(data);
    }
    else if (tmp == 'A') //设置升速的加速度, A0000 
    {
        data[0] = ReceiveOneChar();
        data[1] = ReceiveOneChar();
        data[2] = ReceiveOneChar();
        data[3] = ReceiveOneChar();
        data[4] = '\0';
        if ((data[0] == '\0') || (data[1] == '\0') || (data[2] == '\0') || (data[3] == '\0'))
            return '#';
            
        stepDelayCnt = atoi(data);
    }
    else
    {
        return '\0'; //不支持的命令，不返回答复
    }
    
    return '*';
}


//---------------------------------------------------
void main()
{
    unsigned char n, res;

    TRISA = 0b00111100;
    PORTA = 0;

    //PORTB
    TRISB = 0b00001011;
    PORTB = 0;
    
    //Turn off analog comparator
    CM2 = 1;
    CM1 = 1;
    CM0 = 1;
    //CMCON = 0b00000111;

    //USART
    BRGH = 1;	//高速波特率模式
    SPBRG = 25;	//9600 at 4Mhz
    SYNC = 0;
    SPEN = 1;	//USART enabled
    TXEN = 1;
    CREN = 1;
    
    //Wait 1 second (circuit stabilization)
    for (n = 10; n > 0; n--)
        delayit(10000);
    
    while (1)
    {
        if (OERR)	//避免阻塞，串口溢出后复位串口
        {
            CREN = 0;
            CREN = 1;
        }
        
        if (RCIF)	//有串口消息到来，处理串口消息
        {
            res = ScanUart();
            if (res != '\0')
            {
                SendOneChar(res); //返回答复消息 
            }
        }
    }
}

