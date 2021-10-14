# Notes
# =====
#
# - create a function that can display items twice as big as normal (i.e. zoom a sprite by pixel doubling)
# - make a function to copy a sprite to a virus playfield
# - use the new pacmaze drawing technique to create sprites
#
# make sure we use setpixel to draw, not .SetPixel.  We need to always update the buffer.

# The buffer is a 2D array.  32 lines of 64 pixels
# BUFFER[V][H]  

# We write to the LED directory for simplicity
# We write to the Canvas and swap to the LED for speed
# We write to the ScreenArray buffer so we know what is on the screen in case we
# need to check it


#------------------------------------------------------------------------------
#   _     _____ ____                          _                              --
#  | |   | ____|  _ \  __ _ _ __ ___ __ _  __| | ___                         --
#  | |   |  _| | | | |/ _` | '__/ __/ _` |/ _` |/ _ \                        --
#  | |___| |___| |_| | (_| | | | (_| (_| | (_| |  __/                        --
#  |_____|_____|____/ \__,_|_|  \___\__,_|\__,_|\___|                        --
#                                                                            --
#                                                                            --
#   This is a collection of classes and functions derived from the           --
#   Arcade Retro Clock RGB project.                                          --
#                                                                            --
#   This project will enable you to display animated text and sprites on     --
#   LED display attached to a Raspberry Pi computer.                         --
#                                                                            --
#                                                                            --
#   Copyright 2021 William McEvoy                                            --
#                                                                            --
#------------------------------------------------------------------------------
#   Version: 1.0                                                             --
#   Date:    October 4, 2020                                                 --
#   Reason:  Initial Creation                                                --
#------------------------------------------------------------------------------


import time
import gc
import random
import os
from configparser import SafeConfigParser
import sys



#RGB Matrix
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions




from datetime import datetime, timedelta
from random import randint
#import argparse
import copy
import numpy
import math
import subprocess
import traceback
import unicornhathd as unicorn



#For capturing keypresses
import curses

#Crypto
from pycoingecko import CoinGeckoAPI


#JSON
import requests
import simplejson as json


#--------------------------------------
# Global Variables                   --
#--------------------------------------

KeyboardSpeed  = 15
ConfigFileName = "ClockConfig.ini"

MainSleep        = 0
FlashSleep       = 0
PacSleep         = 0.01
ScrollSleep      = 0.03
TinyClockStartHH = 0
TinyClockHours   = 0
CPUModifier      = 0
Gamma            = 1
ShowCrypto       = 'N'
HatWidth         = 64
HatHeight        = 32
KeyboardPoll     = 10
BrightColorCount = 27



#Initialize Matrix objects
options = RGBMatrixOptions()

options.rows       = HatHeight
options.cols       = HatWidth
options.brightness = 100
#stops sparkling 
options.gpio_slowdown = 5


#options.chain_length = self.args.led_chain
#options.parallel = self.args.led_parallel
#options.row_address_type = self.args.led_row_addr_type
#options.multiplexing = self.args.led_multiplexing
#options.pwm_bits = self.args.led_pwm_bits
#options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
#options.led_rgb_sequence = self.args.led_rgb_sequence
#options.pixel_mapper_config = self.args.led_pixel_mapper
#if self.args.led_show_refresh:
#  options.show_refresh_rate = 1

#if self.args.led_no_hardware_pulse:
#  options.disable_hardware_pulsing = True


#The matrix object is what is used to interact with the LED display
TheMatrix    = RGBMatrix(options = options)

#Screen array is a copy of the matrix light layout because RGBMatrix is not queryable.  
ScreenArray  = ([[]])
ScreenArray  = [[ (0,0,0) for i in range(HatWidth)] for i in range(HatHeight)]

#Canvas is an object that we can paint to (setpixels) and then swap to the main display for a super fast update (vsync)
Canvas = TheMatrix.CreateFrameCanvas()
Canvas.Fill(0,0,0)
   


#-----------------------------
# Timers                    --
#-----------------------------

StartTime = time.time()





#Sprite display locations
ClockH,      ClockV,      ClockRGB      = 0,0,  (0,150,0)
DayOfWeekH,  DayOfWeekV,  DayOfWeekRGB  = 0,6,  (150,0,0)
MonthH,      MonthV,      MonthRGB      = 0,12, (0,20,200)
DayOfMonthH, DayOfMonthV, DayOfMonthRGB = 2,18, (100,100,0)
CurrencyH,   CurrencyV,   CurrencyRGB   = 0,27, (0,150,0)

#Sprite filler tuple
SpriteFillerRGB = (0,4,0)














#------------------------------------------------------------------------------
# COLORS                                                                     --
#------------------------------------------------------------------------------

#This section evolved and came out of several different video games (SDColor = SpaceDotColor for example) so the
#names are not always clear.  Obvious names are useful, use any combination you like.

#There are many colors defined here
#some as three separate values representing R,G,b
#some as tubles (R,G,B)
# YellowR, YellowG, YellowB would be used as  color = (YellowR, YellowG, YellowB)


def ApplyGamma(color,TheGamma):
  #Need to round to integer
  NewColor = int(color * TheGamma)
  
  if NewColor > 255: NewColor = 255
  
  #print ("Old:",color," New:",NewColor)
  return NewColor




#Yellow
YellowR = ApplyGamma(220,Gamma)
YellowG = ApplyGamma(220,Gamma)
YellowB = ApplyGamma(0,Gamma)

#Red
RedR = ApplyGamma(100,Gamma)
RedG = ApplyGamma(0,Gamma)
RedB = ApplyGamma(0,Gamma)

#HighRed
HighRedR = ApplyGamma(225,Gamma)
HighRedG = ApplyGamma(0,Gamma)
HighRedB = ApplyGamma(0,Gamma)

#MedRed
MedRedR = ApplyGamma(100,Gamma)
MedRedG = ApplyGamma(0,Gamma)
MedRedB = ApplyGamma(0,Gamma)

#Orange
OrangeR = ApplyGamma(100,Gamma)
OrangeG = ApplyGamma(50,Gamma)
OrangeB = ApplyGamma(0,Gamma)


#Purple
PurpleR = ApplyGamma(75,Gamma)
PurpleG = ApplyGamma(0,Gamma)
PurpleB = ApplyGamma(75,Gamma)

#Green
GreenR = ApplyGamma(0,Gamma)
GreenG = ApplyGamma(100,Gamma)
GreenB = ApplyGamma(0,Gamma)

#HighGreen
HighGreenR = ApplyGamma(0,Gamma)
HighGreenG = ApplyGamma(225,Gamma)
HighGreenB = ApplyGamma(0,Gamma)

#MedGreen
MedGreenR = ApplyGamma(0,Gamma)
MedGreenG = ApplyGamma(155,Gamma)
MedGreenB = ApplyGamma(0,Gamma)

#LowGreen
LowGreenR = ApplyGamma(0,Gamma)
LowGreenG = ApplyGamma(100,Gamma)
LowGreenB = ApplyGamma(0,Gamma)

#DarkGreen
DarkGreenR = ApplyGamma(0,Gamma)
DarkGreenG = ApplyGamma(45,Gamma)
DarkGreenB = ApplyGamma(0,Gamma)


#Blue
BlueR = ApplyGamma(0,Gamma)
BlueG = ApplyGamma(0,Gamma)
BlueB = ApplyGamma(100,Gamma)

#WhiteLow
WhiteLowR = ApplyGamma(45,Gamma)
WhiteLowG = ApplyGamma(45,Gamma)
WhiteLowB = ApplyGamma(45,Gamma)

#WhiteMed
WhiteMedR = ApplyGamma(100,Gamma)
WhiteMedG = ApplyGamma(100,Gamma)
WhiteMedB = ApplyGamma(100,Gamma)

#WhiteHigh
WhiteHighR = ApplyGamma(225,Gamma)
WhiteHighG = ApplyGamma(225,Gamma)
WhiteHighB = ApplyGamma(225,Gamma)

#Character Colors
PacR = ApplyGamma(YellowR,Gamma)
PacG = ApplyGamma(YellowG,Gamma)
PacB = ApplyGamma(YellowB,Gamma)


#Red
Ghost1R = ApplyGamma(150,Gamma)
Ghost1G = ApplyGamma(0,Gamma)
Ghost1B = ApplyGamma(0,Gamma)

#Orange
Ghost2R = ApplyGamma(130,Gamma)
Ghost2G = ApplyGamma(75,Gamma)
Ghost2B = ApplyGamma(0,Gamma)

#Purple
Ghost3R = ApplyGamma(125,Gamma)
Ghost3G = ApplyGamma(0,Gamma)
Ghost3B = ApplyGamma(125,Gamma)

#LightBlue
Ghost4R = ApplyGamma(0,Gamma)
Ghost4G = ApplyGamma(150,Gamma)
Ghost4B = ApplyGamma(150,Gamma)


#Dots
DotR = ApplyGamma(95,Gamma)
DotG = ApplyGamma(95,Gamma)
DotB = ApplyGamma(95,Gamma)

DotRGB = (DotR,DotG,DotB)

#Wall
WallR = ApplyGamma(10,Gamma)
WallG = ApplyGamma(10,Gamma)
WallB = ApplyGamma(100,Gamma)

WallRGB = (WallR,WallG,WallB)


#PowerPills
PillR = ApplyGamma(0,Gamma)
PillG = ApplyGamma(200,Gamma)
PillB = ApplyGamma(0,Gamma)

BlueGhostR = ApplyGamma(0,Gamma)
BlueGhostG = ApplyGamma(0,Gamma)
BlueGhostB = ApplyGamma(200,Gamma)






#HighRed
SDHighRedR = ApplyGamma(255,Gamma)
SDHighRedG = ApplyGamma(0,Gamma)
SDHighRedB = ApplyGamma(0,Gamma)


#MedRed
SDMedRedR = ApplyGamma(175,Gamma)
SDMedRedG = ApplyGamma(0,Gamma)
SDMedRedB = ApplyGamma(0,Gamma)


#LowRed
SDLowRedR = ApplyGamma(100,Gamma)
SDLowRedG = ApplyGamma(0,Gamma)
SDLowRedB = ApplyGamma(0,Gamma)

#DarkRed
SDDarkRedR = ApplyGamma(45,Gamma)
SDDarkRedG = ApplyGamma(0,Gamma)
SDDarkRedB = ApplyGamma(0,Gamma)

# Red RGB Tuples
HighRed = (SDHighRedR,SDHighRedG,SDHighRedB)
MedRed  = (SDMedRedR ,SDMedRedG ,SDMedRedB)
LowRed  = (SDLowRedR ,SDLowRedG ,SDLowRedB)
DarkRed = (SDDarkRedR,SDDarkRedG,SDDarkRedB)
ShadowRed = (25,0,0)


#HighOrange
SDHighOrangeR = ApplyGamma(255,Gamma)
SDHighOrangeG = ApplyGamma(128,Gamma)
SDHighOrangeB = ApplyGamma(0,Gamma)

#MedOrange
SDMedOrangeR = ApplyGamma(200,Gamma)
SDMedOrangeG = ApplyGamma(100,Gamma)
SDMedOrangeB = ApplyGamma(0,Gamma)

#LowOrange
SDLowOrangeR = ApplyGamma(155,Gamma)
SDLowOrangeG = ApplyGamma(75,Gamma)
SDLowOrangeB = ApplyGamma(0,Gamma)

#DarkOrange
SDDarkOrangeR = ApplyGamma(100,Gamma)
SDDarkOrangeG = ApplyGamma(45,Gamma)
SDDarkOrangeB = ApplyGamma(0,Gamma)

HighOrange = (SDHighOrangeR,SDHighOrangeG,SDHighOrangeB)
MedOrange  = (SDMedOrangeR, SDMedOrangeG, SDMedOrangeB)
LowOrange  = (SDLowOrangeR, SDLowOrangeG, SDLowOrangeB)
DarkOrange = (SDDarkOrangeR,SDDarkOrangeG,SDDarkOrangeB)
ShadowOrange = (50,20,0)

# High = (R,G,B)
# Med  = (R,G,B)
# Low  = (R,G,B)
# Dark = (R,G,B)


#SDHighPurple
SDHighPurpleR = ApplyGamma(230,Gamma)
SDHighPurpleG = ApplyGamma(0,Gamma)
SDHighPurpleB = ApplyGamma(255,Gamma)

#MedPurple
SDMedPurpleR = ApplyGamma(105,Gamma)
SDMedPurpleG = ApplyGamma(0,Gamma)
SDMedPurpleB = ApplyGamma(155,Gamma)

#SDLowPurple
SDLowPurpleR = ApplyGamma(75,Gamma)
SDLowPurpleG = ApplyGamma(0,Gamma)
SDLowPurpleB = ApplyGamma(120,Gamma)


#SDDarkPurple
SDDarkPurpleR = ApplyGamma(45,Gamma)
SDDarkPurpleG = ApplyGamma(0,Gamma)
SDDarkPurpleB = ApplyGamma(45,Gamma)

# Purple RGB Tuples
HighPurple = (SDHighPurpleR,SDHighPurpleG,SDHighPurpleB)
MedPurple  = (SDMedPurpleR ,SDMedPurpleG ,SDMedPurpleB)
LowPurple  = (SDLowPurpleR ,SDLowPurpleG ,SDLowPurpleB)
DarkPurple = (SDDarkPurpleR,SDDarkPurpleG,SDDarkPurpleB)
ShadowPurple = (25,0,25)





#HighGreen
SDHighGreenR = ApplyGamma(0,Gamma)
SDHighGreenG = ApplyGamma(255,Gamma)
SDHighGreenB = ApplyGamma(0,Gamma)

#MedGreen
SDMedGreenR = ApplyGamma(0,Gamma)
SDMedGreenG = ApplyGamma(200,Gamma)
SDMedGreenB = ApplyGamma(0,Gamma)

#LowGreen
SDLowGreenR = ApplyGamma(0,Gamma)
SDLowGreenG = ApplyGamma(100,Gamma)
SDLowGreenB = ApplyGamma(0,Gamma)

#DarkGreen
SDDarkGreenR = ApplyGamma(0,Gamma)
SDDarkGreenG = ApplyGamma(45,Gamma)
SDDarkGreenB = ApplyGamma(0,Gamma)

#Green tuples
HighGreen = (SDHighGreenR,SDHighGreenG,SDHighGreenB)
MedGreen  = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
LowGreen  = (SDLowGreenR,SDLowGreenG,SDLowGreenB)
DarkGreen = (SDDarkGreenR,SDDarkGreenG,SDDarkGreenB)
ShadowGreen = (0,35,0)




#HighBlue
SDHighBlueR = ApplyGamma(0,Gamma)
SDHighBlueG = ApplyGamma(0,Gamma)
SDHighBlueB = ApplyGamma(255,Gamma)


#MedBlue
SDMedBlueR = ApplyGamma(0,Gamma)
SDMedBlueG = ApplyGamma(0,Gamma)
SDMedBlueB = ApplyGamma(175,Gamma)

#LowBlue
SDLowBlueR = ApplyGamma(0,Gamma)
SDLowBlueG = ApplyGamma(0,Gamma)
SDLowBlueB = ApplyGamma(100,Gamma)

#DarkBlue
SDDarkBlueR = ApplyGamma(0,Gamma)
SDDarkBlueG = ApplyGamma(0,Gamma)
SDDarkBlueB = ApplyGamma(45,Gamma)


# Blue RGB Tuples
HighBlue = (SDHighBlueR,SDHighBlueG,SDHighBlueB)
MedBlue  = (SDHighBlueR,SDHighBlueG,SDHighBlueB)
LowBlue  = (SDHighBlueR,SDHighBlueG,SDHighBlueB)
DarkBlue = (SDHighBlueR,SDHighBlueG,SDHighBlueB)
ShadowBlue = (0,0,25)


#WhiteMax
SDMaxWhiteR = ApplyGamma(255,Gamma)
SDMaxWhiteG = ApplyGamma(255,Gamma)
SDMaxWhiteB = ApplyGamma(255,Gamma)

#WhiteHigh
SDHighWhiteR = ApplyGamma(255,Gamma)
SDHighWhiteG = ApplyGamma(255,Gamma)
SDHighWhiteB = ApplyGamma(255,Gamma)

#WhiteMed
SDMedWhiteR = ApplyGamma(150,Gamma)
SDMedWhiteG = ApplyGamma(150,Gamma)
SDMedWhiteB = ApplyGamma(150,Gamma)

#WhiteLow
SDLowWhiteR = ApplyGamma(100,Gamma)
SDLowWhiteG = ApplyGamma(100,Gamma)
SDLowWhiteB = ApplyGamma(100,Gamma)

#WhiteDark
SDDarkWhiteR = ApplyGamma(35,Gamma)
SDDarkWhiteG = ApplyGamma(35,Gamma)
SDDarkWhiteB = ApplyGamma(35,Gamma)


# White RGB Tuples
MaxWhite  = (SDMaxWhiteR,SDMaxWhiteG,SDMaxWhiteB)
HighWhite = (SDHighWhiteR,SDHighWhiteG,SDHighWhiteB)
MedWhite  = (SDHighWhiteR,SDHighWhiteG,SDHighWhiteB)
LowWhite  = (SDHighWhiteR,SDHighWhiteG,SDHighWhiteB)
DarkWhite = (SDHighWhiteR,SDHighWhiteG,SDHighWhiteB)
ShadowWhite = (15,15,15)


#YellowMax
SDMaxYellowR = ApplyGamma(255,Gamma)
SDMaxYellowG = ApplyGamma(255,Gamma)
SDMaxYellowB = ApplyGamma(0,Gamma)


#YellowHigh
SDHighYellowR = ApplyGamma(215,Gamma)
SDHighYellowG = ApplyGamma(215,Gamma)
SDHighYellowB = ApplyGamma(0,Gamma)

#YellowMed
SDMedYellowR = ApplyGamma(175,Gamma)
SDMedYellowG = ApplyGamma(175,Gamma)
SDMedYellowB = ApplyGamma(0,Gamma)

#YellowLow
SDLowYellowR = ApplyGamma(100,Gamma)
SDLowYellowG = ApplyGamma(100,Gamma)
SDLowYellowB = ApplyGamma(0,Gamma)


#YellowDark
SDDarkYellowR = ApplyGamma(55,Gamma)
SDDarkYellowG = ApplyGamma(55,Gamma)
SDDarkYellowB = ApplyGamma(0,Gamma)


# Yellow RGB Tuples
MaxYellow  = (SDMaxYellowR,SDMaxYellowG,SDMaxYellowB)
HighYellow = (SDHighYellowR,SDHighYellowG,SDHighYellowB)
MedYellow  = (SDMedYellowR,SDMedYellowG,SDMedYellowB)
LowYellow  = (SDLowYellowR,SDLowYellowG,SDLowYellowB)
DarkYellow = (SDDarkYellowR,SDDarkYellowG,SDDarkYellowB)
ShadowYellow = (30,30,0)


#Pink
SDMaxPinkR = ApplyGamma(155,Gamma)
SDMaxPinkG = ApplyGamma(0,Gamma)
SDMaxPinkB = ApplyGamma(130,Gamma)

SDHighPinkR = ApplyGamma(130,Gamma)
SDHighPinkG = ApplyGamma(0,Gamma)
SDHighPinkB = ApplyGamma(105,Gamma)

SDMedPinkR = ApplyGamma(100,Gamma)
SDMedPinkG = ApplyGamma(0,Gamma)
SDMedPinkB = ApplyGamma(75,Gamma)

SDLowPinkR = ApplyGamma(75,Gamma)
SDLowPinkG = ApplyGamma(0,Gamma)
SDLowPinkB = ApplyGamma(50,Gamma)

SDDarkPinkR = ApplyGamma(45,Gamma)
SDDarkPinkG = ApplyGamma(0,Gamma)
SDDarkPinkB = ApplyGamma(50,Gamma)


# Pink RGB Tuples
MaxPink  = (SDMaxPinkR,SDMaxPinkG,SDMaxPinkB)
HighPink = (SDHighPinkR,SDHighPinkG,SDHighPinkB)
MedPink  = (SDHighPinkR,SDHighPinkG,SDHighPinkB)
LowPink  = (SDHighPinkR,SDHighPinkG,SDHighPinkB)
DarkPink = (SDHighPinkR,SDHighPinkG,SDHighPinkB)
ShadowPink = (22,0,25)


#Cyan
SDMaxCyanR = ApplyGamma(0,Gamma)
SDMaxCyanG = ApplyGamma(255,Gamma)
SDMaxCyanB = ApplyGamma(255,Gamma)

SDHighCyanR = ApplyGamma(0,Gamma)
SDHighCyanG = ApplyGamma(150,Gamma)
SDHighCyanB = ApplyGamma(150,Gamma)

SDMedCyanR = ApplyGamma(0,Gamma)
SDMedCyanG = ApplyGamma(100,Gamma)
SDMedCyanB = ApplyGamma(100,Gamma)

SDLowCyanR = ApplyGamma(0,Gamma)
SDLowCyanG = ApplyGamma(75,Gamma)
SDLowCyanB = ApplyGamma(75,Gamma)

SDDarkCyanR = ApplyGamma(0,Gamma)
SDDarkCyanG = ApplyGamma(50,Gamma)
SDDarkCyanB = ApplyGamma(50,Gamma)

# Cyan RGB Tuples
MaxCyan  = (SDMaxCyanR,SDMaxCyanG,SDMaxCyanB)
HighCyan = (SDHighCyanR,SDHighCyanG,SDHighCyanB)
MedCyan  = (SDHighCyanR,SDHighCyanG,SDHighCyanB)
LowCyan  = (SDHighCyanR,SDHighCyanG,SDHighCyanB)
DarkCyan = (SDHighCyanR,SDHighCyanG,SDHighCyanB)
ShadowCyan = (0,20,20)




ColorList = []
ColorList.append((0,0,0))
# 1 2 3 4
ColorList.append((SDDarkWhiteR,SDDarkWhiteG,SDDarkWhiteB))
ColorList.append((SDLowWhiteR,SDLowWhiteG,SDLowWhiteB))
ColorList.append((SDMedWhiteR,SDMedWhiteG,SDMedWhiteB))
ColorList.append((SDHighWhiteR,SDHighWhiteG,SDHighWhiteB))

# 5 6 7 8
ColorList.append((SDDarkRedR,SDDarkRedG,SDDarkRedB))
ColorList.append((SDLowRedR,SDLowRedG,SDLowRedB))
ColorList.append((SDMedRedR,SDMedRedG,SDMedRedB))
ColorList.append((SDHighRedR,SDHighRedG,SDHighRedB))

# 9 10 11 12
ColorList.append((SDDarkGreenR,SDDarkGreenG,SDDarkGreenB))
ColorList.append((SDLowGreenR,SDLowGreenG,SDLowGreenB))
ColorList.append((SDMedGreenR,SDMedGreenG,SDMedGreenB))
ColorList.append((SDHighGreenR,SDHighGreenG,SDHighGreenB))

# 13 14 15 16
ColorList.append((SDDarkBlueR,SDDarkBlueG,SDDarkBlueB))
ColorList.append((SDLowBlueR,SDLowBlueG,SDLowBlueB))
ColorList.append((SDMedBlueR,SDMedBlueG,SDMedBlueB))
ColorList.append((SDHighBlueR,SDHighBlueG,SDHighBlueB))

# 17 18 19 20
ColorList.append((SDDarkOrangeR,SDDarkOrangeG,SDDarkOrangeB))
ColorList.append((SDLowOrangeR,SDLowOrangeG,SDLowOrangeB))
ColorList.append((SDMedOrangeR,SDMedOrangeG,SDMedOrangeB))
ColorList.append((SDHighOrangeR,SDHighOrangeG,SDHighOrangeB))

# 21 22 23 24
ColorList.append((SDDarkYellowR,SDDarkYellowG,SDDarkYellowB))
ColorList.append((SDLowYellowR,SDLowYellowG,SDLowYellowB))
ColorList.append((SDMedYellowR,SDMedYellowG,SDMedYellowB))
ColorList.append((SDHighYellowR,SDHighYellowG,SDHighYellowB))

