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
    reason = str(reason)
    lastLeftParentheses = reason.rfind('(') if '(' in reason else len(reason) + 1
    print_(f'Error: {reason[:lastLeftParentheses - 1]} (Line {line + 1})')  

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

def preview_thread():
    while True:
        if currently_editing is not None:
            dimensions = currently_editing.shape[:2][::-1]
            factor = dimensions[0] / 1000
            resized = cv2.resize(currently_editing, (int(dimensions[0] / factor), int(dimensions[1] / factor)))
            cv2.imshow("Image", cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))
            cv2.waitKey(1)

def edit(path):
    global currently_editing
    currently_editing = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)

def rgb2bgr(col):
    return col[::-1]

def dim():
    print_(currently_editing.shape[:2][::-1])

## image editing functions
def rectangle(x1, y1, x2, y2, color, thickness):
    global currently_editing
    cv2.rectangle(currently_editing, (x1, y1), (x2, y2), rgb2bgr(color), thickness)

edit_filepath = r'D:\Projects\Programming\Python Scripts\.image effects\imgfx\editor\test.ed'

terminal = []

# seperate thread for terminal output
cThread = threading.Thread(target=curses_thread, name="Curses")
cThread.start()

# another thread for image preview
pThread = threading.Thread(target=preview_thread, name="Preview")
pThread.start()

# session variables
variables = {}
currently_editing = None

lasthash = ''
while True: 
    variables = {}
    terminal = [0]

    current_hash = get_file_hash(edit_filepath)
    # scan lines
    if current_hash != lasthash: #only process file if it has changed
        lasthash = current_hash
        with open(edit_filepath, 'r') as file:
            for l, line in enumerate(file):
                line = line.replace('print', 'print_')
                try: 
                    exec(line.strip())
                except Exception as e:
                    ERROR(e, l)

            terminal[0] = 1 # terminal is ready to be printed
    time.sleep(.01)