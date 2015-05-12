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

//#define _XTAL_FREQ 4000000 //使用内置rc振荡器

//Z轴
unsigned char zPrevPos = '1'; //'1' = down, '2' = up

//X轴
unsigned int xPrevPos = 0;	//Start at zero, upper left position
unsigned char xBacklashSteps = X_BACKLASH; //回差补偿步数

//Y轴
unsigned int yPrevPos = 0;	//Start at zero, upper left position

unsigned int xStepDelay = 25; //X轴脉冲中的间隔时间
unsigned int yStepDelay = 25; //Y轴脉冲中的间隔时间
unsigned int zStepDelay = 160; //Z轴脉冲中的间隔时间


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
void XmoveAbsolute(unsigned int steps, unsigned char moveLeft)
{
    unsigned int n;
    
    if (steps == 0)
        return;
    
    if (moveLeft)
    {
        if (X_DIR == 0) //上次向右
        {
            X_DIR = 1;
            for (n = xBacklashSteps; n > 0; n--) //消回差
            {
                if ((X_STOP_SW_LEFT == 0) || (X_STOP_SW_RIGHT == 0))
                    break;
                
                X_STEP = 1; //上升沿启动
                delayit(xStepDelay);
                X_STEP = 0;
                delayit(xStepDelay);
            }
        }
    }
    else
    {
        if (X_DIR == 1) //上次向左
        {
            X_DIR = 0;
            for (n = xBacklashSteps; n > 0; n--) //消回差
            {
                if ((X_STOP_SW_LEFT == 0) || (X_STOP_SW_RIGHT == 0))
                    break;
                
                X_STEP = 1; //上升沿启动
                delayit(xStepDelay);
                X_STEP = 0;
                delayit(xStepDelay);
            }
        }
    }
    
    for (n = steps; n > 0; n--)
    {
        if ((X_STOP_SW_LEFT == 0) || (X_STOP_SW_RIGHT == 0))
            break;

        X_STEP = 1; //上升沿启动
        delayit(xStepDelay);
        X_STEP = 0;
        delayit(xStepDelay);

        if (moveLeft)
            xPrevPos--;
        else
            xPrevPos++;
    }
}

//直接移动多少步，moveUp=1为向上，=0为向下
//y轴电机齿轮组基本上没有回差，不需要补偿
void YmoveAbsolute(unsigned int steps, unsigned char moveUp)
{
    unsigned int n;

    if (moveUp)
        Y_DIR = 0;
    else
        Y_DIR = 1;

    for (n = steps; n > 0; n--)
    {
        if ((Y_STOP_SW_TOP == 0) || (Y_STOP_SW_BOTTOM == 0))
            break;

        Y_STEP = 1; //上升沿启动
        delayit(yStepDelay);
        Y_STEP = 0;
        delayit(yStepDelay);

        if (moveUp)
            yPrevPos--;
        else
            yPrevPos++;
    }
}

//直接移动多少步，moveUp=1为向上，=0为向下
void ZmoveAbsolute(unsigned char steps, unsigned char moveUp)
{
    unsigned char n;

    if (moveUp)
        Z_DIR = 0;
    else
        Z_DIR = 1;

    for (n = steps; n > 0; n--)
    {
        if ((Z_STOP_SW_TOP == 0) || (Z_STOP_SW_BOTTOM == 0))
            break;

        Z_STEP = 1; //上升沿启动
        delayit(zStepDelay);
        Z_STEP = 0;
        delayit(zStepDelay);
    }
}

//移动x轴，pos单位为步数
void Xmove(unsigned int pos)
{
    unsigned int c;
    unsigned char moveLeft;

    if (xPrevPos < pos)
        moveLeft = 0;
    else
        moveLeft = 1;

    //移动的绝对值
    c = abs(pos - xPrevPos);

    XmoveAbsolute(c, moveLeft);
}