# 25 26 27 28
ColorList.append((SDDarkPurpleR,SDDarkPurpleG,SDDarkPurpleB))
ColorList.append((SDLowPurpleR,SDLowPurpleG,SDLowPurpleB))
ColorList.append((SDMedPurpleR,SDMedPurpleG,SDMedPurpleB))
ColorList.append((SDHighPurpleR,SDHighPurpleG,SDHighPurpleB))

# 29 30 31 32 33
ColorList.append((SDDarkPinkR,SDDarkPinkG,SDDarkPinkB))
ColorList.append((SDLowPinkR,SDLowPinkG,SDLowPinkB))
ColorList.append((SDMedPinkR,SDMedPinkG,SDMedPinkB))
ColorList.append((SDHighPinkR,SDHighPinkG,SDHighPinkB))
ColorList.append((SDMaxPinkR,SDMaxPinkG,SDMaxPinkB))


# 34 35 36 37 38
ColorList.append((SDDarkCyanR,SDDarkCyanG,SDDarkCyanB))
ColorList.append((SDLowCyanR,SDLowCyanG,SDLowCyanB))
ColorList.append((SDMedCyanR,SDMedCyanG,SDMedCyanB))
ColorList.append((SDHighCyanR,SDHighCyanG,SDHighCyanB))
ColorList.append((SDMaxCyanR,SDMaxCyanG,SDMaxCyanB))


# MAX
# 39 40 41 42 43 44 45
ColorList.append((255,  0,  0))  #MAX-RED    39
ColorList.append((  0,255,  0))  #MAX-GREEN  40
ColorList.append((  0,  0,255))  #MAX-BLUE   41
ColorList.append((255,255,0  ))  #MAX-YELLOW 42
ColorList.append((255,  0,255))  #MAX-PURPLE 43
ColorList.append((  0,255,255))  #MAX-CYAN   44
ColorList.append((255,255,255))  #MAX-WHITE  45

#max orange is 20

ColorList.append((SDMaxCyanR,SDMaxCyanG,SDMaxCyanB))



GlowingTextRGB   = []
GlowingShadowRGB = []

GlowingTextRGB.append((250,250,250)) #WHITE
GlowingTextRGB.append((200,  0,  0)) #RED
GlowingTextRGB.append((  0,200,  0)) #Green
GlowingTextRGB.append((  0,  0,200)) #Blue
GlowingTextRGB.append((200,200,  0)) #Yellow
GlowingTextRGB.append((200,  0,200)) #Purple
GlowingTextRGB.append((  0,200,200)) #Cyan
GlowingTextRGB.append((200,100,200)) #Orange

GlowingShadowRGB.append(( 20, 20, 20)) #WHITE
GlowingShadowRGB.append(( 20,  0,  0)) #RED
GlowingShadowRGB.append((  0, 20,  0)) #Green
GlowingShadowRGB.append((  0,  0, 20)) #Blue
GlowingShadowRGB.append(( 20, 20,  0)) #Yellow
GlowingShadowRGB.append(( 20,  0, 20)) #Purple
GlowingShadowRGB.append((  0, 20, 20)) #Cyan
GlowingShadowRGB.append(( 20, 10,  0)) #Orange




# MAX
# 39 40 41 42 43 44 45
ColorList.append((255,  0,  0))  #MAX-RED    39
ColorList.append((  0,255,  0))  #MAX-GREEN  40
ColorList.append((  0,  0,255))  #MAX-BLUE   41
ColorList.append((255,255,0  ))  #MAX-YELLOW 42
ColorList.append((255,  0,255))  #MAX-PURPLE 43
ColorList.append((  0,255,255))  #MAX-CYAN   44
ColorList.append((255,255,255))  #MAX-WHITE  45




BrightColorList = []
BrightColorList.append((0,0,0))
# 1 2 3
BrightColorList.append((SDLowWhiteR,SDLowWhiteG,SDLowWhiteB))
BrightColorList.append((SDMedWhiteR,SDMedWhiteG,SDMedWhiteB))
BrightColorList.append((SDHighWhiteR,SDHighWhiteG,SDHighWhiteB))

# 4 5 6
BrightColorList.append(LowRed)
BrightColorList.append(MedRed)
BrightColorList.append(HighRed)

# 7 8 9
BrightColorList.append((SDLowGreenR,SDLowGreenG,SDLowGreenB))
BrightColorList.append((SDMedGreenR,SDMedGreenG,SDMedGreenB))
BrightColorList.append((SDHighGreenR,SDHighGreenG,SDHighGreenB))

# 10 11 12
BrightColorList.append((SDLowBlueR,SDLowBlueG,SDLowBlueB))
BrightColorList.append((SDMedBlueR,SDMedBlueG,SDMedBlueB))
BrightColorList.append((SDHighBlueR,SDHighBlueG,SDHighBlueB))

# 13 14 15
BrightColorList.append((SDLowOrangeR,SDLowOrangeG,SDLowOrangeB))
BrightColorList.append((SDMedOrangeR,SDMedOrangeG,SDMedOrangeB))
BrightColorList.append((SDHighOrangeR,SDHighOrangeG,SDHighOrangeB))

# 16 17 18
BrightColorList.append((SDLowYellowR,SDLowYellowG,SDLowYellowB))
BrightColorList.append((SDMedYellowR,SDMedYellowG,SDMedYellowB))
BrightColorList.append((SDHighYellowR,SDHighYellowG,SDHighYellowB))

# 19 20 21
BrightColorList.append((SDLowPurpleR,SDLowPurpleG,SDLowPurpleB))
BrightColorList.append((SDMedPurpleR,SDMedPurpleG,SDMedPurpleB))
BrightColorList.append((SDHighPurpleR,SDHighPurpleG,SDHighPurpleB))

# 22 23 24
BrightColorList.append((SDMedPinkR,SDMedPinkG,SDMedPinkB))
BrightColorList.append((SDHighPinkR,SDHighPinkG,SDHighPinkB))
BrightColorList.append((SDMaxPinkR,SDMaxPinkG,SDMaxPinkB))


# 25 26 27
BrightColorList.append((SDMedCyanR,SDMedCyanG,SDMedCyanB))
BrightColorList.append((SDHighCyanR,SDHighCyanG,SDHighCyanB))
BrightColorList.append((SDMaxCyanR,SDMaxCyanG,SDMaxCyanB))









#ColorList.append((SDDarkR,SDDarkG,SDDarkB))
#ColorList.append((SDLowR,SDLowG,SDLowB))
#ColorList.append((SDMedR,SDMedG,SDMedB))
#ColorList.append((SDHighR,SDHighG,SDHighB))


#--> need to apply gamma to SD variables directly, as they are referenced later




# def ApplyGamma(r,g,b,Gamma):
  # NewR = r * Gamma
  # NewG = g * Gamma
  # NewB = b * Gamma
  
  # if NewR > 255: NewR = 255
  # if NewG > 255: NewG = 255
  # if NewB > 255: NewB = 255
  # print ("Old:",r,g,b," New:",NewR,NewG,NewB)
  # return NewR,NewG,NewB

# if (Gamma > 1):
  # for index in range(1,38):
    # r,g,b = ColorList[index]
    # r,g,b = ApplyGamma(r,g,b,Gamma)
    # ColorList[index] = r,g,b




#------------------------------------------------------------------------------
#                                                                            --
# BIG LED FUNCTIONS                                                          --
#                                                                            --
#------------------------------------------------------------------------------

def ClearBigLED():
  TheMatrix.Clear()


def ClearBuffers():
  #There are TWO buffers.  One is built into the API, and we can write to it but now query it.  That is the Canvas.
  #The second one is ScreenArray, which is our own version, kept up to date when we draw to the Canvas or the Matrix.


  global ScreenArray

  ScreenArray  = [[]]
  ScreenArray  = [[ (0,0,0) for i in range(HatWidth)] for i in range(HatHeight)]
  Canvas.Clear()






#------------------------------------------------------------------------------
#   ____ _                                                                   --
#  / ___| | __ _ ___ ___  ___  ___                                           --
# | |   | |/ _` / __/ __|/ _ \/ __|                                          --
# | |___| | (_| \__ \__ \  __/\__ \                                          --
#  \____|_|\__,_|___/___/\___||___/                                          --
#                                                                            --
#------------------------------------------------------------------------------



#This is a custom function because UnicornHatHD does not have one !
def setpixels(TheBuffer):
  x = 0
  y = 0

  #Copy our old buffer to the new LED buffer.  This will be replaced.
  #ScreenArray = TheBuffer

  for y in range (HatHeight):
    for x in range (HatWidth):
      r,g,b = TheBuffer[y][x]
      setpixel(x,y,r,g,b)



      
def setpixelsWithClock(TheBuffer,ClockSprite,h,v):
  x = 0
  y = 0

  for y in range (HatHeight):
    for x in range (HatWidth):
      if (x >= h and x <= h+ClockSprite.width) and (y >= v and y <= v+ClockSprite.height):
        r = ClockSprite.r
        g = ClockSprite.g
        b = ClockSprite.b
      else:
        r,g,b = TheBuffer[y][x]
      setpixel(x,y,r,g,b)



      
      

def setpixel(x, y, r, g, b):
  global ScreenArray

  if (CheckBoundary(x,y) == 0):
    TheMatrix.SetPixel(x,y,r,g,b)
    ScreenArray[y][x] = (r,g,b)

    
def setpixelRGB(x, y, RGB):
  global ScreenArray
  r,g,b = RGB
  if (CheckBoundary(x,y) == 0):
    TheMatrix.SetPixel(x,y,r,g,b)
    ScreenArray[y][x] = (r,g,b)
    

def setpixelsLED(TheBuffer):
  x = 0
  y = 0

  for y in range (HatHeight):
    for x in range (HatWidth):
      
      r,g,b = TheBuffer[y][x]
      TheMatrix.SetPixel(x,y,r,g,b)



#Bug fix because my HD is inverted horizontally
def getpixel(h,v):
  #print ("get hv:",h,v)
  r = 0
  g = 0
  b = 0
  #r,g,b = unicorn.get_pixel(abs(15-h),v)
  r,g,b = ScreenArray[v][h]
  #print("Get pixel HV RGB:",h,v,"-",r,g,b)
  return r,g,b      


def ShowScreenArray():
  for h in range (0,HatWidth):
    for v in range (0,HatHeight):
      r,g,b = ScreenArray[v][h]
      if (r + g + b > 0):
        #FlashDot(h,v,0.005)
        TheMatrix.SetPixel(h,v,0,0,220)
        time.sleep(0.0)
        


  
  
def ClockTimer(seconds):
  global start_time
  elapsed_time = time.time() - start_time
  elapsed_hours, rem = divmod(elapsed_time, 3600)
  elapsed_minutes, elapsed_seconds = divmod(rem, 60)
  #print("Elapsed Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours),int(elapsed_minutes),elapsed_seconds),end="\r")

  if (elapsed_seconds >= seconds ):
    start_time = time.time()
    return 1
  else:
    return 0
  
  
  
  
  
  
  






  
  
