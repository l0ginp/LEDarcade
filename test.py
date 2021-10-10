# %%

import LEDarcade as LED
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
import random

#Variable declaration section
ScrollSleep   = 0.025
HatHeight = 32
HatWidth  = 64


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






#--------------------------------------
#  SHOW TITLE SCREEN                 --
#--------------------------------------


#This allows you to create a title screen with different size text
#some scrolling text, an animation and even a nice fade to black

LED.ShowTitleScreen(
  BigText             = 'L.E.D.',
  BigTextRGB          = LED.HighGreen,
  BigTextShadowRGB    = LED.ShadowGreen,
  LittleText          = 'ARCADE',
  LittleTextRGB       = LED.HighRed,
  LittleTextShadowRGB = LED.ShadowRed, 
  ScrollText          = 'HACKATHON 2021',
  ScrollTextRGB       = LED.HighYellow,
  ScrollSleep         = ScrollSleep, # time in seconds to control the scrolling (0.005 is fast, 0.1 is kinda slow)
  DisplayTime         = 1,           # time in seconds to wait before exiting 
  ExitEffect          = 0            # 0=Random / 1=shrink / 2=zoom out / 3=bounce 
  )






#--------------------------------------
#  SHOW SIMPLE SPRITES               --
#--------------------------------------



LED.ClearBuffers() #clean the internal graphic buffers
LED.ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=1,Text='PLAIN',RGB=LED.HighCyan,ShadowRGB=LED.ShadowCyan,ZoomFactor= 2,GlowLevels=25,DropShadow=True)
LED.ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=12,Text='SPRITES',RGB=LED.HighCyan,ShadowRGB=LED.ShadowCyan,ZoomFactor= 2,GlowLevels=25,DropShadow=True)
time.sleep(1)

for x in range(1,10):
  #Currently there are 27 colorful "bright" RGB values, stored in BrightColorList[].
  GhostRGB = LED.BrightColorList[random.randint(1,LED.BrightColorCount)]
  LED.CopySpriteToPixelsZoom(LED.BlueGhostSprite,random.randint(5,45),random.randint(0,20), ColorTuple=GhostRGB,ZoomFactor=random.randint(1,6),Fill=False)
  time.sleep(0.25)
  LED.CopySpriteToPixelsZoom(LED.PacSprite,random.randint(5,45),random.randint(0,20), ColorTuple=LED.HighYellow,ZoomFactor=random.randint(1,2),Fill=False)
  time.sleep(0.25)


#--------------------------------------
#  ZOOM AND GLOW SPRITES             --
#--------------------------------------

LED.ClearBigLED()
LED.ClearBuffers() #clean the internal graphic buffers
LED.ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=1,Text='ZOOMED',RGB=LED.HighCyan,ShadowRGB=LED.ShadowCyan,ZoomFactor= 2,GlowLevels=25,DropShadow=True)
LED.ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=12,Text='SPRITES',RGB=LED.HighCyan,ShadowRGB=LED.ShadowCyan,ZoomFactor= 2,GlowLevels=25,DropShadow=True)
time.sleep(1)
LED.ShowGlowingSprite(CenterHoriz=True,CenterVert=False,h=0,v=0,TheSprite=LED.BlueGhostSprite,RGB=LED.HighOrange,ShadowRGB=LED.ShadowOrange,ZoomFactor= 1,GlowLevels=100,FadeLevels=50,DropShadow=True,FadeDelay=0)
LED.ShowGlowingSprite(CenterHoriz=True,CenterVert=False,h=0,v=0,TheSprite=LED.BlueGhostSprite,RGB=LED.HighOrange,ShadowRGB=LED.ShadowOrange,ZoomFactor= 2,GlowLevels=100,FadeLevels=50,DropShadow=True,FadeDelay=0)
LED.ShowGlowingSprite(CenterHoriz=True,CenterVert=False,h=0,v=0,TheSprite=LED.BlueGhostSprite,RGB=LED.HighOrange,ShadowRGB=LED.ShadowOrange,ZoomFactor= 3,GlowLevels=100,FadeLevels=50,DropShadow=True,FadeDelay=0)
LED.ShowGlowingSprite(CenterHoriz=True,CenterVert=False,h=0,v=0,TheSprite=LED.BlueGhostSprite,RGB=LED.HighOrange,ShadowRGB=LED.ShadowOrange,ZoomFactor= 4,GlowLevels=100,FadeLevels=50,DropShadow=True,FadeDelay=0)
LED.ShowGlowingSprite(CenterHoriz=True,CenterVert=False,h=0,v=0,TheSprite=LED.BlueGhostSprite,RGB=LED.HighOrange,ShadowRGB=LED.ShadowOrange,ZoomFactor= 5,GlowLevels=100,FadeLevels=50,DropShadow=True,FadeDelay=0)
LED.ShowGlowingSprite(CenterHoriz=True,CenterVert=False,h=0,v=0,TheSprite=LED.BlueGhostSprite,RGB=LED.HighOrange,ShadowRGB=LED.ShadowOrange,ZoomFactor= 6,GlowLevels=100,FadeLevels=50,DropShadow=True,FadeDelay=0)