//移动y轴，pos单位为步数
void Ymove(unsigned int pos)
{
    unsigned int c;
    unsigned char moveUp;

    if (yPrevPos < pos)
        moveUp = 0;
    else
        moveUp = 1;
        
    c = abs(pos - yPrevPos);
    
    YmoveAbsolute(c, moveUp);
}

//移动Z轴，pos单位为步数
void Zmove(unsigned char pos)
{
    if (zPrevPos != pos)
    {
        if (pos == '1') //down
        {
            ZmoveAbsolute(20, 0);
            zPrevPos = '1';
        }
        else if (pos == '2') //up
        {
            ZmoveAbsolute(20, 1);
            zPrevPos = '2';
        }
    }
}

//将当前位置当做新的原点
void Reset()
{
    xPrevPos = 0;
    yPrevPos = 0;
    zPrevPos = '1';
}

//三轴位置复位，x轴回最左，y轴回最上，z轴回最下
void ResetPosition()
{
    //先升起z轴才移动x和y轴
    while (Z_STOP_SW_TOP)
        ZmoveAbsolute(20, 1);
    while (X_STOP_SW_LEFT)
        XmoveAbsolute(100, 1);
    while (Y_STOP_SW_TOP)
        YmoveAbsolute(100, 1);
    
    while (Z_STOP_SW_BOTTOM)
        ZmoveAbsolute(20, 0);

    Reset();
}