class Sprite(object):
  def __init__(self,width,height,r,g,b,grid):
    self.width  = width
    self.height = height
    self.r      = r
    self.g      = g
    self.b      = b
    self.grid   = grid
    self.name   = "?"

  
  
  
    #Draw the sprite using an affect like in the movie Tron 
  def LaserScan(self,h1,v1,speed=0.005):
    x = 0
    y = 0
    r = self.r
    g = self.g
    b = self.b
    #print ("CAS - LaserScan -")
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if(self.grid[count] >= 0):
        if (CheckBoundary((x+h1),y+v1) == 0):
          FlashDot4((x+h1),y+v1,speed)
          TheMatrix.SetPixel((x+h1),y+v1,r,g,b)
          TheMatrix.SwapOnVSync(Canvas)



  
  def DisplayIncludeBlack(self,h1,v1):
    x = 0,
    y = 0
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
      elif self.grid[count] == 0:
        if (CheckBoundary(x+h1,y+v1) == 0):
          TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)



  def Display(self,h1,v1):
    x = 0,
    y = 0
    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
    #unicorn.show()


  def CopySpriteToBuffer(self,h1,v1):
    #Does the same as Display, but does not call show(), allowing calling function to further modify the Buffer
    #before displaying
    x = 0,
    y = 0
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
      elif self.grid[count] == 0:
        if (CheckBoundary(x+h1,y+v1) == 0):
          TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
    #unicorn.show()
    
    

  def EraseNoShow(self,h1,v1):
    #This function draws a black sprite, erasing the sprite.  
    #It does NOT call #unicorn.show(), which would cause a visilble blink
    x = 0
    y = 0
    #print ("Erase:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          #TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
          TheMatrix.SetPixel(x+h1,y+v1,0,0,0)

    
  def Erase(self,h1,v1):
    #This function draws a black sprite, erasing the sprite.  This may be useful for
    #a future "floating over the screen" type of sprite motion
    #It is pretty fast now, seems just as fast as blanking whole screen using off() or clear()
    x = 0
    y = 0
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          TheMatrix.SetPixel(x+h1,y+v1,0,0,0)

  def HorizontalFlip(self):
    x = 0
    y = 0
    flipgrid = []
    
    #print ("flip:",self.width, self.height)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      #print("Calculations: ",(y*self.height)+ self.height-x-1)  
      flipgrid.append(self.grid[(y*self.height)+ self.height-x-1])  
    #print("Original:", str(self.grid))
    #print("Flipped :", str(flipgrid))
    self.grid = flipgrid      

    
  def Scroll(self,h,v,direction,moves,delay):
    #print("Entering Scroll")
    x = 0
    oldh = 0
    #Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      for count in range (0,moves):
        h = h + (modifier)
        #erase old sprite
        if count >= 1:
          oldh = h - modifier
          #print ("Scroll:",self.width, self.height, self.r, self.g, self.b,h,v)
          #TheMatrix.Clear()
          self.Erase(oldh,v)  

        #draw new sprite
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(delay)

        #Check for keyboard input
        r = random.randint(0,50)
        if (r == 0):
          Key = PollKeyboard()


    if direction == "up" or direction == "down":
      for count in range (0,moves):
        v = v + (modifier)
        #erase old sprite
        if count >= 1:
          oldv = v - modifier
          #self.Erase(h,oldv)
          setpixels(Buffer)
            
        #draw new sprite
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(delay)
        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()
        

        
  
  def ScrollAcrossScreen(self,h,v,direction,ScrollSleep):
    #print ("--ScrollAcrossScreen--")
    #print ("width height",self.width,self.height)
    if (direction == "right"):
      self.Scroll((0- self.width),v,"right",(HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Scroll(HatWidth-1,v,"left",(HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Scroll(h,HatWidth-1,"left",(HatWidth + self.height),ScrollSleep)


  def DisplayNoBlack(self,h1,v1):
    x = 0,
    y = 0

    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if (CheckBoundary(x+h1,y+v1) == 0):
        if (not(self.r == 0 and self.g == 0 and self.b == 0)):
          TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
    


  def Float(self,h,v,direction,moves,delay):
    #Scroll across the screen, floating over the background
    
    x = 0
    oldh = 0
    #Capture Background
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    
    
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      
      for count in range (0,moves):
        h = h + (modifier)
        #erase old sprite
        #print ("Erasing Frame HV:",oldf," ",h,v)
        setpixels(Buffer)

        if count >= 1:
          oldh = h - modifier
          
        #draw new sprite
        self.Display(h,v)
        #unicorn.show() 
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(delay)

      #Check for keyboard input
      r = random.randint(0,5)
      if (r == 0):
        Key = PollKeyboard()

  
  def FloatAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Float((0- self.width),v,"right",(HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Float(HatWidth-1,v,"left",(HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Float(h,HatWidth-1,"left",(HatWidth + self.height),ScrollSleep)














# ----------------------
# -- Animated Sprites --
# ----------------------

class AnimatedSprite(object):
  def __init__(self,width,height,r,g,b,frames,grid):
    self.width  = width
    self.height = height
    self.r      = r
    self.g      = g
    self.b      = b
    self.frames = frames
    self.grid   = []

  def Display(self,h1,v1,frame):
    x = 0,
    y = 0

    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y, " frame: ", frame)
      if self.grid[frame][count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
    #unicorn.show() 


  def DisplayNoBlack(self,h1,v1,frame):
    x = 0,
    y = 0

    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y, " frame: ", frame)
      if self.grid[frame][count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          if (not(self.r == 0 and self.g == 0 and self.b == 0)):
            TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
    #unicorn.show() 



  def Erase(self,h1,v1,frame):
    #This function draws a black sprite, erasing the sprite.  This may be useful for
    #a future "floating over the screen" type of sprite motion
    #It is pretty fast now, seems just as fast as blanking whole screen using off() or clear()
    x = 0
    y = 0
    #print ("Erase:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[frame][count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          #TheMatrix.SetPixel(x+h1,y+v1,255,255,255)
          #unicorn.show()
          #time.sleep(0.05)
          TheMatrix.SetPixel(x+h1,y+v1,0,0,0)

          
  def EraseSpriteFromPlayfield(self,Playfield):
    #Erase the sprite by writing 'EmptyObject' to every spot on the playfield occupied by the sprite
    x     = 0
    y     = 0
    count = 0



    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if (CheckBoundary(x+h1,y+v1) == 0):
        #TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
        Playfield[y+v1][x+h1] = EmptyObject
        #FlashDot(x+h1,y+v1,0.002)
    return Playfield



  def HorizontalFlip(self):
    #Attempting to speed things up by disabling garbage collection
    gc.disable()
    for f in range(0,self.frames ):
      x = 0
      y = 0
      flipgrid = []
      #print ("flip:",self.width, self.height)
      for count in range (0,(self.width * self.height )):
        y,x = divmod(count,self.width)
        #print("Count:",count,"xy",x,y)
        #print("Calculations: ",(y*self.height)+ self.height-x-1)  
        flipgrid.append(self.grid[f][(y*self.height)+ self.height-x-1])  
      #print("Original:", str(self.grid[f]))
      #print("Flipped :", str(flipgrid))
      self.grid[f] = flipgrid      
    gc.enable()
          
  def Scroll(self,h,v,direction,moves,delay):
    #print("AnimatedSprite.scroll")
    x = 0
    oldh = 0
    #Capture Background
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      
      for count in range (0,moves):
        oldf = f
        f = f+1
        if (f > self.frames):
          f = 0
        h = h + (modifier)
        #erase old sprite
        #print ("Erasing Frame HV:",oldf," ",h,v)
        if count >= 1:
          oldh = h - modifier
          #print ("Scroll:",self.width, self.height, self.r, self.g, self.b,h,v)
          self.Erase(oldh,v,oldf)
        #draw new sprite
        setpixels(Buffer)
        self.Display(h,v,f)
        #unicorn.show() 
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(delay)

        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()



  def ScrollWithFrames(self,h,v,direction,moves,delay):
    #print("Entering Scroll")
    x    = 0
    oldh = 0
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    oldf = self.frames
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      for count in range (0,moves):
        #print ("Count:",count)
        if (count >= 1):
          oldh = h
          #print ("Erasing Frame: ", oldf, " hv: ",oldh,v)
          self.Erase(oldh,v,oldf+1)
        h = h + (modifier)
        #print ("incrementing H:",h)

        #Check for keyboard input
        r = random.randint(0,25)
        if (r == 0):
          Key = PollKeyboard()

        #Animate Each Frame
        for f in range (0, self.frames+1):
          #erase old sprite
          oldf = f-1
          if oldf < 0:
            oldf = self.frames
          #print ("Erasing Frame: ", oldf, " hv: ",h,v)
          self.Erase(h,v,oldf)
          setpixels(Buffer)
            
          #draw new sprite
          #print ("Display Frame: ", f, " hv: ",h,v)
          self.Display(h,v,f)
          #unicorn.show()
          #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)

          time.sleep(delay)
          self.Erase(h,v,f)

       
  
  def ScrollAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Scroll((0- self.width),v,"right",(HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Scroll(HatWidth-1,v,"left",(HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Scroll(h,HatWidth-1,"left",(HatWidth + self.height),ScrollSleep)





  def Float(self,h,v,direction,moves,delay):
    #Scroll across the screen, floating over the background
    
    x = 0
    oldh = 0
    #Capture Background
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      
      for count in range (0,moves):
        oldf = f
        f = f+1
        if (f > self.frames):
          f = 0
        h = h + (modifier)
        #erase old sprite
        #print ("Erasing Frame HV:",oldf," ",h,v)
        setpixels(Buffer)

        if count >= 1:
          oldh = h - modifier
          #print ("Scroll:",self.width, self.height, self.r, self.g, self.b,h,v)
          
        #draw new sprite
        self.DisplayNoBlack(h,v,f)
        #unicorn.show() 
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(delay)

        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()

  
  def FloatAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Float((0- self.width),v,"right",(HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Float(HatWidth-1,v,"left",(HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Float(h,HatWidth-1,"left",(HatWidth + self.height),ScrollSleep)





  def Animate(self,h,v,delay,direction):
    x = 0,
    y = 0,
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    if (direction == 'forward'):
      for f in range (0,self.frames+1):
        self.Display(h,v,f)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(delay)
        setpixels(Buffer)
    else:  
      for f in range (0,self.frames+1):
        self.Display(h,v,(self.frames-f))
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(delay)
        setpixels(Buffer)
      
      





      


# ----------------------------
# -- Color Animated Sprites --
# ----------------------------

class ColorAnimatedSprite(object):
  def __init__(self,h,v,name,width,height,frames,framerate,grid):
    self.h      = h
    self.v      = v
    self.name   = name
    self.width  = width
    self.height = height
    self.frames = frames
    self.currentframe = 1
    self.framerate    = framerate #how many ticks per frame of animation, higher the number the slower the animation
    self.grid         = [[]]      #holds numbers that indicate color of the pixel
    self.ticks        = 0         #internal calculation of how many times a frame has been displayed.  
  


  def Display(self,h1,v1):
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe


    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print ("Name:",self.name," Frame:",frame, " Count: ",count, "Width Height",self.width,self.height )
      #print ("self.grid[frame][count]:",self.grid[frame][count] )
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h1),y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          #print ("CAS - Display - rgb",r,g,b)
          if (r > -1 and g > -1 and b > -1):
            TheMatrix.SetPixel(x+h1,y+v1,r,g,b)
            setpixel(x+h1,y+v1,r,g,b)



  def DisplayNoBlack(self,h1,v1):
    #Treat black pixels in sprite as transparent
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print ("Name:",self.name," Frame:",frame, " Count: ",count, "Width Height",self.width,self.height )
      #print ("self.grid[frame][count]:",self.grid[frame][count] )
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h1),y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          #print ("CAS - Display - rgb",r,g,b)
          if (not(r == 0 and g == 0 and b == 0)):
            TheMatrix.SetPixel(x+h1,y+v1,r,g,b)
    #unicorn.show() 

    self.currentframe = self.currentframe + 1
    if (self.currentframe > self.frames):
      self.currentframe = 1



  def DisplayAnimated(self,h1 = -1, v1 = -1):
    #Treat black pixels in sprite as transparent -- maybe? Not yet.  Currently erasing.
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    
    if (h1 < 0):
      h1 = self.h
    if (v1 < 0):
      v1 = self.v

    self.ticks = self.ticks + 1
   
    #NOTE: This usage of ticks is different than in ScrollWithFrames
    if (self.ticks == self.framerate):
      self.currentframe = self.currentframe + 1
      self.ticks        = 0

    if (self.currentframe > self.frames):
      self.currentframe = 1


    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      

      if (CheckBoundary((x+h1),y+v1) == 0):
        r,g,b =  ColorList[self.grid[self.currentframe][count]]
        TheMatrix.SetPixel(x+h1,y+v1,r,g,b)

       

    
    return
   


  def Erase(self):
    #This function draws a black sprite, erasing the sprite.  This may be useful for
    #a future "floating over the screen" type of sprite motion
    #It is pretty fast now, seems just as fast as blanking whole screen using off() or clear()
    x = 0
    y = 0
    h1 = self.h
    v1 = self.v
    frame = self.currentframe
    #print ("CAS - Erase - width hieigh HV currentframe",self.width, self.height, h1,v1,frame)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
     # print("Count:",count,"xy",x,y)
     # print ("CAS - Erase Frame Count",frame,count)
      if self.grid[frame][count] > 0:
        if (CheckBoundary(abs(15-(x+h1)),y+v1) == 0):
         # print ("CAS - Erase HV:",x+h1,y+v1)
          TheMatrix.SetPixel(x+h1,y+v1,0,0,0)

          
  def EraseLocation(self,h,v):
    x = 0
    y = 0
    frame = self.currentframe

    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)

 
      if self.grid[frame][count] > 0:
        if (CheckBoundary((x+h),y+v) == 0):
          #print ("CAS - EraseLocation HV:",x+h,y+v)
          TheMatrix.SetPixel(x+h,y+v,0,0,0)
          

  def EraseSpriteFromPlayfield(self,Playfield):
    #Erase the sprite by writing 'EmptyObject' to every spot on the playfield occupied by the sprite
    x     = 0
    y     = 0
    count = 0


    width   = self.width 
    height  = self.height
    h       = self.h
    v       = self.v
    frame   = self.currentframe
  


    for count in range (0,(width * height)):
      y,x = divmod(count,width)

      if (CheckBoundary(x+h,y+v) == 0):
        TheMatrix.SetPixel(x+h,y+v,0,0,0)
        Playfield[y+v][x+h] = EmptyObject
    return Playfield



          
  def Scroll(self,h,v,direction,moves,delay):
    #print("CAS - Scroll -   HV Direction moves Delay", h,v,direction,moves,delay)
    x = 0
    oldh = 0
    r = 0
    g = 0
    b = 0
    
    #Capture Background
    #Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("CAS - Scroll - Direction: ",direction)  
      
      for count in range (0,moves):
        #print ("CAS - Scroll - currentframe: ",self.currentframe)
        if (self.currentframe < (self.frames)):
          self.currentframe = self.currentframe + 1
        else:
          self.currentframe = 1
        h = h + (modifier)
        if count >= 1:
          oldh = h - modifier

        #draw new sprite
        #self.setpixels(Buffer)
          
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(delay)


  def ScrollWithFrames(self,h,v,direction,moves,delay):

  #NOTE: We need a rewrite.  We need to take into account movenet per tick as well as frames per tick


    #print("CAS - ScrollWithFrames - HV direction moves delay", h,v,direction,moves,delay)
    x    = 0
    oldh = 0
    self.currentframe = 1
    self.ticks = 0


    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    oldf = self.frames
    #we use f to iterate the animation frames
    f = self.frames
    

    if direction == "left" or direction == "right":
      for count in range (0,moves):
        #print ("Count:",count)
        self.ticks = self.ticks + 1

#this is where we need to include distance per tick

        if (count >= 1):
          oldh = h
          h = h + (modifier)
          #print ("CAS - SWF - H oldh modifier",h,oldh,modifier)
        

        m,r = divmod(self.ticks, self.framerate)
        if (r== 0):
          self.Display(h,v)
          #Increment current frame counter (taking into account framerate)
          #print("Ticks:",self.ticks,"Framerate:",self.framerate, "CurrentFrame:",self.currentframe)
          if (self.currentframe <= (self.frames)):
            self.currentframe = self.currentframe + 1
          if (self.currentframe > (self.frames)):
            self.currentframe = 1
        time.sleep(delay)
          
  def HorizontalFlip(self):
    #print ("CAS - Horizontalflip width heigh frames",self.width, self.height,self.frames)
    for f in range(1,self.frames+1):
      x = 0
      y = 0
      cells = (self.width * self.height)

      flipgrid = []
      #print ("Frame: ",f)
      #print ("cells: ",cells)
      for count in range (0,cells):
        y,x = divmod(count,self.width)
       #print("y,x = divmod(",count,self.width,"): ",y,x)
        #print ("cell to flip: ",((y*self.width)+ self.width-x-1), "value: ",self.grid[f][((y*self.width)+ self.width-x-1)])
        
        flipgrid.append(self.grid[f][((y*self.width)+ self.width-x-1)])  

      #print("Original:", str(self.grid[f]))
      #print("Flipped :", str(flipgrid))
      self.grid[f] = flipgrid      
    #print ("Done Flipping")
    
       
  
  def ScrollAcrossScreen(self,h,v,direction,ScrollSleep):
    #hv seem a little messed up, investigate what their original purpose was and fix
    if (direction == "right"):
      self.ScrollWithFrames((0- self.width),v,"right",(HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.ScrollWithFrames(HatWidth-1,v,"left",(HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.ScrollWithFrames(h,HatWidth-1,"left",(HatWidth + self.height),ScrollSleep)



  def Float(self,h,v,direction,moves,delay):
    #print("CAS - Scroll -   HV Direction moves Delay", h,v,direction,moves,delay)
    x = 0
    oldh = 0
    r = 0
    g = 0
    b = 0
    
    #Capture Background
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("CAS - Scroll - Direction: ",direction)  
      
      for count in range (0,moves):
        #print ("CAS - Scroll - currentframe: ",self.currentframe)
        if (self.currentframe < (self.frames-1)):
          self.currentframe = self.currentframe + 1
        else:
          self.currentframe = 1
        h = h + (modifier)
        if count >= 1:
          oldh = h - modifier

        #draw new sprite
        setpixels(Buffer)
          
        self.DisplayNoBlack(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(delay)



  def FloatAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Float((0- self.width),v,"right",(HatWidth + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Float(HatWidth-1,v,"left",(HatWidth + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Float(h,HatWidth-1,"left",(HatWidth + self.height),ScrollSleep)


  def Animate(self,h,v,direction,delay):
   #print("CAS - Animate - HV delay ",h,v,delay,)
    x = 0,
    y = 0,
    Buffer = copy.deepcopy(unicorn.get_pixels())
    
    if (direction == 'forward'):
      for f in range (0,self.frames):
        #erase old sprite
        #setpixels(Buffer)
        #draw new sprite
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)

        #Increment current frame counter
        if (self.currentframe < (self.frames-1)):
          self.currentframe = self.currentframe + 1
        else:
          self.currentframe = 1
          
        time.sleep(delay)
        

    else:  
      for f in range (0,self.frames+1):
        #erase old sprite
        #setpixels(Buffer)
        setpixels(Buffer)
        #draw new sprite
        #print ("CAS - Animate - currentframe: ",self.currentframe)
        self.Display(h,v)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)

        #Increment current frame counter
        if (self.currentframe <= (self.frames-1)):
          self.currentframe = self.currentframe -1
        else:
          self.currentframe = self.frames
          
        #time.sleep(delay)
      

  #Draw the sprite using an affect like in the movie Tron 
  def LaserScan(self,h1,v1,speed=0.005):
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    #print ("CAS - LaserScan -")
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h1),y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          if (r > 0 or g > 0 or b > 0):
            FlashDot4((x+h1),y+v1,speed)
            TheMatrix.SetPixel((x+h1),y+v1,r,g,b)

            TheMatrix.SwapOnVSync(Canvas)




  def LaserErase(self,h1,v1,speed=0.005):
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    #print ("CAS - LaserErase -")
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h1),y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          if (r > 0 or g > 0 or b > 0):
            FlashDot4((x+h1),y+v1,speed)
            TheMatrix.SetPixel((x+h1),y+v1,0,0,0)
      #unicorn.show() 
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)



    #unicorn.show() 

  def CopyAnimatedSpriteToPlayfield(self,Playfield, TheObject):
    #Copy an animated sprite to the Playfield. 
    #Animated can have different shapes per frame
    #Each spot on the playfield will contain a reference to the objecttype e.g. a ship

    width   = self.width 
    height  = self.height
    h       = TheObject.h - (width // 2)
    v       = TheObject.v - (height // 2)
    frame   = self.currentframe
  
    #Copy sprite to playfield
    for count in range (0,(width * height)):
      y,x = divmod(count,width)

      if(self.grid[frame][count] >= 0):
        if (CheckBoundary((x+h),y+v) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          if (r > -1 and g > -1 and b > -1):
              Playfield[y+v][x+h] = TheObject
              #TheMatrix.SetPixel(x+h1,y+v1,r,g,b)
          else:
              Playfield[y+v][x+h] = EmptyObject('EmptyObject')
              TheMatrix.SetPixel(x+h1,y+v1,r,g,b)

           
    return Playfield;







#------------------------------------------------------------------------------
# Network Display Classes                                                    --
#------------------------------------------------------------------------------

# class PixelSimDisplay():
  # #Created by Kareem Sultan - Dec 2020
  # def __init__(self, url, display_name, on_attach=None, on_detach=None):
    # self.url = url
    # self.display_name = display_name
    # self.on_attach = on_attach
    # self.on_detach = on_detach
    # #we don't send packet if it is duplicate of previous
    # self.PreviousPacketString = ""
    # self.PacketString = ""

    # #self.on_message = on_message

# #    try:
    # print("Defining connection:",self.display_name)
    # self.hub_connection = HubConnectionBuilder()\
        # .with_url(url, options={"verify_ssl":True, "access_token_factory":lambda: "dummytoken"})\
        # .configure_logging(logging.DEBUG)\
        # .with_automatic_reconnect({
            # "type": "raw",
            # "keep_alive_interval": 10,
            # "reconnect_interval": 5,
            # "max_attempts": 5
        # })\
        # .build()

    # print("--connection on--")
    # self.hub_connection.on("recieveMessage", print)
    # print("--connection on_open--")
    # self.hub_connection.on_open(self.on_connect)
    # print("--connection on_close--")
    # self.hub_connection.on_close(lambda: print("connection closed"))
    # print("---")

    # # except Exception as ErrorMessage:
      # # TheTrace = traceback.format_exc()
      # # print("")
      # # print("")
      # # print("--------------------------------------------------------------")
      # # print("ERROR - Defining hub_connection")
      # # print(ErrorMessage)
      # # print("")
      # # #print("EXCEPTION")
      # # #print(sys.exc_info())
      # # print("")
      # # print ("TRACE")
      # # print (TheTrace)
      # # print("--------------------------------------------------------------")
      # # print("")
      # # print("")
      

  # def on_display_attached(self):
    # print("--Display attached--")
      

  # def on_connect(self):

      # print ("--on_connect start--")
    # #try:
      # print("---------------------------------------------------------------")
      # print("connection opened and handshake received ready to send messages")
      # self.hub_connection.send("AttachDisplay: ", [self.display_name])
      
      # if self.on_attach is not None and callable(self.on_attach):
              # print ("--calling on_attach--")
      # self.on_attach(self)
      # print("---------------------------------------------------------------")
      # print("--on_connect end--")



    # # except Exception as ErrorMessage:
      # # TheTrace = traceback.format_exc()
      # # print("")
      # # print("")
      # # print("--------------------------------------------------------------")
      # # print("ERROR - on_connect")
      # # print(ErrorMessage)
      # # print("")
      # # #print("EXCEPTION")
      # # #print(sys.exc_info())
      # # print("")
      # # print ("TRACE")
      # # print (TheTrace)
      # # print("--------------------------------------------------------------")
      # # print("")
      # # print("")
      # # time.sleep(5)
      
      
  # def connect(self):
    # try:
      # self.hub_connection.start()  
    
    # except Exception as ErrorMessage:
      # TheTrace = traceback.format_exc()
      # print("")
      # print("")
      # print("--------------------------------------------------------------")
      # print("ERROR - Connect")
      # print(ErrorMessage)
      # print("")
      # #print("EXCEPTION")
      # #print(sys.exc_info())
      # print("")
      # print ("TRACE")
      # print (TheTrace)
      # print("--------------------------------------------------------------")
      # print("")
      # print("")
      # time.sleep(5)

  
  # def disconnect(self):
    # try:
      # self.hub_connection.stop()
    # except Exception as ErrorMessage:
      # TheTrace = traceback.format_exc()
      # print("")
      # print("")
      # print("--------------------------------------------------------------")
      # print("ERROR - disconnect")
      # print(ErrorMessage)
      # print("")
      # #print("EXCEPTION")
      # #print(sys.exc_info())
      # print("")
      # print ("TRACE")
      # print (TheTrace)
      # print("--------------------------------------------------------------")
      # print("")
      # print("")
      # time.sleep(5)
  
  # def update(self):
    # #print ("PixelArray:",)
    # try:
      # print ("Sending message")  
      # self.hub_connection.send("sendMessage", [self.PacketString])
    # except Exception as ErrorMessage:
      # TheTrace = traceback.format_exc()
      # print("")
      # print("")
      # print("--------------------------------------------------------------")
      # print("ERROR - update")
      # print(ErrorMessage)
      # print("")
      # #print("EXCEPTION")
      # #print(sys.exc_info())
      # print("")
      # print ("TRACE")
      # print (TheTrace)
      # print("--------------------------------------------------------------")
      # print("")
      # print("")
      # time.sleep(5)


  # #Send the message/packet
  # def SendPacket(self):
    
    # print ("Inputstring:",self.PacketString)
    # #print ("PrevString: ",self.PreviousPacketString[1:16])
    
    
    # try:
      
      # if (self.PreviousPacketString != self.PacketString ):
        # startTime = time.time()
        # #r = requests.post(url = self.URLEndpoint, data = PacketString, timeout=0.3) 
        # #r = self.TheSession.post(url = self.URLEndpoint, data = PacketString, timeout=self.timeout) 
        # self.update()
        # self.PreviousPacketString = self.PacketString
        # endTime = time.time()
        # totalTimeTaken = str(float(round((endTime - startTime ),3)))
        # print ("ElapsedTime:",totalTimeTaken)


      # else:
        # print ("--skip frame--")

        # #print ("PacketString:",self.PacketString[1:16])
        # #print ("PrevString:  ",self.PreviousPacketString[1:16])

    # except Exception as ErrorMessage:
      # TheTrace = traceback.format_exc()
      # print("")
      # print("")
      # print("--------------------------------------------------------------")
      # print("ERROR")
      # print(ErrorMessage)
      # print("")
      # #print("EXCEPTION")
      # #print(sys.exc_info())
      # print("")
      # print ("TRACE")
      # print (TheTrace)
      # print("--------------------------------------------------------------")
      # print("")
      # print("")
      # time.sleep(5)



  # #The HTTPDisplay object can capture the current Unicorn buffer and send that as a packet
  # def SendBufferPacket(self,width,height):
    # self.PacketString = ""
    # x = 0
    # y = 0
    # rgb = (0,0,0)
    # HatWidth  = width
    # HatHeight = height
    # UnicornBuffer = unicorn.get_pixels()
   
    # ints = []
   
    # for x in range(0,HatHeight):
      # for y in range(0,HatWidth):
        # r,g,b = UnicornBuffer[x][y]
        # self.PacketString = self.PacketString + '#%02x%02x%02x' % (r,g,b) + ","
        # #self.PacketString = self.PacketString + str(r) + "," + str(g) + "," + str(b) + ","
        # #ints.append(UnicornBuffer[x][y])
    # #pixel_string = ','.join(map(str, ints))

    
    # self.PacketString = self.PacketString[:-1]
    # #print (pixel_string)
    # #print (string)
    # #self.SendPacket([pixel_string])
    # #print ("PixelString ",self.PacketString[1:8])
    # self.SendPacket()
    # #self.SendPacket([string])
    # return;
  


#------------------------------------------------------------------------------
# Drawing Sprite Classes                                                     --
#------------------------------------------------------------------------------



class TextMap(object):
  #A text map is a series of same length strings that are used to visually layout a map
  def __init__(self, h,v, width, height):
    self.h         = h
    self.v         = v
    self.width     = width
    self.height    = height
    self.ColorList = {}
    self.TypeList  = {}
    self.map       = []


  def CopyMapToColorSprite(self,TheSprite,Frame=0):
    mapchar = ""
    dottype = ""
    NumDots = 0
    SpriteFrame = []

    #read the map string and process one character at a time
    #decode the color and type of dot to place
    #print ("Height:",self.height)
    for y in range (0,self.height):
      #print ("map[",y,"] =",self.map[y])
      for x in range (0,self.width):
        mapchar = self.map[y][x]
        TheColor =  self.ColorList.get(mapchar)
        dottype  =  self.TypeList.get(mapchar)
        SpriteFrame.append(TheColor)
    TheSprite.grid.append(SpriteFrame)
    TheSprite.frames = TheSprite.frames + 1


    

    








#------------------------------------------------------------------------------
# SPRITES                                                                    --
#------------------------------------------------------------------------------




DigitList = []
#0
DigitList.append([1,1,1, 
                  1,0,1,
                  1,0,1,
                  1,0,1,
                  1,1,1])
#1
DigitList.append([0,0,1, 
                  0,0,1,
                  0,0,1,
                  0,0,1,
                  0,0,1])
#2
DigitList.append([1,1,1, 
                  0,0,1,
                  1,1,1,
                  1,0,0,
                  1,1,1])
#3
DigitList.append([1,1,1, 
                  0,0,1,
                  0,1,1,
                  0,0,1,
                  1,1,1])
#4
DigitList.append([1,0,1, 
                  1,0,1,
                  1,1,1,
                  0,0,1,
                  0,0,1])
               
#5  
DigitList.append([1,1,1, 
                  1,0,0,
                  1,1,1,
                  0,0,1,
                  1,1,1])
#6
DigitList.append([1,1,1, 
                  1,0,0,
                  1,1,1,
                  1,0,1,
                  1,1,1])
#7
DigitList.append([1,1,1, 
                  0,0,1,
                  0,1,0,
                  1,0,0,
                  1,0,0])
#8  
DigitList.append([1,1,1, 
                  1,0,1,
                  1,1,1,
                  1,0,1,
                  1,1,1])
#9  
DigitList.append([1,1,1, 
                  1,0,1,
                  1,1,1,
                  0,0,1,
                  0,0,1])
                    

# List of Digit Number Numeric sprites
DigitSpriteList = [Sprite(3,5,RedR,RedG,RedB,DigitList[i]) for i in range(0,10)]


AlphaList = []
#A
AlphaList.append([0,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0])

#B
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0])
#c
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,0,
                  1,0,0,0,0,
                  1,0,0,0,0,
                  0,1,1,1,0])

#D
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,1,1,0,0])

#E
AlphaList.append([1,1,1,1,0,
                  1,0,0,0,0,
                  1,1,1,0,0,
                  1,0,0,0,0,
                  1,1,1,1,0])
                  
#F
AlphaList.append([1,1,1,1,0,
                  1,0,0,0,0,
                  1,1,1,0,0,
                  1,0,0,0,0,
                  1,0,0,0,0])

#G
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,0,
                  1,0,1,1,0,
                  1,0,0,1,0,
                  0,1,1,1,0])

#H
AlphaList.append([1,0,0,1,0,
                  1,0,0,1,0,
                  1,1,1,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0])
#I
AlphaList.append([0,1,1,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,1,1,1,0])
#J
AlphaList.append([0,1,1,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  1,0,1,0,0,
                  0,1,0,0,0])
                  
#K
AlphaList.append([1,0,0,1,0,
                  1,0,1,0,0,
                  1,1,0,0,0,
                  1,0,1,0,0,
                  1,0,0,1,0])
#L
AlphaList.append([0,1,0,0,0,
                  0,1,0,0,0,
                  0,1,0,0,0,
                  0,1,0,0,0,
                  0,1,1,1,0])

#M
AlphaList.append([1,0,0,0,1,
                  1,1,0,1,1,
                  1,0,1,0,1,
                  1,0,0,0,1,
                  1,0,0,0,1])

#N
AlphaList.append([1,0,0,0,1,
                  1,1,0,0,1,
                  1,0,1,0,1,
                  1,0,0,1,1,
                  1,0,0,0,1])
#O
AlphaList.append([0,1,1,0,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  0,1,1,0,0])
#P
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0,
                  1,0,0,0,0,
                  1,0,0,0,0])
#Q
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,1,
                  1,0,0,0,1,
                  1,0,0,1,0,
                  0,1,1,0,1])
#R 
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0,
                  1,0,1,0,0,
                  1,0,0,1,0])
#S
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,0,
                  0,1,1,0,0,
                  0,0,0,1,0,
                  1,1,1,0,0])
#T
AlphaList.append([0,1,1,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0])
#U
AlphaList.append([1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  0,1,1,0,0])
#V
AlphaList.append([1,0,0,0,1,
                  1,0,0,0,1,
                  0,1,0,1,0,
                  0,1,0,1,0,
                  0,0,1,0,0])
#W
AlphaList.append([1,0,0,0,1,
                  1,0,0,0,1,
                  1,0,1,0,1,
                  0,1,0,1,0,
                  0,1,0,1,0])
#X
AlphaList.append([1,0,0,0,1,
                  0,1,0,1,0,
                  0,0,1,0,0,
                  0,1,0,1,0,
                  1,0,0,0,1])
#Y
AlphaList.append([0,1,0,1,0,
                  0,1,0,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0])
#Z
AlphaList.append([1,1,1,1,0,
                  0,0,0,1,0,
                  0,0,1,0,0,
                  0,1,0,0,0,
                  1,1,1,1,0])


                  
                  
# List of Alpha sprites
AlphaSpriteList = [Sprite(5,5,RedR,RedG,RedB,AlphaList[i]) for i in range(0,26)]



                  
                  
#space                  
SpaceSprite = Sprite(
  3,
  5,
  0,
  0,
  0,
  [0,0,0,
   0,0,0,
   0,0,0,
   0,0,0,
   0,0,0]
)

#Exclamation
ExclamationSprite = Sprite(
  3,
  5,
  0,
  0,
  0,
  [0,1,0,
   0,1,0,
   0,1,0,
   0,0,0,
   0,1,0]
)

#Period
PeriodSprite = Sprite(
  2,
  5,
  0,
  0,
  0,
  [0,0,
   0,0,
   0,0,
   0,0,
   0,1]
)




#QuestionMark
QuestionMarkSprite = Sprite(
  5,
  5,
  0,
  0,
  0,
  [0,0,1,1,0,
   0,0,0,1,0,
   0,0,1,1,0,
   0,0,0,0,0,
   0,0,1,0,0]
)


#PoundSignSprite
PoundSignSprite = Sprite(
  5,
  5,
  0,
  0,
  0,
  [0,1,0,1,0,
   1,1,1,1,1,
   0,1,0,1,0,
   1,1,1,1,1,
   0,1,0,1,0]
)



 
ColonSprite = Sprite(
  3,
  5,
  RedR,
  RedG,
  RedB,
  [0,0,0,
   0,1,0,
   0,0,0,
   0,1,0,
   0,0,0]
)



DashSprite = Sprite(
  3,
  5,
  RedR,
  RedG,
  RedB,
  [0,0,0,0,
   0,0,0,0,
   0,1,1,0,
   0,0,0,0,
   0,0,0,0]
)


#$
DollarSignSprite = Sprite(
  4,
  5,
  RedR,
  RedG,
  RedB,
  [0,1,1,1,
   1,0,1,0,
   0,1,1,0,
   0,0,1,1,
   1,1,1,0]
)


#------------------------------------------------------------------------------
# CUSTOM SPRITES                                                             --
#   These sprites come from various video games in the Arcade Retro Clock.   --
#   They were created for an 8x8 display but work quite well on any size.    --
#   Animated sprites have frames of animations that are displayed as the     --
#   sprite moves.                                                            --
#                                                                            --
#   Note:                                                                    --
#   These sprites are "drawn" with a lot of imagination but are stored as    --
#   a list of integers.  This is a technique I created back in the 80's      --
#   while programming my TRS-80 color computer, and certainly WAY before     --
#   I had a firm grasp on Python arrays/lists/tuples and all that jazz.      --
#------------------------------------------------------------------------------








PacSprite = Sprite(
  6,
  5,
  YellowR,
  YellowG,
  YellowB,
  [0,0,1,1,1,0,
   0,1,1,1,0,0,
   0,1,1,0,0,0,
   0,1,1,1,0,0,
   0,0,1,1,1,0]
)


RedGhostSprite = Sprite(
  5,
  5,
  RedR,
  RedG,
  RedB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)
    

OrangeGhostSprite = Sprite(
  5,
  5,
  OrangeR,
  OrangeG,
  OrangeB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)
    
BlueGhostSprite = Sprite(
  5,
  5,
  BlueR,
  BlueG,
  BlueB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)

PurpleGhostSprite = Sprite(
  5,
  5,
  PurpleR,
  PurpleG,
  PurpleB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)



ChickenRunning = ColorAnimatedSprite(h=0, v=0, name="Chicken", width=8, height=8, frames=4,framerate=1,grid=[])
ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0,22, 0,21, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)

ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)

ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0,21, 0,22, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)


ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)







