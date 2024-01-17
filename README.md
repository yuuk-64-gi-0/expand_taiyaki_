# expand_taiyaki_
## Abstract
This python program files provide 2D visualizer for \_taiyaki\_ stream.

## Requirements
* OS:Windows 10 or 11
* Software:python3 (Not anaconda, recommended: version 3.11)

## Quick guide for using
* Please double click "Launch_in_venv.bat" to start this program easy.
If it is the first time to launch, required python libraries will be installed to script/venv via pip commands.
Then "Controller \[0-9\]" and "Image window \[0-9\]" will appear on your screen.
* When you want to terminate this program, please do one of the following three things.
    1. Click close button of "Controller \[0-9\]"
    2. Click close button of "Image window \[0-9\]"
    3. Make "Image window \[0-9\]" active and push ESC-key

    __Do not close console window. The program will terminate, but next launch will not perform correctly.__

## Usage
![""](Images_for_README/Controller_window_normal.png)
#### Buttons
* add image window:Generates a new window with settings linked to it. When one of the Image windows is closed, the program continues to run if another Image window remains.
* read config:Launches File Manager and input the configuration file contents selected in the Controller window.
* export config:Launches File Manager and export the configuration to the file at selected path.
* read default:Resets the configuration to their defaults.
#### Entries
* channel (pull down):A microphone device you use.
* gain apm.% (float entry):The gain amplitude rate of volume from microphone.
* image file (file manager):Click and select the image file (PNG, Jpeg, BMP etc) for showing in Image window.
* display (pull down):Switches whether the image is shown or hidden.
* pos x (integer entry):The horizontal position of image from left edge of the Image window (right direction is positive). Unit is pixel.
* pos y (integer entry):The vertical position of image from bottom edge of the Image window (upper direction is positive). Unit is pixel.
* img W_scale (float entry):The width scale of image. 1.0 is the original width.
* min img H_scale (float entry):The height scale of image when no sounds input. 1.0 is the original width.
* max img H_scale (float entry):The height scale of image when upper limit sounds input. 1.0 is the original width.
* expand mode (pull down):Sorry, I'll omit the explanation, but linear is recommended.
* window height (integer entry):window height of Image window. Unit is pixel.
* window width (integer entry):window width of Image window. Unit is pixel.
* bg color (string entry):background color of Image window. Hex type color code (ex.: "#00FF99" or "#0F9") and color name are available.

## Requirements (python libraries)
__If you launch the program from "Launch_in_venv.bat", you do not need to install these libraries beforehand.__
* numpy>=1.24.4
* Pillow>=10.0.0
* PyAudio>=0.2.12
* pygame>=2.3.0
* webcolors>=1.13