#--------------------------------------
#  SHOW COLOR ANIMATED SPRITES       --
#--------------------------------------


LED.ClearBuffers() #clean the internal graphic buffers
LED.ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=1,Text='MOVING',RGB=LED.HighCyan,ShadowRGB=LED.ShadowCyan,ZoomFactor= 2,GlowLevels=25,DropShadow=True)
LED.ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=12,Text='SPRITES',RGB=LED.HighCyan,ShadowRGB=LED.ShadowCyan,ZoomFactor= 2,GlowLevels=25,DropShadow=True)
time.sleep(1)

#Show 8x8 sprites zoomed
for x in range(1,75):
  #Currently there are 27 colorful "bright" RGB values, stored in BrightColorList[].
  LED.CopyAnimatedSpriteToPixelsZoom(LED.DotZerkRobotWalkingSmall,h=28,v=22, ZoomFactor=2)
  LED.CopyAnimatedSpriteToPixelsZoom(LED.DotZerkRobot,h=5,v=16, ZoomFactor=2)
  LED.CopyAnimatedSpriteToPixelsZoom(LED.ChickenRunning,h=45,v=18, ZoomFactor=2)
  time.sleep(0.05)





#--------------------------------------
#  ANIMATIONS                        --
#--------------------------------------



#Show small animations


LED.ClearBuffers() #clean the internal graphic buffers
LED.ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=8,Text='PACMAN',RGB=LED.HighYellow,ShadowRGB=LED.ShadowYellow,ZoomFactor= 2,GlowLevels=25,DropShadow=True)
LED.ThreeGhostPacSprite.ScrollAcrossScreen(0,26,'right',ScrollSleep)
LED.ThreeBlueGhostPacSprite.ScrollAcrossScreen(HatWidth,26,'left',ScrollSleep)


LED.ClearBuffers() #clean the internal graphic buffers
LED.ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=8,Text='CHICKN',RGB=LED.HighOrange,ShadowRGB=LED.ShadowOrange,ZoomFactor= 2,GlowLevels=25,DropShadow=True)
LED.ChickenRunning.ScrollAcrossScreen(HatWidth,24,'left',ScrollSleep)
LED.ChickenRunning.HorizontalFlip()
LED.ChickenRunning.ScrollAcrossScreen(0,24,'right',ScrollSleep)

LED.ClearBuffers() #clean the internal graphic buffers
LED.ShowGlowingText(CenterHoriz=True,CenterVert=False,h=0,v=8,Text='WORMZ',RGB=LED.HighPink,ShadowRGB=LED.ShadowPink,ZoomFactor= 2,GlowLevels=25,DropShadow=True)
LED.ChickenChasingWorm.ScrollAcrossScreen(HatWidth,23,'left',ScrollSleep * 2)  #make this one a little slower
LED.WormChasingChicken.HorizontalFlip()
LED.WormChasingChicken.ScrollAcrossScreen(0,23,'right',ScrollSleep *1.5 )






  