WormChasingChicken = ColorAnimatedSprite(h=0, v=0, name="Chicken", width=24, height=8, frames=4,framerate=1,grid=[])
WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17,17, 0, 0, 0, 0,
    0, 0, 0,22, 0,21, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17,17, 0, 0, 0, 0,

  ]
)

WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17, 0, 0,17,17, 0, 0, 0, 0,

  ]
)

WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0,17,17, 0, 0, 0, 0,
    0, 0, 0,21, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0,17,17, 0, 0, 0, 0

  ]
)


WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17, 0, 0,17,17, 0, 0, 0, 0

  ]
)












ChickenChasingWorm = ColorAnimatedSprite(h=0, v=0, name="Chicken", width=16, height=8, frames=4,framerate=1,grid=[])
ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    5,17, 5,17,17, 0, 0, 0, 0, 0, 0,22, 0,21, 0, 0

  ]
)

ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    0, 5,17, 0,17, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0

  ]
)

ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    5,17, 5,17,17, 0, 0, 0, 0, 0, 0,21, 0,22, 0, 0

  ]
)


ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    0, 5,17, 0,17, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0

  ]
)




ThreeGhostPacSprite = ColorAnimatedSprite(h=0, v=0, name="ThreeGhost", width=26, height=5, frames=5, framerate=1,grid=[])



ThreeGhostPacSprite.grid.append(
  [
   0, 0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0,22,22,22, 0, 0,
   0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 22,22,22, 0,0, 0,
   0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 22,22, 0, 0,0, 0,
   0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 22,22,22, 0,0, 0,
   0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,22,22,22, 0, 0
  
   ]
)


ThreeGhostPacSprite.grid.append(
  [
     0,0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0,22,22,22,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 22,22,22,22,22, 0,
    0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 22,22,22,0,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 22,22,22,22,22, 0,
    0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,22,22,22,0, 0
  
   ]
)



ThreeGhostPacSprite.grid.append(
  [
    0, 0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0,23,23,23,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,23,23,23, 0,
    0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 23,23,23,23,23, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,23,23,23, 0,
    0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,23,23,23,0, 0
  
   ]
)



ThreeGhostPacSprite.grid.append(
  [
    0,0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0,  0,23,23,23,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,23,23,0, 0,
    0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 23,23,23,0,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,23,23,0,  0,
    0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,23,23,23,0, 0
  
   ]
)

 
ThreeGhostPacSprite.grid.append(
  [
     0,0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 0, 0,23,23,23,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,0,0,0, 0,
    0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 0, 23,23,0,0,0, 0,
    0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 0, 23,23,0,0,0, 0,
    0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0, 0, 0,23,23,23,0, 0
  
   ]
)




ThreeBlueGhostPacSprite = ColorAnimatedSprite(h=0, v=0, name="ThreeGhost", width=26, height=5, frames=6, framerate=1,grid=[])

ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,23,23,23, 0,
    0,14, 2,14, 1,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,23,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,23,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)


ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 23,23,23,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,23,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 23,23,23,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)



ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 23,23,23,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 23,23,23,23,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 23,23,23,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)

ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,23,23,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,23,23,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,23,23,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)

 
ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,0,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0, 0
  
   ]
)

ThreeBlueGhostPacSprite.grid.append(
  [
     0,0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,23,23,23,0, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,23,23, 0,
    0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,0,23, 0,
    0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,23,23, 0,
    0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,23,23,23,0,  0
  
   ]
)






ThreeGhostSprite = ColorAnimatedSprite(h=0, v=0, name="ThreeGhost", width=19, height=5, frames=1, framerate=1,grid=[])
ThreeGhostSprite.grid.append(
  [
   0, 0,33,33,33, 0, 0, 0,18,18,18, 0, 0, 0, 7, 7, 7, 0, 0, 
   0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 
   0,33, 1,33, 1,33, 0,18, 1,18, 1,18, 0, 7, 1, 7, 1, 7, 0, 
   0,33,33,33,33,33, 0,18,18,18,18,18, 0, 7, 7, 7, 7, 7, 0, 
   0,33, 0,33, 0,33, 0,18, 0,18, 0,18, 0, 7, 0, 7, 0, 7, 0 
  
   ]
)


ThreeBlueGhostSprite = ColorAnimatedSprite(h=0, v=0, name="ThreeBlueGhost", width=19, height=5, frames=1, framerate=1,grid=[])
ThreeBlueGhostSprite.grid.append(
  [
   0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 
   0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 
   0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 
   0,14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 
   0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0 
  
   ]
)




PacDotAnimatedSprite = AnimatedSprite(5,5,YellowR,YellowG,YellowB,4,[])
PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,0,0,
   1,1,0,0,0,
   1,1,1,0,0,
   0,1,1,1,0]
)

PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,1,1,
   1,1,0,0,0,
   1,1,1,1,1,
   0,1,1,1,0]
)


PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,1,1,
   1,1,1,1,1,
   1,1,1,1,1,
   0,1,1,1,0]
)
PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,1,0,
   1,1,1,0,0,
   1,1,1,1,0,
   0,1,1,1,0]
)

PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,0,0,0,
   1,0,0,0,0,
   1,1,0,0,0,
   0,1,1,1,0]
)


# Make left and right facing pacmen
PacRightAnimatedSprite = copy.deepcopy(PacDotAnimatedSprite)
PacLeftAnimatedSprite  = copy.deepcopy(PacDotAnimatedSprite)
PacLeftAnimatedSprite.HorizontalFlip()




DotZerkRobot = ColorAnimatedSprite(h=0, v=0, name="Robot", width=10, height=8, frames=9, framerate=1,grid=[])
DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 8, 1, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)
DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 1, 8, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)
DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 1, 8, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)
DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 6, 1, 8, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)


DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 6, 1, 8, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)

DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 6, 8, 1, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)


DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 8, 1, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)


DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 8, 1, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0

  ]
)

DotZerkRobot.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6, 8, 1, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 0, 6, 6, 0, 0,

  ]
)




DotZerkRobotWalking = ColorAnimatedSprite(h=0, v=0, name="Robot", width=10, height=8, frames=2, framerate=1,grid=[])
DotZerkRobotWalking.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6,14,14, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 0, 0, 6, 0, 0, 0,
    0, 0, 6, 6, 0, 6, 6, 0, 0, 0,

  ]
)
DotZerkRobotWalking.grid.append(
  [
    0, 0, 0, 6, 6, 6, 6, 0, 0, 0,
    0, 0, 6,14,14, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 6, 6, 6, 6, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 6, 0, 6, 6, 6, 6, 0, 6, 0,
    0, 0, 0, 0, 6, 6, 0, 0, 0, 0,
    0, 0, 0, 0, 6, 6, 0, 0, 0, 0,
    0, 0, 0, 6, 6, 6, 0, 0, 0, 0

  ]
)


DotZerkRobotWalkingSmall = ColorAnimatedSprite(h=0, v=0, name="Robot", width=9, height=5, frames=4, framerate=1,grid=[])
DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0, 0,10,10,10,10, 0, 0,
   0, 0,10, 7, 7,10,10,10, 0,
   0, 0,10,10,10,10,10,10, 0,
   0, 0,10, 0, 0, 0, 0,10, 0,
   0, 10,10, 0, 0, 0,10,10, 0

  ]
)
DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0, 0,10,10,10,10, 0, 0,
   0, 0,10, 7, 7,10,10,10, 0,
   0, 0,10,10,10,10,10,10, 0,
   0, 0, 0,10, 0, 0,10, 0, 0,
   0, 0,10,10, 0,10,10, 0, 0,

  ]
)

DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0, 0,10,10,10,10, 0, 0,
   0, 0,10, 7, 7,10,10,10, 0,
   0, 0,10,10,10,10,10,10, 0,
   0, 0, 0, 0,10,10, 0, 0, 0,
   0, 0, 0,10,10,10, 0, 0, 0,

  ]
)
DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0, 0,10,10,10,10, 0, 0,
   0, 0,10, 7, 7,10,10,10, 0,
   0, 0,10,10,10,10,10,10, 0,
   0, 0, 0,10, 0, 0,10, 0, 0,
   0, 0,10,10, 0,10,10, 0, 0,

  ]
)





RunningManSprite = ColorAnimatedSprite(
  h=0, 
  v=0, 
  name="RunningMan", 
  width  = 25, 
  height = 18, 
  frames = 0, 
  framerate=2,
  grid=[]  )

                 

RunningManSpriteMap = TextMap(
  h      = 1,
  v      = 1,
  width  = 25, 
  height = 18
  )

RunningManSpriteMap.ColorList = {
  ' ' : 0,
  '-' : 1,
  '.' : 2,
  'o' : 15,  # Med Blue
  'O' : 4,  
  'r' : 5,
  'R' : 8,
  'b' : 12,
  'B' : 13,
  '#' : 27
}

RunningManSpriteMap.TypeList = {
  ' ' : 'Empty',
  '-' : 'wall',
  '.' : 'wall',
  'o' : 'wall',
  'O' : 'wall'
}



RunningManSpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "      oooooooo           ", 
  "    oooooooo             ", 
  "    oo  oooo    oo       ", 
  "    oo  oooooooo         ", 
  "                         ", 
  "        oooo             ", 
  "        oooo             ", 
  "      oooooooooooo       ", 
  "      oo        oo       ", 
  "    oooo      oo         ", 
  "    oo        oo         ", 
  "  oooo                   ", 
  "  oo                     ", 
  "  oo                     ", 
  "                         ", 

  )
      
RunningManSpriteMap.CopyMapToColorSprite(TheSprite=RunningManSprite)


RunningManSpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "  oooooooooooo           ", 
  "  oo    oooo             ", 
  "  oo    oooooooooo       ", 
  "        oooo             ", 
  "                         ", 
  "        oooo             ", 
  "        oooo             ", 
  "      oooooooooooo       ", 
  "      oo        oo       ", 
  "    oooo        oo       ", 
  "    oo          oo       ", 
  "  oooo                   ", 
  "  oo                     ", 
  "                         ", 
  "                         ", 
  )

RunningManSpriteMap.CopyMapToColorSprite(TheSprite=RunningManSprite)


RunningManSpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "      oooooooo           ", 
  "    oooooooo             ", 
  "    oo  oooooooooo       ", 
  "    oo  oooo             ", 
  "                         ", 
  "        oooo             ", 
  "        oooo             ", 
  "      oooooooo           ", 
  "      oo    oo           ", 
  "    oooo    oooo         ", 
  "  oooo        oo         ", 
  "  oo          oo         ", 
  "              oooo       ", 
  "                         ", 
  "                         ", 
  )

RunningManSpriteMap.CopyMapToColorSprite(TheSprite=RunningManSprite)


RunningManSpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "    oooooooo             ", 
  "    oo  oooooo           ", 
  "    oo  oooo  oo         ", 
  "                         ", 
  "        oooo             ", 
  "      oooooo             ", 
  "      oooooooo           ", 
  "      oo    oo           ", 
  "  oooooo    oo           ", 
  "  oo        oo           ", 
  "  oo        oo           ", 
  "            oooo         ", 
  "                         ", 
  "                         ", 
  )

RunningManSpriteMap.CopyMapToColorSprite(TheSprite=RunningManSprite)


RunningManSpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "      oooooooooo         ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "    oooooooo             ", 
  "    oo    oo             ", 
  "    oo    oo             ", 
  "          oooo           ", 
  "                         ", 
  "                         ", 
  )

RunningManSpriteMap.CopyMapToColorSprite(TheSprite=RunningManSprite)


RunningManSpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "    oooooooo             ", 
  "    oo  oo               ", 
  "    oo  oo               ", 
  "        oooo             ", 
  "                         ", 
  "                         ", 
  )

RunningManSpriteMap.CopyMapToColorSprite(TheSprite=RunningManSprite)



RunningManSpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "      oooooooo           ", 
  "      oooooooo           ", 
  "      oooooooooo         ", 
  "        oooo             ", 
  "        oooooo           ", 
  "      oooooooooo         ", 
  "      oo      oo         ", 
  "      oo  oooooo         ", 
  "      oo  oo             ", 
  "      oo                 ", 
  "        oo               ", 
  "                         ", 
  "                         ", 
  )

RunningManSpriteMap.CopyMapToColorSprite(TheSprite=RunningManSprite)




RunningManSpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "    oooooooo             ", 
  "    oo  oooooooo         ", 
  "    oo                   ", 
  "        oooo             ", 
  "        oooooo           ", 
  "      oooooooooooo       ", 
  "      oo        oo       ", 
  "      oo    oooooo       ", 
  "    oo      oo           ", 
  "    oo                   ", 
  "    oo                   ", 
  "                         ", 
  "                         ", 
  )

RunningManSpriteMap.CopyMapToColorSprite(TheSprite=RunningManSprite)






RunningMan2Sprite = ColorAnimatedSprite(
  h=0, 
  v=0, 
  name="RunningMan", 
  width  = 25, 
  height = 18, 
  frames = 0, 
  framerate=2,
  grid=[]  )

                 

RunningMan2SpriteMap = TextMap(
  h      = 1,
  v      = 1,
  width  = 25, 
  height = 18
  )

RunningMan2SpriteMap.ColorList = {
  ' ' : 0,
  '-' : 17, # Dark orange
  '.' : 19, # Med  orange
  'o' : 6,  # Low  Red
  'O' : 7,  # Med  Red
  'r' : 5,
  'R' : 8,
  'b' : 12,
  'B' : 13,
  '#' : 27
}

RunningMan2SpriteMap.TypeList = {
  ' ' : 'Empty',
  '-' : 'wall',
  '.' : 'wall',
  'o' : 'wall',
  'O' : 'wall'
}



RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "      oooooooo           ", 
  "    oooooooo             ", 
  "    oo  oooo    OO       ", 
  "    oo  oooooooo         ", 
  "                         ", 
  "        oooo             ", 
  "        oooo             ", 
  "      oooooooooooo       ", 
  "      oo        oo       ", 
  "    oooo      oo         ", 
  "    oo        --         ", 
  "  oooo                   ", 
  "  .o                     ", 
  "  .o                     ", 
  "                         ", 

  )
      
RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "  oooooooooooo           ", 
  "  oo    oooo             ", 
  "  oo    ooooooooOO       ", 
  "        oooo             ", 
  "                         ", 
  "        oooo             ", 
  "        oooo             ", 
  "      oooooooooooo       ", 
  "      oo        oo       ", 
  "    oooo        oo       ", 
  "    oo          --       ", 
  "  .ooo                   ", 
  "  .o                     ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "      oooooooo           ", 
  "    oooooooo             ", 
  "    oo  ooooooOO         ", 
  "    oo  oooo             ", 
  "                         ", 
  "        oooo             ", 
  "        oooo             ", 
  "      oooooooo           ", 
  "      oo    oo           ", 
  "    oooo    oooo         ", 
  "  .ooo        oo         ", 
  "  .o          oo         ", 
  "              ----       ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "    oooooooo             ", 
  "    oo  oooooo           ", 
  "    oo  oooo  OO         ", 
  "                         ", 
  "        oooo             ", 
  "      oooooo             ", 
  "      oooooooo           ", 
  "      oo    oo           ", 
  "  .ooooo    oo           ", 
  "  .o        oo           ", 
  "  .o        oo           ", 
  "            ----         ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "      ooooooOO           ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "    .ooooooo             ", 
  "    .o    oo             ", 
  "    .o    oo             ", 
  "          ----           ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "      ooooOO             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "    .ooooooo             ", 
  "    .o  oo               ", 
  "    .o  oo               ", 
  "        ----             ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)



RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "      oooooooo           ", 
  "      oooooooo           ", 
  "      ooOOoooooo         ", 
  "        oooo             ", 
  "        oooooo           ", 
  "      oooooooooo         ", 
  "      oo      oo         ", 
  "      oo  .ooooo         ", 
  "      oo  .o             ", 
  "      oo                 ", 
  "        --               ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)




RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "    oooooooo             ", 
  "    oo  oooooooo         ", 
  "    OO                   ", 
  "        oooo             ", 
  "        oooooo           ", 
  "      oooooooooooo       ", 
  "      oo        oo       ", 
  "      oo    .ooooo       ", 
  "    -o      .o           ", 
  "    -o                   ", 
  "    -o                   ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)



RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "      oooooooo           ", 
  "    oooooooo             ", 
  "    oo  oooo    oo       ", 
  "    OO  oooooooo         ", 
  "                         ", 
  "        oooo             ", 
  "        oooo             ", 
  "      oooooooooooo       ", 
  "      oo        oo       ", 
  "    oooo      .o         ", 
  "    oo        .o         ", 
  "  -ooo                   ", 
  "  -o                     ", 
  "  -o                     ", 
  "                         ", 

  )
      
RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "  oooooooooooo           ", 
  "  oo    oooo             ", 
  "  OO    oooooooooo       ", 
  "        oooo             ", 
  "                         ", 
  "        oooo             ", 
  "        oooo             ", 
  "      oooooooooooo       ", 
  "      oo        oo       ", 
  "    oooo        oo       ", 
  "    oo          ..       ", 
  "  -ooo                   ", 
  "  -o                     ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "      oooooooo           ", 
  "    oooooooo             ", 
  "    oo  oooooooo         ", 
  "    OO  oooo             ", 
  "                         ", 
  "        oooo             ", 
  "        oooo             ", 
  "      oooooooo           ", 
  "      oo    oo           ", 
  "    oooo    oooo         ", 
  "  -ooo        oo         ", 
  "  -o          oo         ", 
  "              ....       ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "    oooooooo             ", 
  "    oo  oooooo           ", 
  "    OO  oooo  oo         ", 
  "                         ", 
  "        oooo             ", 
  "      oooooo             ", 
  "      oooooooo           ", 
  "      oo    oo           ", 
  "  -ooooo    oo           ", 
  "  -o        oo           ", 
  "  -o        oo           ", 
  "            ....         ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "      ooOOoooo           ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "    -ooooooo             ", 
  "    -o    oo             ", 
  "    -o    oo             ", 
  "          ....           ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)


RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "      oooooo             ", 
  "      ooooOO             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "        oooo             ", 
  "    -ooooooo             ", 
  "    -o  oo               ", 
  "    -o  oo               ", 
  "        ....             ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)



RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "      oooooooo           ", 
  "      oooooooo           ", 
  "      ooooooooOO         ", 
  "        oooo             ", 
  "        oooooo           ", 
  "      oooooooooo         ", 
  "      oo      oo         ", 
  "      oo  -ooooo         ", 
  "      oo  -o             ", 
  "      oo                 ", 
  "        ..               ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)




RunningMan2SpriteMap.map= (
  #0.........1.........2.....
  "                         ", 
  "          oooo           ", 
  "          oo             ", 
  "        oooooo           ", 
  "      oooooo             ", 
  "    oooooooo             ", 
  "    oo  ooooooOO         ", 
  "    oo                   ", 
  "        oooo             ", 
  "        oooooo           ", 
  "      oooooooooooo       ", 
  "      oo        oo       ", 
  "      oo    -ooooo       ", 
  "    oo      -o           ", 
  "    oo                   ", 
  "    oo                   ", 
  "                         ", 
  "                         ", 
  )

RunningMan2SpriteMap.CopyMapToColorSprite(TheSprite=RunningMan2Sprite)








BigSpiderLegOutSprite = ColorAnimatedSprite(
  h=0, 
  v=0, 
  name="Spider", 
  width  = 40, 
  height = 11, 
  frames = 0, 
  framerate=2,
  grid=[]  )

                

BigSpiderLegOutSpriteMap = TextMap(
  h      = 1,
  v      = 1,
  width  = 40, 
  height = 11
  )

BigSpiderLegOutSpriteMap.ColorList = {
  ' ' : 0,
  '.' : 1,
  '-' : 2,
  'o' : 3,  
  'O' : 4,  
  '*' : 8,
  '#' : 14,
  'b' : 15,
  'B' : 16

}

BigSpiderLegOutSpriteMap.TypeList = {
  ' ' : 'Empty',
  'O' : 'wall'
}


BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3
  "                                        ",
  "      ..    ......    ..                ", 
  "     .--.  .------.  .--.               ", 
  "    .-  -..-o*oo*o-..-  -.              ", 
  "   .-    -.-oOOOOo-.-    -.             ", 
  "   .-     .-oooooo-.     -.             ", 
  "   .-      .------.      -.             ", 
  "   .-       ......       -.             ", 
  "   .-                    -.             ", 
  "   .-                    -.             ", 
  "                                        ", 
  )

BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)


BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3
  "                     ..                 ", 
  "      ..    ......  .--.                ", 
  "     .--.  .------. .--.                ", 
  "    .-  -..-o*oo*o-..- -.               ", 
  "   .-    -.-oOOOOo-.-  -.               ", 
  "   .-     .-oooooo-.   -.               ", 
  "   .-      .------.    -.               ", 
  "   .-       ......     -.               ", 
  "   .-                  -.               ", 
  "   .-                                   ", 
  "                                        ",
  )

BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)


BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3
  "                     ...                ", 
  "      ..    ......  .---.               ", 
  "     .--.  .------. .-  -.              ", 
  "    .-  -..-o*oo*o-..-  -.              ", 
  "   .-    -.-oOOOOo-.-   -.              ", 
  "   .-     .-oooooo-.    -.              ", 
  "   .-      .------.     -.              ", 
  "   .-       ......      -.              ", 
  "   .-                                   ", 
  "   .-                                   ", 
  "                                        ", 
   )


BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)


BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3
  "                     .....              ", 
  "      ..    ......  .-----.             ", 
  "     .--.  .------. .-    -.            ", 
  "    .-  -..-o*oo*o-..-    -.            ", 
  "   .-    -.-oOOOOo-.-     -.            ", 
  "   .-     .-oooooo-.      -.            ", 
  "   .-      .------.                     ", 
  "   .-       ......                      ", 
  "   .-                                   ", 
  "   .-                                   ", 
  "                                        ", 
   )


BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)



BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                         ",
  "                          .....          ",
  "        ..    ......     .-----.         ",
  "       .--.  .------.   .-     -.        ",
  "      .-  -..-o*oo*o-. .-      -.        ",
  "     .-    -.-oOOOOo-.-        -.        ",
  "    .-      .-oooooo-.         -.        ",
  "   .-        .------.                    ",
  "   .-         ......                     ",
  "   .-                                    ",
  "                                         ",
  "                                         ",
   )
BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)




BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                         ",
  "                                         ",
  "                                         ",
  "                  ......     ........    ",
  "         .....   .------.   .-------.    ",
  "        .-----...-o*oo*o-. .-        -.  ",
  "       .-     --.-oOOOOo-.-           -. ",
  "      .-        .-oooooo-.            -. ",
  "    .-           .------.                ",
  "   .-             ......                 ",
  "                                         ",
   )
BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)


BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                           ",
  "                                           ",
  "                                           ",
  "                   ......                  ",
  "                  .------.                 ",
  "         .........-o*oo*o-..........       ",
  "        .--------.-oOOOOo-.----------.     ",
  "      .-         .-oooooo-.          -.    ",
  "    .-            .------.            -.   ",
  "   .-              ......              -.  ",
  "                                            ",
   )
BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)


BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                         ",
  "                                         ",
  "                                         ",
  "                  ......     ........    ",
  "         .....   .------.   .-------.    ",
  "        .-----...-o*oo*o-. .-        -.  ",
  "       .-     --.-oOOOOo-.-           -. ",
  "      .-        .-oooooo-.            -. ",
  "    .-           .------.                ",
  "   .-             ......                 ",
  "                                         ",
   )
BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)


BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                         ",
  "                          .....          ",
  "        ..    ......     .-----.         ",
  "       .--.  .------.   .-     -.        ",
  "      .-  -..-o*oo*o-. .-      -.        ",
  "     .-    -.-oOOOOo-.-        -.        ",
  "    .-      .-oooooo-.         -.        ",
  "   .-        .------.                    ",
  "   .-         ......                     ",
  "   .-                                    ",
  "                                         ",
  "                                         ",
   )
BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)


BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3
  "                     .....              ", 
  "      ..    ......  .-----.             ", 
  "     .--.  .------. .-    -.            ", 
  "    .-  -..-o*oo*o-..-    -.            ", 
  "   .-    -.-oOOOOo-.-     -.            ", 
  "   .-     .-oooooo-.      -.            ", 
  "   .-      .------.                     ", 
  "   .-       ......                      ", 
  "   .-                                   ", 
  "   .-                                   ", 
  "                                        ", 
   )


BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)




BigSpiderLegOutSpriteMap.map= (
  #0.........1.........2.........3
  "                     ...                ", 
  "      ..    ......  .---.               ", 
  "     .--.  .------. .-  -.              ", 
  "    .-  -..-o*oo*o-..-  -.              ", 
  "   .-    -.-oOOOOo-.-   -.              ", 
  "   .-     .-oooooo-.    -.              ", 
  "   .-      .------.     -.              ", 
  "   .-       ......      -.              ", 
  "   .-                                   ", 
  "   .-                                   ", 
  "                                        ", 
   )


BigSpiderLegOutSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderLegOutSprite)







#----------------------------
# Big Spider Walking       --
#----------------------------


BigSpiderWalkingSprite = ColorAnimatedSprite(
  h=0, 
  v=0, 
  name="Spider", 
  width  = 40, 
  height = 11, 
  frames = 0, 
  framerate=1,
  grid=[]  )

                

BigSpiderWalkingSpriteMap = TextMap(
  h      = 1,
  v      = 1,
  width  = 40, 
  height = 11
  )

BigSpiderWalkingSpriteMap.ColorList = {
  ' ' : 0,
  '.' : 1,
  '-' : 2,
  'o' : 3,  
  'O' : 4,  
  '*' : 8,
  '#' : 14,
  'b' : 15,
  'B' : 16

}

BigSpiderWalkingSpriteMap.TypeList = {
  ' ' : 'Empty',
  'O' : 'wall'
}


BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3
  "                                        ",
  "      ..    ......    ..                ", 
  "     .--.  .------.  .--.               ", 
  "    .-  -..-o*oo*o-..-  -.              ", 
  "   .-    -.-oOOOOo-.-    -.             ", 
  "   .-     .-oooooo-.     -.             ", 
  "   .-      .------.      -.             ", 
  "   .-       ......       -.             ", 
  "   .-                    -.             ", 
  "   .-                    -.             ", 
  "                                        ", 
  )

BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)


BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3
  "                     ..                 ", 
  "      ..    ......  .--.                ", 
  "     .--.  .------. .--.                ", 
  "    .-  -..-o*oo*o-..- -.               ", 
  "   .-    -.-oOOOOo-.-  -.               ", 
  "   .-     .-oooooo-.   -.               ", 
  "   .-      .------.    -.               ", 
  "   .-       ......     -.               ", 
  "   .-                  -.               ", 
  "   .-                                   ", 
  "                                        ",
  )

BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)


BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3
  "                     ...                ", 
  "      ..    ......  .---.               ", 
  "     .--.  .------. .-  -.              ", 
  "    .-  -..-o*oo*o-..-  -.              ", 
  "   .-    -.-oOOOOo-.-   -.              ", 
  "   .-     .-oooooo-.    -.              ", 
  "   .-      .------.     -.              ", 
  "   .-       ......      -.              ", 
  "   .-                                   ", 
  "   .-                                   ", 
  "                                        ", 
   )


BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)


BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3
  "                     .....              ", 
  "      ..    ......  .-----.             ", 
  "     .--.  .------. .-    -.            ", 
  "    .-  -..-o*oo*o-..-    -.            ", 
  "   .-    -.-oOOOOo-.-     -.            ", 
  "   .-     .-oooooo-.      -.            ", 
  "   .-      .------.                     ", 
  "   .-       ......                      ", 
  "   .-                                   ", 
  "   .-                                   ", 
  "                                        ", 
   )


BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)



BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                         ",
  "                          .....          ",
  "        ..    ......     .-----.         ",
  "       .--.  .------.   .-     -.        ",
  "      .-  -..-o*oo*o-. .-      -.        ",
  "     .-    -.-oOOOOo-.-        -.        ",
  "    .-      .-oooooo-.         -.        ",
  "   .-        .------.                    ",
  "   .-         ......                     ",
  "   .-                                    ",
  "                                         ",
  "                                         ",
   )
BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)




BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                         ",
  "                                         ",
  "                                         ",
  "                  ......     ........    ",
  "         .....   .------.   .-------.    ",
  "        .-----...-o*oo*o-. .-        -.  ",
  "       .-     --.-oOOOOo-.-           -. ",
  "      .-        .-oooooo-.            -. ",
  "    .-           .------.                ",
  "   .-             ......                 ",
  "                                         ",
   )
BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)


BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                           ",
  "                                           ",
  "                                           ",
  "                   ......                  ",
  "                  .------.                 ",
  "         .........-o*oo*o-..........       ",
  "        .--------.-oOOOOo-.----------.     ",
  "      .-         .-oooooo-.          -.    ",
  "    .-            .------.            -.   ",
  "   .-              ......              -.  ",
  "                                           ",
   )
BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)





BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                            ",
  "                                            ",  
  "                                            ",  
  "       ........     ......                  ",  
  "       .-------.   .------.   .....         ",  
  "     .-        -. .-o*oo*o-...-----.        ",  
  "    .-           -.-oOOOOo-.--     -.       ",  
  "    .-            .-oooooo-.        -.      ",  
  "                   .------.           -.    ",  
  "                    ......             -.   ",  
  "                                           ",  
)
BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)


BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3.........4
  "                                            ",
  "             .....                          ",  
  "            .-----.     ......    ..        ",  
  "           .-     -.   .------.  .--.       ",  
  "           .-      -. .-o*oo*o-..-  -.      ",  
  "           .-        -.-oOOOOo-.-    -.     ",  
  "           .-         .-oooooo-.      -.    ",  
  "                       .------.        -.   ",  
  "                        ......         -.   ",  
  "                                       -.   ",  
  "                                            ",  
  "                                            ",  
  )
BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)


BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3
  "                  .....                     ",
  "                 .-----.  ......    ..      ",  
  "                .-    -. .------.  .--.     ",  
  "                .-    -..-o*oo*o-..-  -.    ",  
  "                .-     -.-oOOOOo-.-    -.   ",  
  "                .-      .-oooooo-.     -.   ",  
  "                         .------.      -.   ",  
  "                          ......       -.   ",  
  "                                       -.   ",  
  "                                       -.   ",  
  "                                            ",  
   )


BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)


BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3
  "                    ...                     ",
  "                   .---.  ......    ..      ",  
  "                  .-  -. .------.  .--.     ",  
  "                  .-  -..-o*oo*o-..-  -.    ",  
  "                  .-   -.-oOOOOo-.-    -.   ",  
  "                  .-    .-oooooo-.     -.   ",  
  "                  .-     .------.      -.   ",  
  "                  .-      ......       -.   ",  
  "                                       -.   ",  
  "                                       -.   ",  
  "                                            ",  
 )

BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)




BigSpiderWalkingSpriteMap.map= (
  #0.........1.........2.........3
  "                     ..                     ",
  "                    .--.  ......    ..      " , 
  "                     .--. .------.  .--.    ",
  "                    .- -..-o*oo*o-..-  -.   ",
  "                   .-  -.-oOOOOo-.-    -.   ",  
  "                   .-   .-oooooo-.     -.   ",  
  "                   .-    .------.      -.   ",  
  "                   .-     ......       -.   ",  
  "                   .-                  -.   ",  
  "                                       -.   ",  
  "                                            " ,
   )
BigSpiderWalkingSpriteMap.CopyMapToColorSprite(TheSprite=BigSpiderWalkingSprite)


#------------------------------------------------------------------------------
# FUNCTIONS                                                                  --
#                                                                            --
#  These functions were created before classes were introduced.              --
#------------------------------------------------------------------------------



  
def ScrollSprite2(Sprite,h,v,direction,moves,r,g,b,delay):
  x = 0
  #modifier is used to increment or decrement the location
  if direction == "right" or direction == "down":
    modifier = 1
  else: 
    modifier = -1
  
  if direction == "left" or direction == "right":
    for count in range (0,moves):
      h = h + (modifier)
      #erase old sprite
      if count >= 1:
        DisplaySprite(Sprite,Sprite.width,Sprite.height,h-(modifier),v,0,0,0)
      #draw new sprite
      DisplaySprite(Sprite,Sprite.width,Sprite.height,h,v,r,g,b)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      time.sleep(delay)
  
  return;

 
  

def ScrollSprite(Sprite,width,height,Direction,startH,startV,stopH,stopV,r,g,b,delay):
  x = 0
  h = startH
  v = startV
  movesH = abs(startH - stopH)
  movesV = abs(startV - stopV)

  #modifier is used to increment or decrement the location
  if Direction == "right" or Direction == "down":
    modifier = 1
  else: 
    modifier = -1
  
  if Direction == "left" or Direction == "right":
    for count in range (0,movesH):
      #print ("StartH StartV StopH StopV X",startH,startV,stopH,stopV,x)
      h = h + (modifier)
      #erase old sprite
      if count >= 1:
        DisplaySprite(Sprite,width,height,h-(modifier),v,0,0,0)
      #draw new sprite
      DisplaySprite(Sprite,width,height,h,v,r,g,b)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      time.sleep(delay)
  
  return;
    
def DisplaySprite(Sprite,width,height,h,v,r,g,b):
  x = 0,
  y = 0
  
  for count in range (0,(width * height)):
    y,x = divmod(count,width)
    #print("Count:",count,"xy",x,y)
    if Sprite[count] == 1:
      if (CheckBoundary(x+h,y+v) == 0):
        TheMatrix.SetPixel(x+h,y+v,r,g,b)
  return;    



def TrimSprite(Sprite1):
  height       = Sprite1.height
  width        = Sprite1.width
  newwidth     = 0
  elements     = height * width
  Empty        = 1
  Skipped      = 0
  EmptyColumns = []
  EmptyCount   = 0
  BufferX      = 0
  BufferColumn = [(0) for i in range(height)]
  
  i = 0
  x = 0
  y = 0

  
  for x in range (0,width):
    
    #Find empty columns, add them to a list
    Empty = 1  
    for y in range (0,height):
      i = x + (y * width)
      
      BufferColumn[y] = Sprite1.grid[i]
      if (Sprite1.grid[i] != 0):
        Empty = 0
    
    if (Empty == 0):
      newwidth =  newwidth + 1
    
    elif (Empty == 1):
      #print ("Found empty column: ",x)
      EmptyColumns.append(x)
      EmptyCount = EmptyCount +1

      
  BufferSprite = Sprite(
    newwidth,
    height,
    Sprite1.r,
    Sprite1.g,
    Sprite1.b,
    [0]*(newwidth*height)
    )
      
  #Now that we identified the empty columns, copy data and skip those columns
  for x in range (0,width):
    Skipped = 0
    
    for y in range (0,height):
      i = x + (y * width)
      b = BufferX + (y * newwidth)
      if (x in EmptyColumns):
        Skipped = 1
      else:
        BufferSprite.grid[b] = Sprite1.grid[i]
    
    
    #advance our Buffer column counter only if we skipped a column
    if (Skipped == 0):
      BufferX = BufferX + 1
    
    
  
  BufferSprite.width = newwidth
  
  
  
  #print (BufferSprite.grid)
  return BufferSprite



def LeftTrimSprite(Sprite1,Columns):
  height       = Sprite1.height
  width        = Sprite1.width
  newwidth     = 0
  elements     = height * width
  Empty        = 1
  Skipped      = 0
  EmptyColumns = []
  EmptyCount   = 0
  BufferX      = 0
  BufferColumn = [(0) for i in range(height)]
  
  i = 0
  x = 0
  y = 0

  
  for x in range (0,width):
    
    #Find empty columns, add them to a list
    Empty = 1  
    for y in range (0,height):
      i = x + (y * width)
      
      BufferColumn[y] = Sprite1.grid[i]
      if (Sprite1.grid[i] != 0):
        Empty = 0
    
    if (Empty == 0 or EmptyCount > Columns):
      newwidth =  newwidth + 1
    
    elif (Empty == 1):
      #print ("Found empty column: ",x)
      EmptyColumns.append(x)
      EmptyCount = EmptyCount +1

      
  BufferSprite = Sprite(
    newwidth,
    height,
    Sprite1.r,
    Sprite1.g,
    Sprite1.b,
    [0]*(newwidth*height)
    )
      
  #Now that we identified the empty columns, copy data and skip those columns
  for x in range (0,width):
    Skipped = 0
    
    for y in range (0,height):
      i = x + (y * width)
      b = BufferX + (y * newwidth)
      if (x in EmptyColumns):
        Skipped = 1
      else:
        BufferSprite.grid[b] = Sprite1.grid[i]
    
    
    #advance our Buffer column counter only if we skipped a column
    if (Skipped == 0):
      BufferX = BufferX + 1
    
    
  
  BufferSprite.width = newwidth
  
  
  
  #print (BufferSprite.grid)
  return BufferSprite
    
    
    
    

  
  
def CreateShortWordSprite(ShortWord):   

  ShortWord = ShortWord.upper()
  TheBanner = CreateBannerSprite(ShortWord)
      

  TheBanner.r = SDMedRedR
  TheBanner.g = SDMedRedG
  TheBanner.b = SDMedRedB
  
  
  #add variables to the object (python allows this, very cool!)
  TheBanner.h = (HatWidth - TheBanner.width) / 2
  TheBanner.v = -4
  TheBanner.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)

  #used for displaying clock
  TheBanner.StartTime = time.time()

  #used for scrolling clock
  TheBanner.PauseStartTime = time.time()
  TheBanner.IsScrolling     = 0
  TheBanner.Delay           = 2
  TheBanner.PausePositionV  = 1
  TheBanner.PauseTimerOn    = 0
  
  TheBanner.on = 1
  TheBanner.DirectionIncrement = 1

  
  return TheBanner 



def ShowShortMessage(RaceWorld,PlayerCar,ShortMessage):
  moves = 1
  ShortMessageSprite    = CreateShortMessageSprite(ShortMessage)
  ShortMessageSprite.on = 1
  while (ShortMessageSprite.on == 1):
    RaceWorld.DisplayWindowWithSprite(PlayerCar.h-7,PlayerCar.v-7,ShortMessageSprite)
    MoveMessageSprite(moves,ShortMessageSprite)
    moves = moves + 1
    #print ("Message On")
    
  ShortMessageSprite.on = 0












def DrawDigit(Digit,h,v,r,g,b):
  #print ("Digit:",Digit)
  x = h
  y = v,
  width = 3
  height = 5  

  if Digit == 0:
    Sprite = ([1,1,1, 
               1,0,1,
               1,0,1,
               1,0,1,
               1,1,1])

  elif Digit == 1:
    Sprite = ([0,0,1, 
               0,0,1,
               0,0,1,
               0,0,1,
               0,0,1])

  elif Digit == 2:
    Sprite = ([1,1,1, 
               0,0,1,
               0,1,0,
               1,0,0,
               1,1,1])

  elif Digit == 3:
    Sprite = ([1,1,1, 
               0,0,1,
               0,1,1,
               0,0,1,
               1,1,1])

  elif Digit == 4:
    Sprite = ([1,0,1, 
               1,0,1,
               1,1,1,
               0,0,1,
               0,0,1])
               
  
  elif Digit == 5:
    Sprite = ([1,1,1, 
               1,0,0,
               1,1,1,
               0,0,1,
               1,1,1])

  elif Digit == 6:
    Sprite = ([1,1,1, 
               1,0,0,
               1,1,1,
               1,0,1,
               1,1,1])

  elif Digit == 7:
    Sprite = ([1,1,1, 
               0,0,1,
               0,1,0,
               1,0,0,
               1,0,0])
  
  elif Digit == 8:
    Sprite = ([1,1,1, 
               1,0,1,
               1,1,1,
               1,0,1,
               1,1,1])
  
  elif Digit == 9:
    Sprite = ([1,1,1, 
               1,0,1,
               1,1,1,
               0,0,1,
               0,0,1])
  

  DisplaySprite(Sprite,width,height,h,v,r,g,b)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  return;  





   

def CheckBoundaries(h,v,Direction):
  if v < 0:
    v = 0
    Direction = TurnRight(Direction)
  elif v > HatHeight-1:
    v = HatHeight-1
    Direction = TurnRight(Direction)
  elif h < 0:
    h = 0
    Direction = TurnRight(Direction)
  elif h > HatWidth-1:
    h = HatWidth-1
    Direction = TurnRight(Direction)
  return h,v,Direction

  
  
def CheckBoundary(h,v):
  BoundaryHit = 0
  if v < 0 or v > HatHeight-1 or h < 0 or h > HatWidth-1:
    BoundaryHit = 1
  return BoundaryHit;








  






def ShowDigitalClock(h,v,duration):
  Buffer = copy.deepcopy(unicorn.get_pixels())
  ClockSprite = CreateClockSprite(12)
  ClockSprite.r = SDLowRedR
  ClockSprite.g = SDLowRedG
  ClockSprite.b = SDLowRedB
  ClockSpriteBackground.DisplayIncludeBlack(h-2,v-1)
  ClockSprite.Display(h,v)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  time.sleep(duration)
  setpixels(Buffer)
  return;



def random_message(MessageFile):
  lines = open(MessageFile).read().splitlines()
  return random.choice(lines)

    


def SaveConfigData():
  
  
   
  print (" ")
  print ("--Save Config Data--")
  #we save the time to file as 5 minutes in future, which allows us to unplug the device temporarily
  #the time might be off, but it might be good enough
  
  AdjustedTime = (datetime.now() + timedelta(minutes=5)).strftime('%k:%M:%S')

  
  if (os.path.exists(ConfigFileName)):
    print ("Config file (",ConfigFileName,"): already exists")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)
  else:
    print ("Config file not found.  Creating new one.")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)
    ConfigFile.add_section('main')
    ConfigFile.add_section('pacdot')
    ConfigFile.add_section('crypto')

    
  print ("Time to save: ",AdjustedTime)
  print ("Pacdot score:      " ,PacDotScore)
  print ("Pacdot high score: " ,PacDotHighScore)
  print ("Pacdot games played:",PacDotGamesPlayed)
  print ("Crypto balance:    " ,CryptoBalance)

  ConfigFile.set('main',   'CurrentTime',       AdjustedTime)
  ConfigFile.set('pacdot', 'PacDotHighScore',   str(PacDotHighScore))
  ConfigFile.set('pacdot', 'PacDotGamesPlayed', str(PacDotGamesPlayed))
  ConfigFile.set('crypto', 'balance',           str(CryptoBalance))


  print ("Writing configuration file")
  with open(ConfigFileName, 'w') as f:
    ConfigFile.write(f)
  print ("--------------------")



    
def LoadConfigData():
  

  print ("--Load Config Data--")
  print ("PacDotHighScore Before Load: ",PacDotHighScore)
    
  if (os.path.exists(ConfigFileName)):
    print ("Config file (",ConfigFileName,"): already exists")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)

    #Get and set time    
    TheTime = ConfigFile.get("main","currenttime")
    print ("Setting time: ",TheTime)
    CMD = "sudo date --set " + TheTime
    #os.system(CMD)
   
    #Get pacdot data
    PacDotHighScore   = ConfigFile.get("pacdot","PacdotHighScore")
    PacDotGamesPlayed = int(ConfigFile.get("pacdot","PacdotGamesPlayed"))
    print ("PacDotHighScore: ",  PacDotHighScore)
    print ("PacDotGamesPlayed: ",PacDotGamesPlayed)

    #Get CryptoBalance
    CryptoBalance = ConfigFile.get("crypto","balance")
    print ("CryptoBalance:   ",CryptoBalance)

    
  else:
    print ("Config file not found! Running with default values.")

    
  print ("--------------------")
  print (" ")
  


 
  
    
  
  
  
  
