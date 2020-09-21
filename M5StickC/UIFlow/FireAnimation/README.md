I saw fire animation project for m5StickC written in C by MajorSnags and decided to implement it in Micropython.  
C Project Source: https://m5stack.hackster.io/MajorSnags/m5stickc-flame-demo-ee6672  
Original Source: https://lodev.org/cgtutor/fire.html  

![Demo](https://i.imgur.com/ruA7uP6.gif)

Challenges:  
1) List memory is limited, I was only able to render 80*40 pixel lists  
Solution: use array module and arrays with short numbers ('H')  
  
2) Random implementation is different, no hsl module  
Solution: implement them yourself or find a working open-source implementation

3) It runs really slow  
Solution: use @micropython.native where it's possible and @micropython.viper only for heavy calculations, avoid floating points and precise division.  
  
Extra Optimizations:  
* pixel-skip - render a pixel only if its color is not empty / not current background color (0x000000)  
* 2func - separate fire pixel calculations and rendering into two functions  
* natmod - use C language to create a native module for computation part  

### Speed comparison (frame time in ms)  

| variation                                          | 1st frame time | 100th frame time | hard reboot required |
|----------------------------------------------------|----------------|------------------|----------------------|
| natmod \+ @viper rendering \(mpy\-cross compiled\) | 93             | 940              | yes                  |
| natmod no\-pixel\-skip \+ @viper rendering         | 966            | 966              | yes                  |
| natmod \+ @viper rendering                         | 112            | 972              | yes                  |
| @viper \+ 2func                                    | 242            | 1073             | yes                  |
| natmod \+ @native rendering                        | 251            | 1180             | yes                  |
| @viper                                             | 261            | 1383             | yes                  |
| @native \+ 2func                                   | 582            | 1484             | yes                  |
| @native                                            | 567            | 1759             | yes                  |
| natmod \+ pure python rendering                    | 607            | 1768             | no                   |
| pure python                                        | 2036           | 3545             | no                   |
| pure python  \+ 2func                              | 2222           | 3566             | no                   |
  
To use precompiled fullfire binary, try importing it inside a function if you face any errors.
  
Further optimizations: decrease rendering area + decrease palette and random selection, add frameskip, this will make fire less realistic, but faster.  
  
P.S. Demo gif was speeded up 10x times