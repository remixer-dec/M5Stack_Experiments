# UART-based camera.
The goal is to take a photo using UnitV, and transfer it to StickC and show it on the screen.  
![Demo](https://i.imgur.com/SvZs45s.gif)
  
Challenges:  
1) Current version of UIFlow doesn't allow to load photos from RAMFS (Kernel panic)  
Solution: either save them to ROM or draw them pixel-by-pixel or use custom JPEG decoder. This project uses the second approach. 
  
2) UIFlow doesn't have Image library that can load images from byte arrays  
Solution: use arrays with colors to store, read and write image data  
  
3) StickC doesn't have enough RAM to store received bytearray.  
Solution: read received byte array and store its data in a typed int array, which uses less memory  
  
4) Light colors use more memory and UART input can have different length, which can corrupt bytearray to array transformation  
Solution: append to array only amount of data that can be divided by 4, which is the number of bytes for int in bytearray.  
  
5) Transferring data via UART is the slowest part of the process.  
Solution: (not implemented yet in this project) Use UARTHS (high-speed UART interface) in UnitV.
  
UnitV code is [here](https://github.com/remixer-dec/M5Stack_Experiments/blob/master/UnitV/MaixPy/UARTCamera)