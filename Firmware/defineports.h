/* Define bits 
Author: cdhigh
*/

#ifndef __DEFINE_PORTS__
#define __DEFINE_PORTS__

#include <pic.h>

//Z Axis - STEPPER MOTOR
#define Z_DIR   RA1 //1 - down, 0 - up
#define Z_STEP  RA0 //rising edge to take step

//X Axis - STEPPER Motor
#define X_DIR   RB7 //1 - left, 0 - right
#define X_STEP  RB6 //rising edge to take step

//Y Axis - STEPPER MOTOR
#define Y_DIR   RA7 //0 - up, 1 - down
#define Y_STEP  RA6 //rising edge to take step

//限位开关，低有效
#define X_STOP_SW_LEFT    RB3
#define X_STOP_SW_RIGHT   RB0
#define Y_STOP_SW_TOP     RA5
#define Y_STOP_SW_BOTTOM  RA4
#define Z_STOP_SW_TOP     RA3
#define Z_STOP_SW_BOTTOM  RA2


#endif
