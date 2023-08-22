# image editor 
uses custom scripting language to load and manipulate images like traditional image editors, running the main "gui" should give you a live preview of the resulting image. 

.ed files for "edit", basically python syntax

all numbers are floats for compatability with functions (minimize errors from passing int when expecting float)

loop refactor stuff:
 scanline(0)
    first function scanned is [print]
    scanline(6) starts scanning inside [()]
        is the first char a string starter " ' ?
        no
            extract expression
            evaluate expression (function):
        

