# %%

import LEDarcade as LED
import GlobalVariables as gv
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time


#Variable declaration section
ScrollSleep = 0.025



print ("---------------------------------------------------------------")
print ("WELCOME TO THE LED ARCADE             ")
print ("")
print ("BY DATAGOD")
print ("")
print ("This program will demonstrate several LED functions that have")
print ("been developed as part of the Arcade Retro Clock RGB project.")
print ("---------------------------------------------------------------")
print ("")
print ("")





#This allows you to create a title screen with different size text
#some scrolling text, an animation and even a nice fade to black

#LED.ClearBuffers()
LED.ShowTitleScreen(
  BigText             = 'LED FUN',
  BigTextRGB          = LED.HighGreen,
  BigTextShadowRGB    = LED.ShadowGreen,
  LittleText          = 'HACKATHON',
  LittleTextRGB       = LED.HighRed,
  LittleTextShadowRGB = LED.ShadowRed, 
  ScrollText          = 'CLONE THIS PROJECT AND START CONTRIBUTING',
  ScrollTextRGB       = LED.HighYellow,
  ScrollSleep         = ScrollSleep, # time in seconds to control the scrolling (0.005 is fast, 0.1 is kinda slow)
  DisplayTime         = 2,           # time in seconds to wait before exiting 
  ExitEffect          = 0            # 0=Random / 1=shrink / 2=zoom out / 3=bounce 
  )









