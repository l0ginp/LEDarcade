# %%

import LEDarcade as LED
import GlobalVariables as gv
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time



print ("hello")



ScrollSleep = 0.05


TheMessage = "THIS IS SCROLLING TEXT"

print ("--------------------------------------")
print ("WELCOME TO THE LED ARCADE             ")
print ("")
print ("BY DATAGOD")
print ("--------------------------------------")
print ("")
print ("")



#LED.ClearBuffers()
LED.ShowTitleScreen(
  BigText             = 'BIGTEXT',
  BigTextRGB          = LED.HighGreen,
  BigTextShadowRGB    = LED.ShadowGreen,
  LittleText          = 'LITTLE TEXT',
  LittleTextRGB       = LED.HighRed,
  LittleTextShadowRGB = LED.ShadowRed, 
  ScrollText          = 'THE END',
  ScrollTextRGB       = LED.HighYellow,
  ScrollSleep         = 0.025,
  DisplayTime         = 2,      # time in seconds to wait before exiting 
  ExitEffect          = 0       # 0=Random / 1=shrink / 2=zoom out / 3=bounce 
  )



#LED.ShowIPAddress()



#gv.TheMatrix.Clear()
#gv.Canvas.Clear()
#LED.ClearBuffers()




