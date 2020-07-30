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
  
Further optimizations: decrease rendering area + decrease palette and random selection, add frameskip, this will make fire less realistic, but faster.  
  
P.S. Demo gif was speeded up 10x times