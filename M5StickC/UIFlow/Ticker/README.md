A ticker for M5StickC with UIFlow firmware  
![Demo](https://i.imgur.com/6XNFoWJ.gif)

Color, speed, max. text length, position, type and delay are configurable, screen rotation parameter defines default text length limit.  
This code does not override default UIFlow auto-linebreak behavior. See the .py file for examples.
Default text length limit might look like it's smaller than the screen size, but it actually tries to avoid linebreaks of long Unicode characters, you can increase it manually, passing limit=number argument.