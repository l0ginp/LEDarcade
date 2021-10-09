# LEDarcade
 A collection of classes and functions for animated text and graphics on an Adafruit LED Matrix.

Follow us on Facebook: https://www.facebook.com/ArcadeRetroClock

![ArcadeRetroClockTitleSmall](https://user-images.githubusercontent.com/7650580/112741888-64bd8200-8f57-11eb-9737-7b443b0ef523.jpg)

Watch the Video: https://youtu.be/Z9uW0MQYcrE?t=10

## Background
Arcade Retro Clock started out as a project on an 8x8 matrix.  Over the years it has been converted to 16x16 and now 64x32.  Each conversion process involved solving many bugs and enhancing the game play especially with respects to the computer's ability to play against itself.

For LEDarcade, I decided to isolate classes, functions, sprites, etc. that are used specifically for displaying messages and animations and to exclude any functions used to control the specific games.

## Examples
There are 4 games that have been converted to this new playform so far.
<BR><BR>
 ![OutbreakTitle](https://user-images.githubusercontent.com/7650580/112741795-a13cae00-8f56-11eb-876c-cc1321538479.jpg)

 Watch the video: https://youtu.be/Z9uW0MQYcrE?t=260
 
<BR><BR>
![PacDotTitleSmall](https://user-images.githubusercontent.com/7650580/112771840-ce8f6780-8ffb-11eb-84b0-9d89e4e62e90.jpg)

<BR><BR>
![TronTitleSmall](https://user-images.githubusercontent.com/7650580/112741779-7fdbc200-8f56-11eb-92c7-7f0e9058166f.jpg)

<BR><BR>
![AstroSmashTitleSmall](https://user-images.githubusercontent.com/7650580/112771883-fd0d4280-8ffb-11eb-8871-918ced7526c7.jpg)


## Requirements
<BR>Raspberry Pi 3 and up
<BR>Adafruit LED Matrix (64x32)
<BR>Adafruit RGB Hat
<BR>hzeller's RBG LED Matrix code: https://github.com/hzeller/rpi-rgb-led-matrix


## Usage
Modify the test.py script to contain the messages you want to display.  Then execute by issuing the comand:
 ~~~
 sudo python3 test.py
 ~~~
 
![Usage](https://github.com/datagod/LEDarcade/blob/main/images/BIGLED_Usage.jpg )
 
 

 
 
 
