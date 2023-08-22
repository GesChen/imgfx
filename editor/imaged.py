import cv2
import numpy as np
import os 
import curses
import threading 
import hashlib
import time

# no guides, full naive method... watch out, bad code ahead!

def get_file_hash(file_path):
    with open(file_path, 'rb') as file:
        return hashlib.md5(file.read()).hexdigest()

def print_(text):
    global terminal
    terminal.append(text)

def ERROR(reason, line):
    print_(f'Error: {reason} (Line {line + 1})')  

def curses_main(stdscr):
    global terminal
    stdscr.clear()

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) #type:ignore
    ERROR_COLOR = curses.color_pair(1)                        #type:ignore
    
    while True:
        if terminal[0] == 1:
            stdscr.erase()

            for l, line in enumerate(terminal[1:]):
                line = str(line)
                if line[:5] == "Error":
                    stdscr.addstr(l, 0, line, ERROR_COLOR)
                else:
                    stdscr.addstr(l, 0, line)
                
            stdscr.refresh()
            terminal[0] = 0

def curses_thread():
    curses.wrapper(curses_main) # type: ignore (random bug not sure why happens)

def image_init(path):
    return

functions = {
    'print' : {'function':print_, 'args':1},
    'init'  : {'function':image_init,   'args':1}
}

edit_filepath = r'D:\Projects\Programming\Python Scripts\.image effects\imgfx\editor\test.ed'

# seperate thread for terminal output
cThread = threading.Thread(target=curses_thread, name="Curses")
cThread.start()

# session variables
variables = {}

lasthash = ''
while True: 
    variables = {}
    terminal = [0]

    current_hash = get_file_hash(edit_filepath)

    # scan lines
    if current_hash != lasthash: #only process file if it has changed
        lasthash = current_hash
        with open(edit_filepath, 'r') as file:
            # TODO: SPLIT INTO MULTIPLE FUNCTIONS
            for l, line in enumerate(file):
                # scan through line
                function = ''
                for c, char in enumerate(line):
                    if   char == '#': #comments
                        break
                    elif char == '(': #functions 
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
                                    if accum in variables.keys():
                                        accum = variables[accum]
                                    args.append(accum) #append to list
                                    accum = '' #reset accum
                                    continue #skip this char

                                accum += charInArg
                            if accum in variables.keys():
                                accum = variables[accum]
                            args.append(accum)
                            # check to make sure the args given match expected
                            expected = functions[function]['args']
                            if len(args) != expected:
                                ERROR(f'Function "{function}" expects {expected} arguments, got {len(args)} instead', l)
                                break

                            functions[function]['function'](*args) #execute func and pass args
                            break
                        else:
                            ERROR(f"Unknown function {function}", l)
                            break
                    elif char == '=': #variables
                        value = line[c+2:].strip()
                        if value[0] == '"' or value[0] == "'":
                            if value[-1] != "'" and value[-1] != '"':
                                ERROR(f"Unclosed string", l)
                                break
                            value = value[1:-1]
                        elif value.isnumeric():
                            value = float(value)
                        variables[function.strip()] = value
                        #function[:-1]
                        break
                    function += char
            terminal[0] = 1 # terminal is ready to be printed
    time.sleep(.01)