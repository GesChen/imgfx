import cv2
import numpy as np
import os 
import curses
import threading 

# no guides, full naive method ahead... watch out!

def custom_print(text):
    global terminal
    
    terminal.append(text)

def ERROR(reason, line):
    custom_print(f'Error: {reason} (Line {line})')  

def curses_main(stdscr):
    global terminal
    stdscr.clear()

    
    while True:
        stdscr.clear()

        for l, line in enumerate(terminal):
            stdscr.addstr(l, 0, line)
        
        stdscr.refresh()

def curses_thread():
    curses.wrapper(curses_main)

functions = {
    'print' : {'function':custom_print, 'args':1}
}

edit_filepath = r'D:\Projects\Programming\Python Scripts\.image effects\imgfx\editor\test.ed'

# seperate thread for terminal output
cThread = threading.Thread(target=curses_thread)
cThread.start()

while True: 
    terminal = []
    # scan lines
    with open(edit_filepath, 'r') as file:
        # TODO: SPLIT INTO MULTIPLE FUNCTIONS
        for l, line in enumerate(file):
            # scan through line
            function = ''
            for c, char in enumerate(line):
                if char == '#':
                    break
                if char == '(':
                    if function in functions.keys(): #is a real function?
                        # get args
                        ai = c # arg index
                        accum = ''
                        args = []
                        inString = False
                        while line[ai + 1] != ')':
                            ai += 1
                            charInArg = line[ai]
                            if ai == len(line) - 1: # endofline but no break? error. 
                                ERROR("Unclosed parentheses", l)
                                charInArg = line[ai - 1]
                                if inString and not(charInArg == "'" or charInArg == '"'):
                                    ERROR("Unclosed string", l)
                                break

                            if charInArg == '"' or charInArg == "'": #hit start/end of string arg?
                                inString = not inString #toggle
                                continue #skip this char 

                            elif charInArg == "," and not inString: #new arg
                                args.append(accum) #append to list
                                accum = '' #reset accum
                                continue #skip this char

                            
                            accum += charInArg
                        args.append(accum)
                        # check to make sure the args given match expected
                        expected = functions[function]['args']
                        if len(args) != expected:
                            ERROR(f"Expected {expected} arguments, got {len(args)} instead", l)

                        functions[function]['function'](*args) #execute func and pass args
                        break
                    else:
                        ERROR(f"Unknown function {function}", l)
                        break
                function += char
            