def SetTimeHHMM():
  DigitsEntered = 0
  H1  = 0
  H2  = 0
  M1  = 0
  M2  = 0
  Key = -1

  CustomH = ([1,0,1,
              1,0,1,
              1,1,1,
              1,0,1,
              1,0,1])

  CustomM = ([1,0,1,
              1,1,1,
              1,1,1,
              1,0,1,
              1,0,1])

  QuestionMarkSprite = Sprite(
  3,
  5,
  0,
  0,
  0,
  [0,1,1,
   0,0,1,
   0,1,1,
   0,0,0,
   0,1,0]
  )

              
              
  CustomHSprite = Sprite(3,5,SDLowRedR,SDLowRedG,SDLowRedB,CustomH)
  CustomMSprite = Sprite(3,5,SDLowRedR,SDLowRedG,SDLowRedB,CustomM)
  AMSprite      = Sprite(5,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,AlphaSpriteList[0].grid)
  PMSprite      = Sprite(5,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,AlphaSpriteList[15].grid)
  AMPMSprite    = JoinSprite(QuestionMarkSprite,CustomMSprite,1)
  




 
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  ScrollScreen('up',ScreenCap,ScrollSleep)
  ShowScrollingBanner("set time: hours minutes",100,100,0,ScrollSleep)
  ScrollScreen('down',ScreenCap,ScrollSleep)

  
  HHSprite = TrimSprite(CustomHSprite)
  HHSprite = JoinSprite (HHSprite,TrimSprite(CustomHSprite),1)
  
  HHSprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  
  #Get first hour digit
  while (Key != 0 and Key != 1):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  H1 = Key
  
  #Convert user input H1 to a sprite
  #x = ord(H1) -48
  
  UserH1Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[H1].grid)
  CustomHSprite.Erase(1,1)
  UserH1Sprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  
  #Get second hour digit (special conditions to make sure we keep 12 hour time)
  Key = -1
  while ((H1 == 1 and (Key != 0 and Key != 1 and Key != 2))
     or (H1 == 0 and (Key == -1)) ):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  H2 = Key
 
  #Convert user input H2 to a sprite
  UserH2Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[H2].grid)
  CustomHSprite.Erase(5,1)
  UserH2Sprite.Display(5,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
    
  #print ("HH: ",H1,H2)
  

  
  
  
  #Get minutes
  time.sleep(1)
  TheMatrix.Clear()

  
  MMSprite = TrimSprite(CustomMSprite)
  MMSprite = JoinSprite (MMSprite,TrimSprite(CustomMSprite),1)
  
  MMSprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  
  #Get first minute digit
  Key = -1
  while (Key < 0 or Key >= 6):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  M1 = Key
  
  #Convert user input M1 to a sprite
  UserM1Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[M1].grid)
  CustomMSprite.Erase(1,1)
  UserM1Sprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  
  #Get second hour digit
  Key = -1
  while (Key == -1):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  M2 = Key
 
  #Convert user input M2 to a sprite
  UserM2Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[M2].grid)
  CustomMSprite.Erase(5,1)
  UserM2Sprite.Display(5,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
    
  #print ("MM: ",M1,M2)
  
  time.sleep(1)
  TheMatrix.Clear()

  # a.m / p.m.
  ShowScrollingBanner("AM or PM",100,100,0,ScrollSleep * 0.65)
  AMPMSprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  #Get A or P
  KeyChar = ''
  while (KeyChar == '' or (KeyChar != 'A' and KeyChar != 'a' and KeyChar != 'P' and KeyChar != 'p' )):
    KeyChar = PollKeyboardRegular()
    time.sleep(0.15)

  AMPMSprite.r = SDLowGreenR
  AMPMSprite.g = SDLowGreenG
  AMPMSprite.b = SDLowGreenB
  AMPMSprite.Display(1,1)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  
  QuestionMarkSprite.Erase(1,1)

  AMPM = ''
  if (KeyChar == 'a' or KeyChar == 'A'):
    AMSprite.Display(0,1)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
    AMPM  = 'am'
    
  elif (KeyChar == 'p' or KeyChar == 'P'):
    PMSprite.Display(0,1)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
    AMPM = 'pm'
    
  
  #print ("KeyChar ampm:",KeyChar, AMPM)    
  time.sleep(1)
 
  
  
  
  #set system time
  NewTime = str(H1) + str(H2) + ":" + str(M1) + str(M2) + AMPM
  CMD = "sudo date --set " + NewTime
  os.system(CMD)
  
  TheMatrix.Clear()
  ScrollScreenShowClock('down',ScrollSleep)         
  








def ShowScrollingBanner(TheMessage,r,g,b,ScrollSpeed):
  TheMessage = TheMessage.upper()
  TheBanner = CreateBannerSprite(TheMessage)
  TheBanner.r = r 
  TheBanner.g = g 
  TheBanner.b = b 
  TheBanner.ScrollAcrossScreen(HatWidth-1,4,"left",ScrollSpeed)


def ShowScrollingBanner2(TheMessage,rgb,ScrollSpeed,v=5):
  r,g,b = rgb
  TheMessage = TheMessage.upper()
  TheBanner = CreateBannerSprite(TheMessage)
  TheBanner.r = r 
  TheBanner.g = g 
  TheBanner.b = b 
  TheBanner.ScrollAcrossScreen(HatWidth-1,v,"left",ScrollSpeed)

def ShowFloatingBanner(TheMessage,rgb,ScrollSpeed,v=5):
  r,g,b = rgb
  TheMessage = TheMessage.upper()
  TheBanner = CreateBannerSprite(TheMessage)
  TheBanner.r = r 
  TheBanner.g = g 
  TheBanner.b = b 
  TheBanner.FloatAcrossScreen(HatWidth-1,v,"left",ScrollSpeed)












  
def FlashDot(h,v,FlashSleep):
  r,g,b = getpixel(h,v)
  TheMatrix.SetPixel(h,v,0,0,255)
  time.sleep(FlashSleep)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  TheMatrix.SetPixel(h,v,r,g,b)
  time.sleep(FlashSleep)
  #unicorn.show()
  TheMatrix.SetPixel(h,v,0,255,0)
  time.sleep(FlashSleep)
  #unicorn.show()
  TheMatrix.SetPixel(h,v,r,g,b)
  time.sleep(FlashSleep)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  return;

def FlashDot2(h,v,FlashSleep):
  r,g,b = getpixel(h,v)
  TheMatrix.SetPixel(h,v,100,100,0)
  TheMatrix.SetPixel(h,v,200,200,0)
  TheMatrix.SetPixel(h,v,255,255,255)
  time.sleep(FlashSleep)
  TheMatrix.SetPixel(h,v,r,g,b)

  return;


  
def FlashDot3(h,v,r,g,b,FlashSleep):
 
    
  LowR = int(r * 0.75)
  LowG = int(g * 0.75)
  LowB = int(b * 0.75)
  HighR = int(r * 1.5)
  HighG = int(g * 1.5)
  HighB = int(b * 1.5)
  
  if (LowR < 0 ):
    LowR = 0
  if (LowG < 0 ):
    LowG = 0
  if (LowB < 0 ):
    LowBB = 0
  
  
  if (HighR > 255):
    HighR = 255
  if (HighG > 255):
    HighG = 255
  if (HighB > 255):
    HighB = 255
    
  TheMatrix.SetPixel(h,v,HighR,HighG,HighB)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  time.sleep(FlashSleep)
  TheMatrix.SetPixel(h,v,r,g,b)
  #unicorn.show()
  TheMatrix.SetPixel(h,v,LowR,LowG,LowB)
  #unicorn.show()
  time.sleep(FlashSleep)
  #unicorn.show()
  TheMatrix.SetPixel(h,v,HighR,HighG,HighB)
  #unicorn.show()
  time.sleep(FlashSleep)
  TheMatrix.SetPixel(h,v,r,g,b)
  #unicorn.show()
  TheMatrix.SetPixel(h,v,LowR,LowG,LowB)
  #unicorn.show()
  time.sleep(FlashSleep)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  
  
def FlashDot4(h,v,FlashSleep):
  r,g,b = getpixel(h,v)
  #TheMatrix.SetPixel(h,v,0,0,100)
  #unicorn.show()
  #time.sleep(FlashSleep)
  #TheMatrix.SetPixel(h,v,0,0,175)
  #unicorn.show()
  time.sleep(FlashSleep)
  TheMatrix.SetPixel(h,v,0,0,255)
  #unicorn.show()
  time.sleep(FlashSleep)
  TheMatrix.SetPixel(h,v,0,255,255)
  #unicorn.show()
  time.sleep(FlashSleep)
  TheMatrix.SetPixel(h,v,255,255,255)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  time.sleep(FlashSleep)
  TheMatrix.SetPixel(h,v,r,g,b)
  #unicorn.show()
  time.sleep(FlashSleep)
  return;
  

def FlashDot5(h,v,TimeSleep):
  #r,g,b = getpixel(h,v)
  
  #There is not get pixel function in rpi-rgb-led
  r,g,b = (255,255,255)

  setpixel(h,v,255,255,255)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  time.sleep(TimeSleep)
  setpixel(h,v,r,g,b)
  
  
  return;


def FlashDot6(h,v):
  r,g,b = getpixel(h,v)
  TheMatrix.SetPixel(h,v,255,255,255)
  #unicorn.show()
  #TheMatrix.SetPixel(h,v,r,g,b)
  return;


def FlashDot7(h,v):
  TheMatrix.SetPixel(h,v,255,150,0)
  #unicorn.show()
  TheMatrix.SetPixel(h,v,0,0,0)
  return;



  

  



def CreateClockSprite(format):   
  #print ("CreateClockSprite")
  #Create the time as HHMMSS
  
  if (format == 12 or format == 2):  
    hhmmss = datetime.now().strftime('%I:%M:%S')
    hh,mm,ss = hhmmss.split(':')
  
  if format == 24:  
    hhmmss = datetime.now().strftime('%H:%M:%S')
    hh,mm,ss = hhmmss.split(':')
  
   

  
  #get hour digits
  h1 = int(hh[0])
  h2 = int(hh[1])
  #get minute digits
  m1 = int(mm[0])
  m2 = int(mm[1])


  #For 12 hour format, we don't want to display leading zero 
  #for tiny clock (2) format we only get hours
  if ((format == 12 or format == 2) and h1 == 0):
    ClockSprite = DigitSpriteList[h2]
  else:
    ClockSprite = JoinSprite(DigitSpriteList[h1], DigitSpriteList[h2], 1)
  
  if (format == 12 or format == 24):
    ClockSprite = JoinSprite(ClockSprite, ColonSprite, 0)
    ClockSprite = JoinSprite(ClockSprite, DigitSpriteList[m1], 0)
    ClockSprite = JoinSprite(ClockSprite, DigitSpriteList[m2], 1)
    

  ClockSprite.r = SDMedRedR
  ClockSprite.g = SDMedRedG
  ClockSprite.b = SDMedRedB
  
  
  #add variables to the object (python allows this, very cool!)
  ClockSprite.h = (HatWidth - ClockSprite.width) // 2
  ClockSprite.v = -4
  ClockSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)

  #used for displaying clock
  ClockSprite.StartTime = time.time()

  #used for scrolling clock
  ClockSprite.PauseStartTime = time.time()
  ClockSprite.IsScrolling     = 0
  ClockSprite.Delay           = 2
  ClockSprite.PausePositionV  = 1
  ClockSprite.PauseTimerOn    = 0

  
  ClockSprite.on = 1
  ClockSprite.DirectionIncrement = 1

  ClockSprite.name = 'Clock'
  
  return ClockSprite 





def CreateSecondsSprite():   
  
  hhmmss = datetime.now().strftime('%I:%M:%S')
  hh,mm,ss = hhmmss.split(':')
 
  #get seconds digits
  s1 = int(ss[0])
  s2 = int(ss[1])

  SecondsSprite = JoinSprite(DigitSpriteList[s1], DigitSpriteList[s2], 1)
  
  SecondsSprite.r = SDDarkOrangeR
  SecondsSprite.g = SDDarkOrangeG
  SecondsSprite.b = SDDarkOrangeB
  
  
  #add variables to the object (python allows this, very cool!)
  SecondsSprite.h = (HatWidth - SecondsSprite.width) // 2
  SecondsSprite.v = 5
  SecondsSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
  
  return SecondsSprite 