//获取串口命令，执行后返回回复字符
void ScanUart()
{
    unsigned char x[7],y[7],z,tmp, res;
    unsigned int x_pos,y_pos;
    
    tmp = RCREG;
    x[6] = 0;
    y[6] = 0;
    res = '*';
    
    //格式：x000000y000000z1
    if (tmp == 'x')
    {
        //Get X
        while (RCIF != 1); x[0] = RCREG;
        while (RCIF != 1); x[1] = RCREG;
        while (RCIF != 1); x[2] = RCREG;
        while (RCIF != 1); x[3] = RCREG;
        while (RCIF != 1); x[4] = RCREG;
        while (RCIF != 1); x[5] = RCREG;
        
        while (RCIF != 1); tmp = RCREG; //letter 'y'
        
        //Get Y
        while (RCIF != 1); y[0] = RCREG;
        while (RCIF != 1); y[1] = RCREG;
        while (RCIF != 1); y[2] = RCREG;
        while (RCIF != 1); y[3] = RCREG;
        while (RCIF != 1); y[4] = RCREG;
        while (RCIF != 1); y[5] = RCREG;
        
        while (RCIF != 1); tmp = RCREG; //letter 'z'
        
        //Get Z
        while (RCIF != 1); z = RCREG;
        
        Zmove(z);	//Z轴优先移动
        
        //微米转换为步数
        x_pos = atol(x) / (10000 / X_CM);
        y_pos = atol(y) / (10000 / Y_CM);
        
        //仅支持一次单轴移动，水平或垂直
        if ((xPrevPos == x_pos) || (yPrevPos == y_pos))
        {
            if (xPrevPos != x_pos)
                Xmove(x_pos);
            if (yPrevPos != y_pos)
                Ymove(y_pos);
        }
        else if (z == '2') //Z轴抬起的情况下可以移动两轴
        {
            Xmove(x_pos);
            Ymove(y_pos);
        }
        else
            res = '#';
        
        while (TXIF != 1); TXREG = res; //返回答复消息
    }
    else if (tmp == '@') //测试或调试命令
    {
        while (RCIF != 1); tmp = RCREG;
        if (tmp == 'r') //repos[xyz] or reset
        {
            while (RCIF != 1); x[0] = RCREG;
            while (RCIF != 1); x[1] = RCREG;
            while (RCIF != 1); x[2] = RCREG;
            while (RCIF != 1); x[3] = RCREG;
            if ((x[0] == 'e') && (x[1] == 'p') && (x[2] == 'o') && (x[3] == 's'))
            {
                //repos则将当前位置做为原点
                while (RCIF != 1); x[4] = RCREG;
                if (x[4] == 'x')
                    xPrevPos = 0;
                else if (x[4] == 'y')
                    yPrevPos = 0;
                else if (x[4] == 'z')
                    zPrevPos = '1';
            }
            else if ((x[0] == 'e') && (x[1] == 's') && (x[2] == 'e') && (x[3] == 't'))
            {
                ResetPosition();
            }
        }
        else if (tmp == 'x') //按步数来移动x轴，格式：@x+0100 or @x-0010，必须为4位数字
        {
            while (RCIF != 1); tmp = RCREG;
            while (RCIF != 1); x[0] = RCREG;
            while (RCIF != 1); x[1] = RCREG;
            while (RCIF != 1); x[2] = RCREG;
            while (RCIF != 1); x[3] = RCREG;
            x[4] = 0;
            if (tmp == '+')
                tmp = 0;
            else
                tmp = 1;
            XmoveAbsolute(atol(x), tmp);
        }
        else if (tmp == 'y') //按步数来移动y轴, 格式：@y+0100 or @y-0010，必须为4位数字
        {
            while (RCIF != 1); tmp = RCREG;
            while (RCIF != 1); y[0] = RCREG;
            while (RCIF != 1); y[1] = RCREG;
            while (RCIF != 1); y[2] = RCREG;
            while (RCIF != 1); y[3] = RCREG;
            y[4] = 0;
            if (tmp == '+')
                tmp = 0;
            else
                tmp = 1;
            YmoveAbsolute(atol(y), tmp);
        }
        else if (tmp == 'z') //按步数来移动z轴, 格式：@z+0010 or @z-0010，必须为4位数字
        {
            while (RCIF != 1); tmp = RCREG;
            while (RCIF != 1); y[0] = RCREG;
            while (RCIF != 1); y[1] = RCREG;
            while (RCIF != 1); y[2] = RCREG;
            while (RCIF != 1); y[3] = RCREG;
            y[4] = 0;
            if (tmp == '+')
                tmp = 0;
            else
                tmp = 1;
            ZmoveAbsolute(atol(y), tmp);
        }
        else if (tmp == 'X') //设置X轴步进脉冲延时时间,@X0000
        {
            while (RCIF != 1); x[0] = RCREG;
            while (RCIF != 1); x[1] = RCREG;
            while (RCIF != 1); x[2] = RCREG;
            while (RCIF != 1); x[3] = RCREG;
            x[4] = 0;
            xStepDelay = atol(x);
        }
        else if (tmp == 'Y') //设置Y轴步进脉冲延时时间,@Y0000
        {
            while (RCIF != 1); y[0] = RCREG;
            while (RCIF != 1); y[1] = RCREG;
            while (RCIF != 1); y[2] = RCREG;
            while (RCIF != 1); y[3] = RCREG;
            y[4] = 0;
            yStepDelay = atol(y);
        }
        else if (tmp == 'Z') //设置Z轴步进脉冲延时时间，@Z0000
        {
        
            while (RCIF != 1); y[0] = RCREG;
            while (RCIF != 1); y[1] = RCREG;
            while (RCIF != 1); y[2] = RCREG;
            while (RCIF != 1); y[3] = RCREG;
            y[4] = 0;
            zStepDelay = atol(y);
        }
        else if (tmp == 'B') //设置回差补偿步数，@B000
        {
            while (RCIF != 1); x[0] = RCREG;
            while (RCIF != 1); x[1] = RCREG;
            while (RCIF != 1); x[2] = RCREG;
            x[3] = 0;
            xBacklashSteps = atol(x);
        }
        else
        {
            res = '#';
        }
        
        while (TXIF != 1); TXREG = res;
    }
    else //非法命令
    {
        while (TXIF != 1); TXREG = '#';
    }
}


//---------------------------------------------------
void main()
{
    unsigned char n;

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

    Reset();

    while (1)
    {
        if (OERR)	//避免阻塞，串口溢出后复位串口
        {
            CREN = 0;
            CREN = 1;
        }

        if (RCIF)	//有串口消息到来，处理串口消息
            ScanUart();
            
    }
}