def CreateDayOfWeekSprite():   
  
  weekdaynum = datetime.today().weekday()
  dow        = ""
 
  if (weekdaynum   == 0 ):
    dow = "MON"
  elif (weekdaynum == 1 ):
    dow = "TUE"
  elif (weekdaynum == 2 ):
    dow = "WED"
  elif (weekdaynum == 3 ):
    dow = "THU"
  elif (weekdaynum == 4 ):
    dow = "FRI"
  elif (weekdaynum == 5 ):
    dow = "SAT"
  elif (weekdaynum == 6 ):
    dow = "SUN"


  DowSprite = LeftTrimSprite(CreateBannerSprite(dow),1)  
  
  DowSprite.r = SDMedOrangeR
  DowSprite.g = SDMedOrangeG
  DowSprite.b = SDMedOrangeB
  
  
  #add variables to the object (python allows this, very cool!)
  DowSprite.h = ((HatWidth - DowSprite.width) // 2) -1
  DowSprite.v = 5
  DowSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
  
  return DowSprite



def CreateMonthSprite():   
  
  ShortMonth = (datetime.now()).strftime('%b').upper()
  print ("Month:",ShortMonth)
  

  MonthSprite = LeftTrimSprite(CreateBannerSprite(ShortMonth),1)
  
  MonthSprite.r = SDMedBlueR
  MonthSprite.g = SDMedBlueG
  MonthSprite.b = SDMedBlueB
  
  
  #add variables to the object (python allows this, very cool!)
  MonthSprite.h = ((HatWidth - MonthSprite.width) // 2) -1
  MonthSprite.v = 5
  MonthSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
  
  return MonthSprite



def CreateDayOfMonthSprite():   
  
  DayOfMonth = str((datetime.now()).day)
  print ("Month:",DayOfMonth)
  

  DayOfMonthSprite = LeftTrimSprite(CreateBannerSprite(DayOfMonth),1)
  
  DayOfMonthSprite.r = SDMedBlueR
  DayOfMonthSprite.g = SDMedBlueG
  DayOfMonthSprite.b = SDMedBlueB
  
  
  #add variables to the object (python allows this, very cool!)
  DayOfMonthSprite.h = ((HatWidth - DayOfMonthSprite.width) // 2) -1
  DayOfMonthSprite.v = 5
  DayOfMonthSprite.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)
  
  return DayOfMonthSprite





def CreateShortMessageSprite(ShortMessage):
  if (ShortMessage == "you win"):
    ShortMessageSprite = Sprite(
      16,
      11,
      200,
      0,
      0,
      [0,1,0,1,0,0,1,1,0,0,1,0,0,1,0,0,
       0,1,0,1,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0,
       0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
       0,1,0,0,0,1,0,1,1,1,0,1,0,0,1,0,
       0,1,0,1,0,1,0,0,1,0,0,1,1,0,1,0,  
       0,1,1,0,1,1,0,0,1,0,0,1,0,1,1,0,
       0,0,1,0,1,0,0,1,1,1,0,1,0,0,1,0,
       0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,  
       ]
    )
  elif (ShortMessage == "you die"):
    ShortMessageSprite = Sprite(
      16,
      11,
      200,
      0,
      0,
      [0,1,0,1,0,0,1,1,0,0,1,0,0,1,0,0,
       0,1,0,1,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,
       0,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0,
       0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
       0,1,1,0,0,1,1,1,0,1,1,1,0,0,1,0,
       0,1,0,1,0,0,1,0,0,1,0,0,0,0,1,0,  
       0,1,0,1,0,0,1,0,0,1,1,1,0,0,1,0,
       0,1,0,1,0,0,1,0,0,1,0,0,0,0,0,0,
       0,1,1,0,0,1,1,1,0,1,1,1,0,0,1,0,  
       ]
    )
  elif (ShortMessage == "smile"):
    ShortMessageSprite = Sprite(
      12,
      10,
      200,
      200,
      0,
      [0,0,0,0,1,1,1,1,0,0,0,0,
       0,0,0,1,0,0,0,0,1,0,0,0,
       0,0,1,0,0,0,0,0,0,1,0,0,
       0,1,0,0,1,0,0,1,0,0,1,0,
       0,1,0,0,0,0,0,0,0,0,1,0,
       0,1,0,1,0,0,0,0,1,0,1,0,
       0,1,0,0,1,1,1,1,0,0,1,0,
       0,0,1,0,0,0,0,0,0,1,0,0,  
       0,0,0,1,0,0,0,0,1,0,0,0,
       0,0,0,0,1,1,1,1,0,0,0,0,
       ]
    )
  else: #(ShortMessage == "frown"):
    ShortMessageSprite = Sprite(
      12,
      10,
      200,
      200,
      0,
      [0,0,0,0,1,1,1,1,0,0,0,0,
       0,0,0,1,0,0,0,0,1,0,0,0,
       0,0,1,0,0,0,0,0,0,1,0,0,
       0,1,0,0,1,0,0,1,0,0,1,0,
       0,1,0,0,0,0,0,0,0,0,1,0,
       0,1,0,0,0,1,1,0,0,0,1,0,
       0,1,0,0,1,0,0,1,0,0,1,0,
       0,0,1,0,0,0,0,0,0,1,0,0,  
       0,0,0,1,0,0,0,0,1,0,0,0,
       0,0,0,0,1,1,1,1,0,0,0,0,
       ]
    )
    
  
  #add variables to the object (python allows this, very cool!)
  ShortMessageSprite.h = (HatWidth - ShortMessageSprite.width) // 2
  ShortMessageSprite.v = 0 - ShortMessageSprite.height
  ShortMessageSprite.rgb = (ShortMessageSprite.r,ShortMessageSprite.g,ShortMessageSprite.b)
  ShortMessageSprite.StartTime = time.time()
  
  #used for scrolling clock
  ShortMessageSprite.PauseStartTime = time.time()
  ShortMessageSprite.IsScrolling     = 0
  ShortMessageSprite.Delay           = 1
  ShortMessageSprite.PausePositionV  = 2
  ShortMessageSprite.PauseTimerOn    = 0
  
  ShortMessageSprite.on = 0
  ShortMessageSprite.DirectionIncrement = 1

  
  return ShortMessageSprite


  
  
def CreateShortWordSprite(ShortWord):   

  ShortWord = ShortWord.upper()
  TheBanner = CreateBannerSprite(ShortWord)
      

  TheBanner.r = SDMedRedR
  TheBanner.g = SDMedRedG
  TheBanner.b = SDMedRedB
  
  
  #add variables to the object (python allows this, very cool!)
  TheBanner.h = (HatWidth - TheBanner.width) // 2
  TheBanner.v = -4
  TheBanner.rgb = (SDMedGreenR,SDMedGreenG,SDMedGreenB)

  #used for displaying clock
  TheBanner.StartTime = time.time()

  #used for scrolling clock
  TheBanner.PauseStartTime = time.time()
  TheBanner.IsScrolling     = 0
  TheBanner.Delay           = 2
  TheBanner.PausePositionV  = 1
  TheBanner.PauseTimerOn    = 0
  
  TheBanner.on = 1
  TheBanner.DirectionIncrement = 1

  
  return TheBanner 

  
  


  

  
 
  
def CreateBannerSprite(TheMessage):
  #We need to dissect the message and build our banner sprite one letter at a time
  #We need to initialize the banner sprite object first, so we pick the first letter
  x = -1
  TheMessage = TheMessage.upper()
  BannerSprite = Sprite(1,5,0,0,0,[0,0,0,0,0])
  
  #Iterate through the message, decoding each characater
  for i,c, in enumerate(TheMessage):
    x = ord(c) -65
    if (c == '?'):
      BannerSprite = JoinSprite(BannerSprite, QuestionMarkSprite,0)
    elif (c == '-'):
      BannerSprite = JoinSprite(BannerSprite, DashSprite,0)
    elif (c == '#'):
      BannerSprite = JoinSprite(BannerSprite, DashSprite,0)
    elif (c == '$'):
      BannerSprite = JoinSprite(BannerSprite, DollarSignSprite,0)
    elif (c == '.'):
      BannerSprite = JoinSprite(BannerSprite, PeriodSprite,0)
    elif (c == ':'):
      BannerSprite = JoinSprite(BannerSprite, ColonSprite,0)
    elif (c == '!'):
      BannerSprite = JoinSprite(BannerSprite, ExclamationSprite,0)
    elif (c == ' '):
      BannerSprite = JoinSprite(BannerSprite, SpaceSprite,0)
    elif (ord(c) >= 48 and ord(c)<= 57):
      BannerSprite = JoinSprite(BannerSprite, DigitSpriteList[int(c)],1)
    else:
      BannerSprite = JoinSprite(BannerSprite, TrimSprite(AlphaSpriteList[x]),1)
  return BannerSprite

  
    

  
  

def ShowLevelCount(LevelCount):
  global MainSleep
  TheMatrix.Clear()
      
  SDColor = (random.randint (0,6) *4 + 1) 
  print ("LevelCountColor:",SDColor)
  
  r,g,b =  ColorList[SDColor]  
  max   = 50
  #sleep = 0.06 * MainSleep
  
  #print ("sleep: ",sleep," MainSleep: ",MainSleep)
  
  LevelSprite = Sprite(1,5,r,g,b,[0,0,0,0,0])
  
  if (LevelCount > 9):
    LevelString = str(LevelCount)
    LevelSprite1 = DigitSpriteList[int(LevelString[0])]
    LevelSprite2 = DigitSpriteList[int(LevelString[1])]
   
    
    for x in range(0,max,1):
      LevelSprite1.r = r + x*5
      LevelSprite1.g = g + x*5
      LevelSprite1.b = b + x*5
      LevelSprite2.r = r + x*5
      LevelSprite2.g = g + x*5
      LevelSprite2.b = b + x*5

      if(LevelSprite1.r > 255):
        LevelSprite1.r = 255
      if(LevelSprite1.g > 255):
        LevelSprite1.g = 255
      if(LevelSprite1.b > 255):
        LevelSprite1.b = 255
      if(LevelSprite2.r > 255):
        LevelSprite2.r = 255
      if(LevelSprite2.g > 255):
        LevelSprite2.g = 255
      if(LevelSprite2.b > 255):
        LevelSprite2.b = 255

      LevelSprite.Display((HatWidth-6) // 2 ,(HatHeight -5)//2)
      LevelSprite.Display((HatWidth-10) // 2 ,(HatHeight -5)//2)      
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      #time.sleep(sleep)

    
    for x in range(0,max,1):
      LevelSprite1.r = r + max -x*3
      LevelSprite1.g = g + max -x*3
      LevelSprite1.b = b + max -x*3
      LevelSprite2.r = r + max -x*3
      LevelSprite2.g = g + max -x*3
      LevelSprite2.b = b + max -x*3

      if(LevelSprite1.r < r):
        LevelSprite1.r = r
      if(LevelSprite1.g < g):
        LevelSprite1.g = g
      if(LevelSprite1.b < b):
        LevelSprite1.b = b
      if(LevelSprite2.r < r):
        LevelSprite2.r = r
      if(LevelSprite2.g < g):
        LevelSprite2.g = g
      if(LevelSprite2.b < b):
        LevelSprite2.b = b

      LevelSprite1.Display(6,1)
      LevelSprite2.Display(10,1)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)

      #time.sleep(sleep) 
     
      
  else:    
    LevelSprite = DigitSpriteList[LevelCount]

    for x in range(0,max,1):
      LevelSprite.r = r + x*3
      LevelSprite.g = g + x*3
      LevelSprite.b = b + x*3

      if(LevelSprite.r > 255):
        LevelSprite.r = 255
      if(LevelSprite.g > 255):
        LevelSprite.g = 255
      if(LevelSprite.b > 255):
        LevelSprite.b = 255

      LevelSprite.Display((HatWidth-3) // 2 ,(HatHeight -5)//2)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      #time.sleep(sleep) 
      
    for x in range(0,max,1):
      LevelSprite.r = r + max -x*3
      LevelSprite.g = g + max -x*3
      LevelSprite.b = b + max -x*3

      if(LevelSprite.r < r):
        LevelSprite.r = r
      if(LevelSprite.g < g):
        LevelSprite.g = g
      if(LevelSprite.b < b):
        LevelSprite.b = b
      LevelSprite.Display((HatWidth-3) // 2 ,(HatHeight -5)//2)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      #time.sleep(sleep)
      

  
  TheMatrix.Clear()
  return
  







  

  


  
def ScreenWipe(Wipe, Speed):
  if Wipe == "RedCurtain":
    for x in range (HatWidth):
      for y in range (HatHeight):
        TheMatrix.SetPixel(x,y,255,0,0)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(Speed)
    
#Primitive, single color



  



  
  
def MoveBigSprite(sprite,FlashSleep):
  for i in range (0,80):
    
    y,x = divmod(i,16)
    #print ("x,y,i",x,y,i)
    if (x >= 0 and x<= 2):
      BigSprite.grid[i] = DigitSpriteList[2].grid[x-(0*4)+(y*3)]
    if (x >= 4 and x<= 6):
      BigSprite.grid[i] = DigitSpriteList[3].grid[x-(1*4)+(y*3)]
    if (x >=8  and x<= 10):
      BigSprite.grid[i] = DigitSpriteList[0].grid[x-(2*4)+(y*3)]
    if (x >=12  and x<= 14):
      BigSprite.grid[i] = DigitSpriteList[7].grid[x-(3*4)+(y*3)]
    #"looping"
  BigSprite.Scroll(-16,0,"right",24,FlashSleep)
  BigSprite.Scroll(9,0,"left",24,FlashSleep)
    

  
def JoinSprite(Sprite1, Sprite2, Buffer):
  #This function takes two sprites, and joins them together horizontally
  #The color of the second sprite is used for the new sprite
  height = Sprite1.height
  width  = Sprite1.width + Buffer + Sprite2.width
  elements = height * width
  x = 0
  y = 0
  
 
  TempSprite = Sprite(
  width,
  height,
  Sprite2.r,
  Sprite2.g,
  Sprite2.b,
  [0]*elements
  )
  for i in range (0,elements):
    y,x = divmod(i,width)
    
    #copy elements of first sprite
    if (x >= 0 and x< Sprite1.width):
      TempSprite.grid[i] = Sprite1.grid[x + (y * Sprite1.width)]
    
    if (x >= (Sprite1.width + Buffer) and x< (Sprite1.width + Buffer + Sprite2.width)):
      TempSprite.grid[i] = Sprite2.grid[(x - (Sprite1.width + Buffer)) + (y * Sprite2.width)]

  
  return TempSprite    


def TrimSprite(Sprite1):
  height       = Sprite1.height
  width        = Sprite1.width
  newwidth     = 0
  elements     = height * width
  Empty        = 1
  Skipped      = 0
  EmptyColumns = []
  EmptyCount   = 0
  BufferX      = 0
  BufferColumn = [(0) for i in range(height)]
  
  i = 0
  x = 0
  y = 0

  
  for x in range (0,width):
    
    #Find empty columns, add them to a list
    Empty = 1  
    for y in range (0,height):
      i = x + (y * width)
      
      BufferColumn[y] = Sprite1.grid[i]
      if (Sprite1.grid[i] != 0):
        Empty = 0
    
    if (Empty == 0):
      newwidth =  newwidth + 1
    
    elif (Empty == 1):
      #print ("Found empty column: ",x)
      EmptyColumns.append(x)
      EmptyCount = EmptyCount +1

      
  BufferSprite = Sprite(
    newwidth,
    height,
    Sprite1.r,
    Sprite1.g,
    Sprite1.b,
    [0]*(newwidth*height)
    )
      
  #Now that we identified the empty columns, copy data and skip those columns
  for x in range (0,width):
    Skipped = 0
    
    for y in range (0,height):
      i = x + (y * width)
      b = BufferX + (y * newwidth)
      if (x in EmptyColumns):
        Skipped = 1
      else:
        BufferSprite.grid[b] = Sprite1.grid[i]
    
    
    #advance our Buffer column counter only if we skipped a column
    if (Skipped == 0):
      BufferX = BufferX + 1
    
    
  
  BufferSprite.width = newwidth
  
  
  
  #print (BufferSprite.grid)
  return BufferSprite



def LeftTrimSprite(Sprite1,Columns):
  height       = Sprite1.height
  width        = Sprite1.width
  newwidth     = 0
  elements     = height * width
  Empty        = 1
  Skipped      = 0
  EmptyColumns = []
  EmptyCount   = 0
  BufferX      = 0
  BufferColumn = [(0) for i in range(height)]
  
  i = 0
  x = 0
  y = 0

  
  for x in range (0,width):
    
    #Find empty columns, add them to a list
    Empty = 1  
    for y in range (0,height):
      i = x + (y * width)
      
      BufferColumn[y] = Sprite1.grid[i]
      if (Sprite1.grid[i] != 0):
        Empty = 0
    
    if (Empty == 0 or EmptyCount > Columns):
      newwidth =  newwidth + 1
    
    elif (Empty == 1):
      #print ("Found empty column: ",x)
      EmptyColumns.append(x)
      EmptyCount = EmptyCount +1

      
  BufferSprite = Sprite(
    newwidth,
    height,
    Sprite1.r,
    Sprite1.g,
    Sprite1.b,
    [0]*(newwidth*height)
    )
      
  #Now that we identified the empty columns, copy data and skip those columns
  for x in range (0,width):
    Skipped = 0
    
    for y in range (0,height):
      i = x + (y * width)
      b = BufferX + (y * newwidth)
      if (x in EmptyColumns):
        Skipped = 1
      else:
        BufferSprite.grid[b] = Sprite1.grid[i]
    
    
    #advance our Buffer column counter only if we skipped a column
    if (Skipped == 0):
      BufferX = BufferX + 1
    
    
  
  BufferSprite.width = newwidth
  
  
  
  #print (BufferSprite.grid)
  return BufferSprite
    
  
 
  




#------------------------------------------------------------------------------
# Keyboard Functions                                                         --
#------------------------------------------------------------------------------




def ProcessKeypress(Key):

  global MainSleep
  global ScrollSleep
  global NumDots

  # a = animation demo
  # h = set time - hours minutes
  # q = quit - go on to next game
  # i = show IP address
  # r = reboot
  # p or space = pause 5 seconds
  # c = analog clock for 1 hour
  # t = Clock Only mode
  # 1 - 8 Games
  # 8 = ShowDotZerkRobotTime
  # 0 = ?
  # m = Debug Playfield/Map
    
  if (Key == "p" or Key == " "):
    time.sleep(5)
  elif (Key == "q"):
    TheMatrix.Clear()
    ShowScrollingBanner2("Quit!",(MedRed),ScrollSleep)
  elif (Key == "r"):
    TheMatrix.Clear()
    #ShowScrollingBanner("Reboot!",100,0,0,ScrollSleep * 0.55)
    os.execl(sys.executable, sys.executable, *sys.argv)
  elif (Key == "t"):

    ActivateClockMode(60)

  elif (Key == "c"):
    DrawTinyClock(60)
  elif (Key == "h"):
    SetTimeHHMM()
  elif (Key == "i"):
    ShowIPAddress()

  elif (Key == "+"):
    MainSleep = MainSleep -0.01
    ScrollSleep = ScrollSleep * 0.75
    if (MainSleep <= 0.01):
      MainSleep = 0.01

    #print("Game speeding up")
    #print("MainSleep: ",MainSleep, " ScrollSleep: ",ScrollSleep)
  elif (Key == "-"):
    MainSleep = MainSleep +0.01
    ScrollSleep = ScrollSleep / 0.75
    #print("Game slowing down ")
    #print("MainSleep: ",MainSleep, " ScrollSleep: ",ScrollSleep)



    
    
    


def GetKey(stdscr):
  ReturnChar = ""
  stdscr.nodelay(1) # doesn't keep waiting for a key press
  c = stdscr.getch()  
  
  #Look for specific characters
  if  (c == ord(" ") 
    or c == ord("+")
    or c == ord("-")
    or c == ord("a")
    or c == ord("b")
    or c == ord("c")
    or c == ord("d")
    or c == ord("h")
    or c == ord("i")
    or c == ord("p")
    or c == ord("q")
    or c == ord("r")
    or c == ord("t")
    or c == ord("n")
    or c == ord("m") ):
    ReturnChar = chr(c)       

  #Look for digits (ascii 48-57 == digits 0-9)
  elif (c >= 48 and c <= 57):
    print ("Digit detected")
    ReturnChar = chr(c)    

  return ReturnChar
 

  
  

def PollKeyboard():
  Key = ""
  curses.filter()
  stdscr = curses.initscr()
  curses.noecho()
  Key = curses.wrapper(GetKey)
  if (Key != ""):
    print ("----------------")
    print ("Key Pressed: ",Key)
    print ("----------------")
    #ProcessKeypress(Key)
    #SaveConfigData()
    
  
  return Key


  
def GetKeyInt(stdscr):
  ReturnInt = -1
  stdscr.nodelay(1) # doesn't keep waiting for a key press
  
  #gets ascii value
  c = stdscr.getch()  

  
  #Look for digits (ascii 48-57 == digits 0-9)
  if (c >= 48 and c <= 57):
    print ("Digit detected")
    ReturnInt = c - 48   

  return ReturnInt

  
  
def PollKeyboardInt():
  Key = -1
  stdscr = curses.initscr()
  curses.noecho()
  Key = curses.wrapper(GetKeyInt)
  if (Key != -1):
    print ("----------------")
    print ("Key Pressed: ",Key)
    print ("----------------")
    ProcessKeypress(Key)
  
  return Key


  

  
  
# This section deals with getting specific input from a question and does not
# trigger events  
  
def GetKeyRegular(stdscr):
  ReturnChar = ""
  stdscr.nodelay(1) # doesn't keep waiting for a key press
  c = stdscr.getch()  

  if (c >= 48 and c <= 150):
    ReturnChar = chr(c)    

  return ReturnChar
  
def PollKeyboardRegular():
  Key = ""
  stdscr = curses.initscr()
  curses.noecho()
  Key = curses.wrapper(GetKeyRegular)
  if (Key != ""):
    print ("----------------")
    print ("Key Pressed: ",Key)
    print ("----------------")
  
  return Key
  


def GetClockDot(time):
  #this is a list of hv coordinates around the outside of the unicorn hat
  #pass in a number from 1-60 to get the correct dot to display
  
  DotList = []
  DotList.append ([4,0]) #0 same as 60
  DotList.append ([4,0])
  DotList.append ([5,0])
  DotList.append ([6,0])
  DotList.append ([7,0])
  DotList.append ([7,1])
  DotList.append ([7,2])
  DotList.append ([7,3])
  DotList.append ([7,4])
  DotList.append ([7,5])
  DotList.append ([7,6])
  DotList.append ([7,7])
  DotList.append ([6,7])
  DotList.append ([5,7])
  DotList.append ([4,7])
  DotList.append ([3,7])
  DotList.append ([2,7])
  DotList.append ([1,7])
  DotList.append ([0,7])
  DotList.append ([0,6])
  DotList.append ([0,5])
  DotList.append ([0,4])
  DotList.append ([0,3])
  DotList.append ([0,2])
  DotList.append ([0,1])
  DotList.append ([0,0])
  DotList.append ([1,0])
  DotList.append ([2,0])
  DotList.append ([3,0])
  
  return DotList[time]







def DrawTinyClock(Minutes):
  print ("--DrawTinyClock--")
  print ("Minutes:",Minutes)
  TheMatrix.Clear()
  MinDate = datetime.now()
  MaxDate = datetime.now() + timedelta(minutes=Minutes)
  now     = datetime.now()
  Quit    = 0
  

  while (now >= MinDate and now <= MaxDate and Quit == 0):
    print ("--DrawTinyClock--")
    TheMatrix.Clear()
    ClockSprite = CreateClockSprite(2)
    ClockSprite.r = SDDarkRedR
    ClockSprite.g = SDDarkRedG
    ClockSprite.b = SDDarkRedB


    #Center the display
    h = 3 - (ClockSprite.width // 2)
    ClockSprite.Display(h,1)

    #break apart the time
    now = datetime.now()

    print ("Now:",now)
    print ("Min:",MinDate)
    print ("Max:",MaxDate)
    DrawClockMinutes()
    Quit = DrawClockSeconds()
    print("Quit:",Quit)
    now = datetime.now()

  TheMatrix.Clear()
    
def DrawClockMinutes():

  #break apart the time
  now = datetime.now()
  mm  = now.minute
  print ("DrawClockMinutes minutes:",mm)  
  
  dots = int(28.0 // 60.0 * mm)

#  #Erase  
  for i in range(1,28):
    h,v = GetClockDot(i)
  TheMatrix.SetPixel(h,v,0,0,0)
  #unicorn.show()
  #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)

  
  for i in range(1,dots+1):
    print ("Setting minute dot:",i)
    h,v = GetClockDot(i)
    TheMatrix.SetPixel(h,v,SDDarkBlueR,SDDarkBlueG,SDDarkBlueB)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
  
  
  
  
def DrawClockSeconds():
  #break apart the time
  now = datetime.now()
  ss  = now.second
  
  print ("--DrawClockSeconds seconds:",ss,"--")  

  r = 0
  g = 0
  b = 0
  
   
  h = 0
  v = 0
  x = -1
  y = -1
  
  
  TheMatrix.SetPixel(3,0,0,0,0)


  for i in range(ss,61):
    
    #Erase dot 0/60
    DisplayDot =  int(28.0 // 60.0 * i)
    h,v = GetClockDot(DisplayDot)
    
    
    print ("Setting second dot:",i)
    #print ("xy hv:",x,y,h,v)
    if (x >= 0):
      #print ("writing old pixel")
      TheMatrix.SetPixel(x,y,r,g,b)

    
    #capture previous pixel
    x,y = h,v
    
    r,g,b = getpixel(h,v)
    TheMatrix.SetPixel(h,v,SDLowWhiteR,SDLowWhiteG,SDLowWhiteB)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
    time.sleep(0.005)

    TheMatrix.SetPixel(h,v,SDDarkPurpleR,SDDarkPurpleG,SDDarkPurpleB)
    #unicorn.show()
    #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
    
    #Check for keyboard input
    Key = PollKeyboard()
    if (Key == 'q'):
      return 1
    

    
    time.sleep(0.995)
    
  print ("--end seconds--")
  return 0
  


#--------------------------------------
#  Transitions and Sequences         --
#--------------------------------------



def ScrollBigClock(direction,speed,ZoomFactor):    
  #Screen capture is a copy of the unicorn display Buffer, which in HD is a numby array
  #Capture the screen, then pass that to this function
  #this function will make a copy, chop up that copy and display the slices in the order to make
  #it look like the screen is scrolling up or down, left or right
  
  #For now, we scroll, replacing with empty screen.  Also, reverse.
 
  RGB, ShadowRGB = GetBrightAndShadowRGB()

  #Canvas.Clear()
  
  #ClockScreen
  ClockScreen  = [[]]
  ClockScreen  = [[ (0,0,0) for i in range(HatWidth)] for i in range(HatHeight)]
  

  ScreenCopy = copy.deepcopy(ScreenArray)
  ScreenCopy2 = copy.deepcopy(ScreenArray)

  #ClearBuffers()
  print("about to create clock sprite")
  TheTime = CreateClockSprite(12)
  TheTime.h = (HatWidth  //2) - (TheTime.width  * ZoomFactor // 2) - ZoomFactor
  TheTime.v = (HatHeight //2) - (TheTime.height * ZoomFactor // 2) - ZoomFactor
  

  print ("create clock scren")
  #this will copy the clock sprite to the regular screen buffer ScreenBuffer
  #make drop shadow then draw current time
  ClockScreen = CopySpriteToBufferZoom(TheBuffer=ClockScreen, TheSprite=TheTime,h=TheTime.h-2,v=TheTime.v+2, ColorTuple=ShadowRGB,FillerTuple=(-1,-1,-1),ZoomFactor = ZoomFactor,Fill=False)
  ClockScreen = CopySpriteToBufferZoom(TheBuffer=ClockScreen, TheSprite=TheTime,h=TheTime.h-1,v=TheTime.v+1, ColorTuple=ShadowRGB,FillerTuple=(-1,-1,-1),ZoomFactor = ZoomFactor,Fill=False)
  ClockScreen = CopySpriteToBufferZoom(TheBuffer=ClockScreen, TheSprite=TheTime,h=TheTime.h,v=TheTime.v, ColorTuple=RGB,FillerTuple=(-1,-1,-1),ZoomFactor = ZoomFactor,Fill=False)
  print ("clock screen created")
  
  print ("about to start scrolling")
  
    

  #Scroll up
  #Delete top row, insert blank on bottom, pushing remaining to the top
  if (direction == 'up'):
    
  
    for x in range (0,HatHeight):
      #Take a line from the clock sprite 
      InsertLine = ClockScreen[x]
      ScreenCopy = numpy.delete(ScreenCopy,(0),axis=0)
      ScreenCopy  = numpy.insert(ScreenCopy,HatHeight-1,InsertLine,axis=0)
      setpixelsLED(ScreenCopy)

      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      time.sleep(speed)

    
    

  Oldmm = 0
  done  = 0
  ShownOnce = 0
  

  print("going into a loop")

  while (1 == 1):
 
    #If the time has changed, draw a new time
    mm = datetime.now().strftime('%M')
    if (mm != Oldmm):
      #Erase old time
      Oldmm = mm
      

      TheTime = CreateClockSprite(12)
      TheTime.h = (HatWidth //2 )  - (TheTime.width * ZoomFactor // 2)  - ZoomFactor
      TheTime.v = (HatHeight //2 ) - (TheTime.height * ZoomFactor // 2) - ZoomFactor

      #Display New Time
      ClockScreen  = [[]]
      ClockScreen  = [[ (0,0,0) for i in range(HatWidth)] for i in range(HatHeight)]
      #make drop shadow then draw current time
      ClockScreen = CopySpriteToBufferZoom(TheBuffer=ClockScreen, TheSprite=TheTime,h=TheTime.h-2,v=TheTime.v+2, ColorTuple=ShadowRGB,FillerTuple=(-1,-1,-1),ZoomFactor = ZoomFactor,Fill=False)
      ClockScreen = CopySpriteToBufferZoom(TheBuffer=ClockScreen, TheSprite=TheTime,h=TheTime.h-1,v=TheTime.v+1, ColorTuple=ShadowRGB,FillerTuple=(-1,-1,-1),ZoomFactor = ZoomFactor,Fill=False)
      ClockScreen = CopySpriteToBufferZoom(TheBuffer=ClockScreen, TheSprite=TheTime,h=TheTime.h,v=TheTime.v, ColorTuple=RGB,FillerTuple=(-1,-1,-1),ZoomFactor = ZoomFactor,Fill=False)
      setpixelsLED(ClockScreen)

      


    Key = PollKeyboard()
    if (Key =='q'):
      for x in range (0,HatHeight):
        InsertLine = ScreenCopy2[x]
        ClockScreen = numpy.delete(ClockScreen,(0),axis=0)
        ClockScreen = numpy.insert(ClockScreen,HatHeight-1,InsertLine,axis=0)
        setpixelsLED(ClockScreen)
        #unicorn.show()
        #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
        time.sleep(speed)
      return;

    print("sleeping")
    time.sleep(1)








def ScrollScreen(direction,ScreenCap,speed):    
  #Screen capture is a copy of the unicorn display Buffer, which in HD is a numby array
  #Capture the screen, then pass that to this function
  #this function will make a copy, chop up that copy and display the slices in the order to make
  #it look like the screen is scrolling up or down, left or right
  
  #For now, we scroll, replacing with empty screen.  Also, reverse.
 
 
  EmptyCap   = [[(0,0,0) for i in range (0,HatWidth)]]
  InsertLine = copy.deepcopy(EmptyCap)
  Buffer     = copy.deepcopy(EmptyCap)

  
  #Scroll up
  #Delete top row, insert blank on bottom, pushing remaining to the top
  if (direction == 'up'):
    Buffer = copy.deepcopy(ScreenCap)
    #print ("Buffer",Buffer)

    for x in range (0,HatHeight):
      
      Buffer = numpy.delete(Buffer,(0),axis=1)
      Buffer = numpy.insert(Buffer,HatHeight-1,InsertLine,axis=1)
      setpixelsLED(Buffer)


      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      #print(Buffer)
      time.sleep(speed)

  #Scroll down
  #Screen is blank, start adding lines from ScreenCap
  if (direction == 'down'):
    # Make an empty Buffer, axis must be 0 to match the EmptyBuffer layout [(0,0,0),(0,0,0),(0,0,0)...etc.]
    Buffer = [[(0,0,0) for i in range(HatHeight)] for i in range(HatWidth)]

    for x in range (0,HatWidth):
      InsertLine = [()]
      #copy line from the ScreenCap into the Buffer
      #we do this one element at a time because I could not figure out how to slice the array properly
      for y in range (0,HatWidth):
        InsertLine = numpy.append(InsertLine, ScreenCap[y][abs(HatWidth-1 - x)])

      InsertLine = InsertLine.reshape(1,HatWidth,3)
      Buffer = numpy.insert(Buffer,0,InsertLine,axis=1)
      setpixelsLED(Buffer)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      time.sleep(speed)


      
      

  #Scroll to RIGHT
  #Delete right row, insert blank on left, pushing remaining to the right
  if (direction == 'right'):
    Buffer = copy.deepcopy(ScreenCap)
    for x in range (0,HatWidth):
      
      Buffer = numpy.delete(Buffer,(0),axis=0)
      Buffer = numpy.append(Buffer,EmptyCap,axis=0)
      setpixelsLED(Buffer)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      #time.sleep(speed)
  
  
  
  
  #Scroll to LEFT
  #Delete left row, insert blank on right, pushing remaining to the left
  if (direction == 'left'):
    # Make an empty Buffer
    for x in range (0,HatWidth-1):
      Buffer = numpy.append(Buffer,EmptyCap,axis=0)

    for x in range (0,HatWidth):
      Buffer = numpy.delete(Buffer,(-1),axis=0)
      
      #Copy each tuple to the line to be inserted (gotta be a better way!)
      for j in range (HatWidth):
        InsertLine[0][j] = ScreenCap[abs(HatWidth-x)][j]
      
      Buffer = numpy.insert(Buffer,0,InsertLine,axis=0)
      
      setpixelsLED(Buffer)
      #unicorn.show()
      #SendBufferPacket(RemoteDisplay,HatHeight,HatWidth)
      time.sleep(speed)


      




# Try looping the number of zooms, but re-capture the screen at the zoomed in level and pass that back into
# the DisplayScreenCap function


def ZoomScreen(ScreenArray,ZoomStart,ZoomStop,ZoomSleep,Fade=False):    
  #Capture the screen, then pass that to this function
  #Loop through the zoom levels specified, calling the DisplayScreenCap function

 
  ZoomFactor    = 0
  DimIncrement  = max(round(100 / abs(ZoomStart - ZoomStop)),1)
  OldBrightness = TheMatrix.brightness
  Brightness    = OldBrightness

  if (ZoomStart <= ZoomStop):
    for ZoomFactor in range (ZoomStart,ZoomStop):
      if (Fade == True):
        Brightness = Brightness - DimIncrement
        if (Brightness >= 0):
          TheMatrix.brightness = Brightness
          #print("Brightness:",Brightness)
      TheMatrix.Clear()        
      DisplayScreenCap(ScreenArray,ZoomFactor)
      if (ZoomSleep > 0):
        time.sleep(ZoomSleep)
        
  else:
    for ZoomFactor in reversed(range(ZoomStop, ZoomStart)):
      #clear the screen as we zoom to remove leftovers
      if (Fade == True):
        Brightness = Brightness - DimIncrement
        if (Brightness >= 0):
          TheMatrix.brightness = Brightness
          #print("Brightness:",Brightness)
      TheMatrix.Clear()        
      DisplayScreenCap(ScreenArray,ZoomFactor)
      if (ZoomSleep > 0):
        time.sleep(ZoomSleep)

  #go back to old brightness
  TheMatrix.brightness = OldBrightness


  # for y in range (HatWidth):
    # for x in range (HatWidth):
      # r,g,b = ScreenCap[abs(15-x)][y]
      # TheMatrix.SetPixel(x,y,r,g,b)





def DisplayScreenCap(ScreenCap,ZoomFactor = 0):
  #This function writes a Screen capture to the buffer using the specified zoom factor
  #ZoomFactor is based on Vertical height.  
  #  Matrix = 32, Zoom 16 = shrink screen to 1/2 size
  #  Matrix = 32, Zoom 64 = show 1/2 of screen capture, doubled so it fits on whole screen
  r = 0
  g = 0
  b = 0
  count    = 0
  H_modifier = 0
  V_modifier = 0
  H = 0
  V = 0
  HIndentFactor = 0    
  VIndentFactor = 0    
  
 

  #NewScreenCap = deepcopy.copy(ScreenCap)


  if (ZoomFactor > 1):
    H_modifier = (1 / HatWidth ) * ZoomFactor * 2  #BigLED is 2 times wider than tall. Hardcoding now, will fix later. 
    V_modifier = (1 / HatHeight ) * ZoomFactor

    #calculate the newsize of the zoomed screen cap
    NewHeight = round(HatHeight * V_modifier)
    NewWidth  = round(HatWidth * H_modifier)

    HIndentFactor = (HatWidth / 2)  - (NewWidth /2)
    VIndentFactor = (HatHeight / 2) - (NewHeight /2)
  else:
    IndentFactor = 0



#  for V in range(max(math.floor((0 + V_modifier * 2) ),0) ,min(math.floor((HatHeight - V_modifier * 2) ),HatHeight-1)) :
#    for H in range (max(math.floor((0 + H_modifier * 4)),0),min(math.floor((HatWidth - H_modifier * 4) ),HatWidth-1)):
  for V in range(0,HatHeight):
    for H in range (0,HatWidth):
      if (CheckBoundary((H * H_modifier) + HIndentFactor ,(V * V_modifier) + VIndentFactor) == 0):
      
        r,g,b = ScreenCap[V][H]
        if (ZoomFactor > 0):
          Canvas.SetPixel((H * H_modifier) + HIndentFactor ,(V * V_modifier) + VIndentFactor,r,g,b)
        
        else:
          Canvas.SetPixel(H,V,r,g,b)

  TheMatrix.SwapOnVSync(Canvas)
        
  
  #unicorn.show()




  
    
def ScrollScreenScrollBanner(message,r,g,b,direction,speed):

  # this has been converted from an older way of scrolling.  
  # we might need to input multiple directions to give more flexibility
  
  
  ScreenCap  = copy.deepcopy(unicorn.get_pixels())
  ScrollScreen('up',ScreenCap,speed)

  af.ShowScrollingBanner(message,r,g,b,speed)

  TheTime.ScrollAcrossScreen(0,1,"right",speed)
  ScrollScreen('down',ScreenCap,speed)













def ShowIPAddress():
  IPAddress = str(subprocess.check_output("hostname -I", shell=True)[:-1]);
  print ("-->",IPAddress,"<--")
  ShowScrollingBanner2(IPAddress[2:17],(HighGreen),ScrollSleep)














def ShowGlowingText(
    h          = -1,            #horizontal placement of upper left corner of text banner
    v          = -1,            #vertical   placement of upper left corner of text banner
    Text       = 'Test',        #Text messatge to display (make sure it fits!)
    RGB        = (100,100,100), #color value of the text
    ShadowRGB  = (20,20,20),    #color value of the shadow
    ZoomFactor = 2,             #scale the text (1=normal, 2=twice the size, etc.)
    GlowLevels = 200,           #how many brightness increments to show the text
    DropShadow = True,          #show a drop shadow of the text
    CenterHoriz = False,        #center text horizontally, overrides H
    CenterVert  = False,        #center text vertically, overrides V
    FadeLevels  = 0,            #Fade the text in this many brightness decrements
    FadeDelay   = 0.25         #How long to keep text on screen before fading

  ):

  global ScreenArray

  r,g,b = RGB 
  r2 = 0
  g2 = 0
  b2 = 0
  Text      = Text.upper()
  TheBanner = CreateBannerSprite(Text)
  

  #Center if HV not specified
  if (CenterHoriz == True):
    h = (HatWidth // 2)  - ((TheBanner.width * ZoomFactor) // 2) - ZoomFactor
  if (CenterVert  == True):
    v = (HatHeight // 2) - ((TheBanner.height * ZoomFactor) // 2) - ZoomFactor
  #Draw Shadow Text
  if(DropShadow == True):
    CopySpriteToPixelsZoom(TheBanner,h-1,v+1,ShadowRGB,(0,0,0),ZoomFactor,Fill=False)

                                    
  if (GlowLevels > 0):
    for i in range (1,GlowLevels):
      r2 = math.ceil((r / GlowLevels) * i)
      g2 = math.ceil((g / GlowLevels) * i)
      b2 = math.ceil((b / GlowLevels) * i)
      CopySpriteToPixelsZoom(TheBanner,h,v,(r2,g2,b2),(0,0,0),ZoomFactor,Fill=False)

  #Draw text
  CopySpriteToPixelsZoom(TheBanner,h,v,(r,g,b),(0,0,0),ZoomFactor,Fill=False)


  #Fade away!
  if (FadeLevels > 0):
    time.sleep(FadeDelay)
    if(DropShadow == True):
      CopySpriteToPixelsZoom(TheBanner,h-1,v+1,(0,0,0),(0,0,0),ZoomFactor,Fill=False)

    for i in range (FadeLevels,0,-1):
      r2 = math.ceil((r / GlowLevels) * i)
      g2 = math.ceil((g / GlowLevels) * i)
      b2 = math.ceil((b / GlowLevels) * i)
      CopySpriteToPixelsZoom(TheBanner,h,v,(r2,g2,b2),(0,0,0),ZoomFactor,Fill=False)
    #erase remnants
    CopySpriteToPixelsZoom(TheBanner,h,v,(0,0,0),(0,0,0),ZoomFactor,Fill=False)
    CopySpriteToPixelsZoom(TheBanner,h-1,v+1,(0,0,0),(0,0,0),ZoomFactor,Fill=False)


  return   




def ShowGlowingSprite(
    h          = -1,                #horizontal placement of upper left corner of text banner
    v          = -1,                #vertical   placement of upper left corner of text banner
    TheSprite  = ExclamationSprite, #Text message to display (make sure it fits!)
    RGB        = HighRed,
    ShadowRGB  = ShadowRed,         #color value of the shadow
    ZoomFactor = 2,                 #scale the text (1=normal, 2=twice the size, etc.)
    GlowLevels = 200,               #how many brightness increments to show the text
    DropShadow = True,          #show a drop shadow of the text
    CenterHoriz = False,        #center text horizontally, overrides H
    CenterVert  = False,        #center text vertically, overrides V
    FadeLevels  = 0,            #Fade the text in this many brightness decrements
    FadeDelay   = 0.25          #How long to keep text on screen before fading
  ):

  #Note: alphanumeric sprites have RGB = 0, so you need to pass in the desired RGB

  global ScreenArray

  r,g,b = (RGB)
  r2 = 0
  g2 = 0
  b2 = 0
    

  #Center if HV not specified
  if (CenterHoriz == True):
    h = (HatWidth // 2)  - ((TheSprite.width * ZoomFactor) // 2) - ZoomFactor
  if (CenterVert  == True):
    v = (HatHeight // 2) - ((TheSprite.height * ZoomFactor) // 2) - ZoomFactor
  #Draw Shadow Text
  if(DropShadow == True):
    CopySpriteToPixelsZoom(TheSprite,h-1,v+1,ShadowRGB,(0,0,0),ZoomFactor,Fill=False)

                                    
  if (GlowLevels > 0):
    for i in range (1,GlowLevels):
      r2 = math.ceil((r / GlowLevels) * i)
      g2 = math.ceil((g / GlowLevels) * i)
      b2 = math.ceil((b / GlowLevels) * i)
      CopySpriteToPixelsZoom(TheSprite,h,v,(r2,g2,b2),(0,0,0),ZoomFactor,Fill=False)

  #Draw Sprite
  CopySpriteToPixelsZoom(TheSprite,h,v,RGB,(0,0,0),ZoomFactor,Fill=False)


  #Fade away!
  if (FadeLevels > 0):
    time.sleep(FadeDelay)
    if(DropShadow == True):
      CopySpriteToPixelsZoom(TheSprite,h-1,v+1,(0,0,0),(0,0,0),ZoomFactor,Fill=False)

    for i in range (FadeLevels,0,-1):
      r2 = math.ceil((r / GlowLevels) * i)
      g2 = math.ceil((g / GlowLevels) * i)
      b2 = math.ceil((b / GlowLevels) * i)
      CopySpriteToPixelsZoom(TheSprite,h,v,(r2,g2,b2),(0,0,0),ZoomFactor,Fill=False)
    #erase remnants
    CopySpriteToPixelsZoom(TheSprite,h,v,(0,0,0),(0,0,0),ZoomFactor,Fill=False)
    CopySpriteToPixelsZoom(TheSprite,h-1,v+1,(0,0,0),(0,0,0),ZoomFactor,Fill=False)

 
  return   





def CopySpriteToPixelsZoom(TheSprite,h,v, ColorTuple=(-1,-1,-1),FillerTuple=(-1,-1,-1),ZoomFactor = 1,Fill=True):
  #Copy a regular sprite to the LED and the ScreenArray buffer
  #Apply a ZoomFactor i.e  1 = normal / 2 = double in size / 3 = 3 times the size
  #print ("Copying sprite to playfield:",TheSprite.name, ObjectType, Filler)
  #if Fill = False, don't write anything for filler, that way we can leave existing lights on LED

  width   = TheSprite.width 
  height  = TheSprite.height

  global ScreenArray  
  
  if (ColorTuple == (-1,-1,-1)):
    r = TheSprite.r
    g = TheSprite.g
    b = TheSprite.b
  else:
    r,g,b   = ColorTuple
  
  if (FillerTuple == (-1,-1,-1)):
    fr = 0
    fg = 0
    fb = 0
  else:
    fr,fg,fb   = FillerTuple


  #Copy sprite to LED pixels
  for count in range (0,(TheSprite.width * TheSprite.height) ):
    y,x = divmod(count,TheSprite.width)

    y = y * ZoomFactor
    x = x * ZoomFactor


    if (ZoomFactor >= 1):
      for zv in range (0,ZoomFactor):
        for zh in range (0,ZoomFactor):
          H = x+h+zh
          V = y+v+zv
         
          if(CheckBoundary(H,V) == 0):

            if TheSprite.grid[count] != 0:
              Canvas.SetPixel(H,V,r,g,b)
              ScreenArray[V][H]=(r,g,b)
            else:
              if (Fill == True):
                Canvas.SetPixel(H,V,fr,fg,fb)
                ScreenArray[V][H]=(fr,fg,fb)

  #draw the contents of the buffer to the LED matrix
  TheMatrix.SwapOnVSync(Canvas)
  



  return;




def CopyAnimatedSpriteToPixelsZoom(TheSprite,h,v, ZoomFactor = 1):
  #Copy a color animated sprite to the LED and the ScreenArray buffer
  #Apply a ZoomFactor i.e  1 = normal / 2 = double in size / 3 = 3 times the size
  #print ("Copying sprite to playfield:",TheSprite.name, ObjectType, Filler)
  #if Fill = False, don't write anything for filler, that way we can leave existing lights on LED

  width   = TheSprite.width 
  height  = TheSprite.height

  global ScreenArray  
  
  TheFrame = TheSprite.currentframe
  #Copy sprite to LED pixels
  for count in range (0,(TheSprite.width * TheSprite.height)):
    y,x = divmod(count,TheSprite.width)

    y = y * ZoomFactor
    x = x * ZoomFactor


    if (ZoomFactor >= 1):
      for zv in range (0,ZoomFactor):
        for zh in range (0,ZoomFactor):
          H = x+h+zh
          V = y+v+zv
         
          if(CheckBoundary(H,V) == 0):

            #if TheSprite.grid[TheFrame][count] != 0:
            r,g,b =  ColorList[TheSprite.grid[TheFrame][count]]
            Canvas.SetPixel(H,V,r,g,b)
            ScreenArray[V][H]=(r,g,b)
  
  #draw the contents of the buffer to the LED matrix
  TheMatrix.SwapOnVSync(Canvas)
  

  TheFrame = TheFrame + 1
  if (TheFrame > TheSprite.frames):
    TheFrame = 1

  TheSprite.currentframe = TheFrame

  return;










def CopySpriteToBufferZoom(TheBuffer,TheSprite,h,v, ColorTuple=(-1,-1,-1),FillerTuple=(-1,-1,-1),ZoomFactor = 1,Fill=True):
  #Copy a regular sprite to a buffer
  #Apply a ZoomFactor i.e  1 = normal / 2 = double in size / 3 = 3 times the size
  #print ("Copying sprite to playfield:",TheSprite.name, ObjectType, Filler)

  global ScreenArray

  width   = TheSprite.width 
  height  = TheSprite.height
  
  if (ColorTuple == (-1,-1,-1)):
    r = TheSprite.r
    g = TheSprite.g
    b = TheSprite.b
  else:
    r,g,b   = ColorTuple

  if (FillerTuple == (-1,-1,-1)):
    fr = 0
    fg = 0
    fb = 0
  else:
    fr,fg,fb   = FillerTuple


  #Copy sprite to buffer 
  for count in range (0,(width * height)):
    y,x = divmod(count,width)

    y = y * ZoomFactor
    x = x * ZoomFactor

    
    if (ZoomFactor >= 1):
      for zv in range (0,ZoomFactor):
        for zh in range (0,ZoomFactor):
          H = x+h+zh
          V = y+v+zv
         
          if(CheckBoundary(H,V) == 0):

            if TheSprite.grid[count] != 0:
              #Canvas.SetPixel(H,V,r,g,b)
              #ScreenArray[V][H]=(r,g,b)
              TheBuffer[V][H]=(r,g,b)

            else:
              if (Fill == True):
                #Canvas.SetPixel(H,V,fr,fg,fb)
                #ScreenArray[V][H]=(fr,fg,fb)
                TheBuffer[V][H]=(fr,fg,fb)


  
  return TheBuffer




  def CopySpriteToBuffer(self,h1,v1):
    #Does the same as Display, but does not call show(), allowing calling function to further modify the Buffer
    #before displaying
    x = 0,
    y = 0
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          TheMatrix.SetPixel(x+h1,y+v1,self.r,self.g,self.b)
      elif self.grid[count] == 0:
        if (CheckBoundary(x+h1,y+v1) == 0):
          TheMatrix.SetPixel(x+h1,y+v1,0,0,0)
    #unicorn.show()



def DisplayScore(score,rgb):

  r,g,b = rgb

  ScoreSprite = CreateBannerSprite(str(score))
  ScoreH      = HatWidth  - ScoreSprite.width
  ScoreV      = HatHeight - ScoreSprite.height
  ScoreSprite.r = r
  ScoreSprite.g = g
  ScoreSprite.b = b
  ScoreSprite.DisplayIncludeBlack(ScoreH,ScoreV)






def DisplayScoreMessage(h=0,v=0,Message='TEST',RGB=(100,100,100),FillerRGB=(0,0,0)):

  r,g,b    = RGB
  fr,fg,fb = FillerRGB
  ScoreH   = h
  ScoreV   = v



  #Display a message where the scoreboard is (lower right corner)
  ScoreMessage = CreateBannerSprite(str(Message.upper()))
  
  if (ScoreH == 0):
    ScoreH      = (HatWidth  - ScoreMessage.width) // 2
  if (ScoreV == 0):
    ScoreV      = HatHeight - ScoreMessage.height
  ScoreMessage.r = r
  ScoreMessage.g = g
  ScoreMessage.b = b
  #ScoreMessage.DisplayIncludeBlack(ScoreH,ScoreV)
  CopySpriteToPixelsZoom(ScoreMessage,ScoreH,ScoreV, ColorTuple=(RGB),FillerTuple=(FillerRGB),ZoomFactor = 1,Fill=True)




def DisplayLevel(level,rgb):

  r,g,b = rgb

  ScoreSprite = CreateBannerSprite(str(level))
  ScoreH      = HatWidth  - 33
  ScoreV      = HatHeight - ScoreSprite.height
  ScoreSprite.r = r
  ScoreSprite.g = g
  ScoreSprite.b = b
  ScoreSprite.DisplayIncludeBlack(ScoreH,ScoreV)








  



def GetElapsedSeconds(starttime):
  elapsed_time = time.time() - starttime
  elapsed_hours   = elapsed_time / 3600
  elapsed_minutes = elapsed_time / 60
  elapsed_seconds = elapsed_time 
  #print ("StartTime:",starttime,"Seconds:",seconds)
  #print("Clock Timer: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours),int(elapsed_minutes),elapsed_seconds),"Elapsed seconds:",elapsed_seconds, "Check seconds:",seconds)
  
  return elapsed_time





def TronGetRandomMessage(MessageType = 'TAUNT'):
  

  if (MessageType == 'TAUNT'):
    MessageList = ('NICE TRY',
                   'YOU FAIL',
                   'NOOOO!',
                   'HA HA!',
                   'AGAIN ?',
                   'LOSER!',
                   'YOU LOSE',
                   'YOU DIED',
                   'PLAYER!!!',
                   'GOT EM',
                   'THEY ESCAPED!',
                   'AFTER THEM!',
                   'YOU WILL FAIL',
                   'FIX THAT WALL',
                   'WHAT???',
                   'NEVER GIVE UP',
                   'THAT STINKS!',
                   'SYNTAX ERROR',
                   'NOT NICE!',
                   'STOPSTOPSTOP',
                   'ILLEGAL STOP',
                   'FULL STOP',
                   'DO NOT RUN',
                   'BUT WHY?',
                   'THAT WAS FUN',
                   'TRY AGAIN?',
                   'COME BACK!',
                   'NO ESCAPE',
                   'NOT TODAY!',
                   'GET THEM',
                   'ALERT!',
                   'IS IT SAFE?',
                   'MISSED IT BY THAT MUCH!',
                   'YOUR LACK OF SKILL DISTURBS ME'

                   
      )
  elif (MessageType == 'CHALLENGE'):
    MessageList = ('DO YOU FIGHT FOR THE PLAYER?',
                   'DO YOU FIGHT FOR MCP?',
                   'WELCOME TO THE CIRCUITBOARD',
                   'ARE YOU A USER?',
                   'ARE YOU READY FOR THE CHALLENGE?',
                   'WITNESS THE MIGHT OF MCP!',
                   'GET YOUR JETBIKE READY',
                   'RUN HIM INTO THE JETWALLS!',
                   'THIS CLOCK IS FULLY ARMED AND OPERATIONAL',
                   'SIT FACING THE SCREEN LOGAN 5',
                   'GET READY',
                   'DESERVE VICTORY!',
                   'FIGHT FOR THE USER!',
                   'FIGHT FOR MCP!',
                   'THERE IS NO SANCTUARY...',
                   'SOYLENT GREEN IS....TASTY!',
                   'THIS IS NOT AN ALERT',
                   'WELCOME TO THE REAL WORLD NEO',
                   'PREPARE YOURSELF FOR BATTLE!',
                   'GET ON YOUR BIKES AND RIDE!',
                   'ANOTHER WARRIOR FOR MY ASMUSEMENT!',
                   'DO YOU DARE TO ENTER THE ARENA?',
                   'YOUR JET BIKE HAS A FLAT TIRE',
                   'DO YOU HAVE TIME FOR A GAME?',
                   'HOW ABOUT A GAME OF THERMONUCLEAR WAR?',
                   'TODAY IS A GOOD DAY TO WATCH A CLOCK',
                   'WELCOME TO THUNDERDOME',
                   'DONT CHANGE THAT DIAL!',
                   'THIS IS A TRANSMISSION FROM THE FUTURE',
                   'IMAGINE IF YOU WILL A CLOCK THAT COULD PLAY GAMES',
                   'IS IT THAT TIME AGAIN?',
                   'PREVIOUSLY ON CLOCK...',
                   'THANKS FOR TUNING IN',
                   'YOU WONT BELIEVE WHAT HAPPENS NEXT',
                   'MISSED IT BY THAT MUCH!',
                   'CAN YOU DIG IT?',
                   'IM BACK BABY'
                   
      )
                   
  elif (MessageType == 'SHORTGAME'):
    #12 characters
    MessageList = ('A DOT GAME',
                   'REIMAGINED',
                   'BY DATAGOD',
                   'AN ODDITY',
                   'A CLOCK GAME',
                   'RGB MATRIX',
                   'A FUN PROJECT',
                   'ON YOUR CLOCK',
                   'FUN TIMES',
                   'PI POWERED',
                   'BLOW YER MIND',
                   'ULTIMATE TIME',
                   'TIME SQUARED',
                   'ITS ABOUT TIME',
                   'TIME TO RUN',
                   'END TIMES',
                   'NO TIME LEFT',
                   'SHOW TIME!',
                   'OUTTA TIME!',
                   'KNOCK KNOCK!',
                   'READY?',
                   'GO!'

      )
  
  
  ListCount = len(MessageList)
  print(ListCount)
  print("ListCount:",ListCount)
  i = 0
  Message = ''
  #Message = MessageList(random.randint(0,ListCount-1))
  Message = random.choice(MessageList)
  print("Message:",Message)
  return Message




def EraseMessageArea(LinesFromBottom = 5):
  for x in range (0,HatWidth):
    for y in range (HatHeight-LinesFromBottom,HatHeight):
      setpixel(x,y,0,0,0)



def IsSpotEmpty(h,v):
  r,g,b = getpixel(h,v)
  if (r > 0 or g > 0 or b > 0):
    return False
  else:
    return True


  
def GetBrightAndShadowRGB():
  #get a bright color and find a shadow that is one 20th the brightness
  i = random.randint(1,7)
  BrightRGB = GlowingTextRGB[i]
  ShadowRGB = GlowingShadowRGB[i]

  return BrightRGB, ShadowRGB






def ShowTitleScreen(
  BigText          = 'BIGTEXT',
  BigTextRGB       = HighBlue,
  BigTextShadowRGB = ShadowBlue,

  LittleText          = 'LITTLE TEXT',
  LittleTextRGB       = HighRed,
  LittleTextShadowRGB = ShadowRed, 
  
  ScrollText    = 'SCROLLING TEXT',
  ScrollTextRGB = HighYellow,
  ScrollSleep   = 0.05,    #how long to wait between each frame of scrolling
  DisplayTime   = 5,       #how long to wait before exiting
  ExitEffect   = True
  ):


  global ScreenArray  
  #Draw the Big text
  #Clear only the LED matrix
  #Draw the next size down
  #When at the final zoom level
  #  - clear the LED Matrix
  #  - clear all buffers (canvas and ScreenArray[V][H])
  #  - draw the text at desired last zoom level
  #  - draw the rest of the text, at this point it is all written to ArrayBuffer
  #  - clear the LED Matrix
  #  - clear all buffers (canvas and ScreenArray[V][H])
  #Call the ZoomScreen function to redraw the display using ScreenArray[V][H] which at this point
  #contains the values last written to the screen.

  BigText    = BigText.upper()
  LittleText = LittleText.upper()
  ScrollText = ScrollText.upper()




  TheMatrix.Clear()
  ClearBuffers()
  


  #Big Text
  TheMatrix.Clear()
  ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=0,Text=BigText,RGB=BigTextRGB,ShadowRGB=BigTextShadowRGB,ZoomFactor= 8,GlowLevels=0,DropShadow=False)
  TheMatrix.Clear()
  ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=1,Text=BigText,RGB=BigTextRGB,ShadowRGB=BigTextShadowRGB,ZoomFactor= 7,GlowLevels=0,DropShadow=False)
  TheMatrix.Clear()
  ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=1,Text=BigText,RGB=BigTextRGB,ShadowRGB=BigTextShadowRGB,ZoomFactor= 6,GlowLevels=0,DropShadow=False)
  TheMatrix.Clear()
  ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=1,Text=BigText,RGB=BigTextRGB,ShadowRGB=BigTextShadowRGB,ZoomFactor= 5,GlowLevels=0,DropShadow=False)
  TheMatrix.Clear()
  ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=1,Text=BigText,RGB=BigTextRGB,ShadowRGB=BigTextShadowRGB,ZoomFactor= 4,GlowLevels=0,DropShadow=False)
  TheMatrix.Clear()
  ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=1,Text=BigText,RGB=BigTextRGB,ShadowRGB=BigTextShadowRGB,ZoomFactor= 3,GlowLevels=0,DropShadow=False)
  TheMatrix.Clear()
  ClearBuffers() #We do this to erase our ScreenArray (which we draw to manually because we cannot read the matrix as a whole)
  ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=1,Text=BigText,RGB=BigTextRGB,ShadowRGB=BigTextShadowRGB,ZoomFactor= 2,GlowLevels=0,DropShadow=True)
  

  time.sleep(0.5)

  #Little Text
  #BrightRGB, ShadowRGB = GetBrightAndShadowRGB()
  ShowGlowingText(CenterHoriz=True,h=0,v=14,Text=LittleText,RGB=LittleTextRGB,ShadowRGB=LittleTextShadowRGB,ZoomFactor= 1,GlowLevels=100,DropShadow=True)

  

  #Scrolling Message
  EraseMessageArea(LinesFromBottom=6)
  BrightRGB, ShadowRGB = GetBrightAndShadowRGB()
  ShowScrollingBanner2(ScrollText,ScrollTextRGB,ScrollSpeed=ScrollSleep,v=25)



  time.sleep(DisplayTime)

  #Pick a random special affect
 
  if(ExitEffect == 0):
    r = random.randint(0,3)
    if (r == 0):
      #Zoom out
      print('Random Zoom out')
      ZoomScreen(ScreenArray,32,256,Fade=True,ZoomSleep=0.01)
    elif (r == 1):
      #Shrink
      print('Random Shrink')
      ZoomScreen(ScreenArray,32,1,Fade=True,ZoomSleep=0.01)
    elif (r == 2):
      #Bounce1
      print('Random Bounce1')
      ZoomScreen(ScreenArray,32,5,Fade=False,ZoomSleep=0.005)
      ZoomScreen(ScreenArray,6,128,Fade=True,ZoomSleep=0)
    elif (r == 3):
      #Bounce2
      print('Random Bounce2')
      ZoomScreen(ScreenArray,32,42,Fade=False,ZoomSleep=0.015)
      ZoomScreen(ScreenArray,42,1,Fade=True,ZoomSleep=0.0)

  elif(ExitEffect == 1):
      #Zoom out
      print('Zoom out')
      ZoomScreen(ScreenArray,32,256,Fade=True,ZoomSleep=0.01)
  elif(ExitEffect == 2):
      #Shrink
      print('Shrink')
      ZoomScreen(ScreenArray,32,1,Fade=True,ZoomSleep=0.01)
  elif(ExitEffect == 3):
      #Bounce
      print('Bounce')
      ZoomScreen(ScreenArray,32,10,Fade=False,ZoomSleep=0.005)
      ZoomScreen(ScreenArray,11,128,Fade=True,ZoomSleep=0)

    
  


def MoveAnimatedSpriteAcrossScreen(TheSprite,v=0,direction="right",steps=1,ZoomFactor=1,sleep=0.1):

  h = 0

  if (direction == "right"):
    #start the sprite completely of screen
    h = 0 - TheSprite.width

    while (h <= HatWidth):
      for i in range (1,TheSprite.frames+1):
        TheSprite.currentframe = i
        CopyAnimatedSpriteToPixelsZoom(TheSprite,h=h,v=v, ZoomFactor=ZoomFactor)
        time.sleep(sleep)
      h = h + steps



  if (direction == "left"):
    #start the sprite completely of screen
    h = HatWidth + 1

    while (h >= (0- TheSprite.width)):
      for i in range (1,TheSprite.frames+1):
        TheSprite.currentframe = i
        CopyAnimatedSpriteToPixelsZoom(TheSprite,h=h,v=v, ZoomFactor=ZoomFactor)
        time.sleep(sleep)
      h = h - steps

