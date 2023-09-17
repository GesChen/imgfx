import cv2
import numpy as np
import scipy as sp
import os
import sys
import win32gui, win32con
import threading
import time

import pygame as pyg
import curses

from screeninfo import get_monitors
from hashlib import md5
from time import sleep

## supporting functions
def is_path(string):
    return os.path.isabs(string) or os.path.exists(string)

def get_file_hash(file_path):
    with open(file_path, 'rb') as file:
        return md5(file.read()).hexdigest()

def handle_replacements(line):
    if line[0].isspace():
        line = line.lstrip()
        line = '\t' + line
    line = line.replace('print', 'print_')
    line = line.replace('time', 'timeElapsed')
    return line

## display
def print_(text):
    global terminal
    terminal.append(text)

def ERROR(reason, line):
    reason = str(reason)
    #lastLeftParentheses = reason.rfind('(') if '(' in reason else len(reason) + 1
    #print_(f'Error: {reason[:lastLeftParentheses - 1]} (Line {line + 1})')
    print_(f'Error: {reason} (Line {line + 1})')

def curses_main(stdscr):
    global terminal
    global lines
    stdscr.clear()

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) #type:ignore
    ERROR_COLOR = curses.color_pair(1)                        #type:ignore

    while running:
        if lineNo < len(list(lines)):
            barlength = 20
            
            progress = lineNo / len(list(lines))
            chars = round(progress * barlength)
            progressText = f"Processing: [{'='*chars}{'-'*(barlength - chars)}] {progress:.2f}%"

            stdscr.addstr(0, 0, progressText)

        if terminal[0] == 1:
            hold = True
            stdscr.clear()
            stdscr.addstr(0, 0, f"Finished processing, took {(time.time() - iterationStartTime):.2f} seconds.")
            stdscr.refresh()

            for l, line in enumerate(terminal[1:]):
                line = str(line)
                try:
                    if line[:5] == "Error":
                        stdscr.addstr(l + 1, 0, repr(line).strip("'"), ERROR_COLOR)
                    else:
                        stdscr.addstr(l + 1, 0, repr(line).strip("'"))
                except:
                    pass
            
            terminal[0] = 0
            hold = False
        stdscr.refresh()

def curses_thread():
    curses.wrapper(curses_main) # type: ignore (random bug not sure why happens)

def preview_thread_old():
    while True:
        if IMAGE.shape[0] != 0:
            dimensions = IMAGE.shape[:2][::-1]
            factor = dimensions[0] / window_size
            resized = cv2.resize(IMAGE, (int(dimensions[0] / factor), int(dimensions[1] / factor)))
            cv2.imshow("Image", cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))
            cv2.waitKey(1)

def maximise_window(window_title):
    hwnd = win32gui.FindWindowEx(None, None, None, window_title)
    if hwnd != 0:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

def pyg_thread():
    pyg.init()
    clock = pyg.time.Clock()
    pyg.display.set_caption("Editor")

    lastScreen = None
    while running:
        clock.tick(60)
        events = pyg.event.get()

        check_for_resize(lastScreen)
        screen = update_screen(lastScreen)

        lastScreen = screen

        handle_events(events)
    
    # exit
    pyg.display.quit()
    pyg.quit()
    sys.exit()

def update_screen(lastScreen):
    global update
    global frame
    global update_frame

    frame += 1
    if IMAGE.shape[0] != 0 and update == True:
        update_frame += 1
        dimensions = IMAGE.shape[:2][::-1]
        factor = dimensions[0] / pyg.display.Info().current_w
        resized = cv2.resize(IMAGE, (int(dimensions[0] / factor), int(dimensions[1] / factor)))

        screen = pyg.display.set_mode(resized.shape[1::-1], pyg.RESIZABLE | pyg.HWSURFACE)
        pyimage = pyg.image.frombuffer(resized.tobytes(), resized.shape[1::-1], "RGB")
        screen.blit(pyimage, (0,0))
        
        
        pyg.display.flip()
        update = False
        
        if update_frame == 1:
            maximise_window("Editor")

        return screen
    return lastScreen

last_res = 0
def check_for_resize(screen):
    if screen is None:
        return

    global last_res
    global window_size
    global update

    res = screen.get_size()
    if res != last_res:
        window_size = res[0]
        update = True
    last_res = res

def handle_events(events):
    for event in events:
        if event.type == pyg.QUIT:
            global running
            running = False

## editing debug
def edit(path):
    global IMAGE
    IMAGE = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)

def dim():
    return IMAGE.shape[:2][::-1]

def save(path):
    if is_path(path):
        trysave(path)
    else:
        try: 
            path = os.path.join(os.getcwd(), path)
            trysave(path)
        except:
            print_("Unable to save. Path is not valid, or other error occured.")

def trysave(path):
    if os.path.isfile(path):
        print_("Found image found with same name. Generating new file name.")
    
    path = generate_unique_filename(path)

    cv2.imwrite(path, cv2.cvtColor(IMAGE, cv2.COLOR_BGR2RGB))
    print_("Saved image at " + path)

def generate_unique_filename(base_path):
    if not os.path.exists(base_path):
        return base_path

    directory, filename = os.path.split(base_path)
    filename_without_extension, file_extension = os.path.splitext(filename)

    counter = 1
    while True:
        new_filename = f"{filename_without_extension}_{counter}{file_extension}"
        new_path = os.path.join(directory, new_filename)
        if not os.path.exists(new_path):
            return new_path
        counter += 1

## color and math functions
def mapRange(value, from_min, from_max, to_min, to_max):
        slope = (to_max - to_min) / (from_max - from_min)
        return to_max + slope * (value - from_min)

def clamp(x, low, high):
        return max(low, min(high, x))

def lerp(a, b, t):
    return np.subtract(b, np.multiply(np.subtract(b, a), t))

def rgb2bgr(col):
    return col[::-1]

def hsv(h, s, v, a = 1):
        if h == 1: h = 0
        i = int(h*6)
        f = h * 6 - i

        w = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        match i:
                case 0: return(v, t, w, a)
                case 1: return(q, v, w, a)
                case 2: return(w, v, t, a)
                case 3: return(w, q, v, a)
                case 4: return(t, w, v, a)
                case 5: return(v, w, q, a)

def hex(hex):
    hex = hex.lstrip('#')

    r = int(hex[0:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:6], 16)

    return (r, g, b, 1)

## image editing functions
def rectangle(x1, y1, x2, y2, color, thickness):
    global IMAGE
    if len(color) == 3:
        cv2.rectangle(IMAGE, (x1, y1), (x2, y2), color[:3], thickness)
        return
    copy = IMAGE.copy()
    alpha = color[3]
    cv2.rectangle(copy, (x1, y1), (x2, y2), color[:3], thickness)
    cv2.addWeighted(copy, alpha, IMAGE, 1 - alpha, 0, IMAGE)
def rect(x1, y1, x2, y2, color, thickness):
    rectangle(x1, y1, x2, y2, color, thickness)

def line(x1, y1, x2, y2, color, thickness):
    global IMAGE
    if len(color) == 3:
        cv2.line(IMAGE, (x1, y1), (x2, y2), color[:3], thickness)
        return
    copy = IMAGE.copy()
    alpha = color[3]
    cv2.line(copy, (x1, y1), (x2, y2), color[:3], thickness)
    cv2.addWeighted(copy, alpha, IMAGE, 1 - alpha, 0, IMAGE)

def polygon(points, color, thickness, closed = True):
    global IMAGE
    if len(color) == 3:
        cv2.polylines(IMAGE, np.int32([points]), closed, color[:3], thickness)
        return
    copy = IMAGE.copy()
    alpha = color[3]
    print_(points)
    cv2.polylines(IMAGE, np.int32([points]), closed, color[:3], thickness)
    cv2.addWeighted(copy, alpha, IMAGE, 1 - alpha, 0, IMAGE)

def path(points, color, thickness):
    polygon(points, color, thickness, closed = False)

def text(x, y, content, color, thickness, size, font = 0):
    global IMAGE
    if len(color) == 3:
        cv2.putText(IMAGE, content, (x, y), font, size, color[:3], thickness)
        return
    copy = IMAGE.copy()
    alpha = color[3]
    cv2.putText(IMAGE, content, (x, y), font, size, color[:3], thickness)
    cv2.addWeighted(copy, alpha, IMAGE, 1 - alpha, 0, IMAGE)

def ellipse(x1, y1, x2, y2, color, thickness, rotation = 0, startAngle = 0, endAngle = 360):
    global IMAGE
    x =     int((x1 + x2) / 2)
    y =     int((y1 + y2) / 2)
    sizeX = int((x2 - x1) / 2)
    sizeY = int((y2 - y1) / 2)

    if len(color) == 3:
        cv2.ellipse(IMAGE, (x, y), (sizeX, sizeY), rotation, startAngle, endAngle, color[:3], thickness)
        return
    copy = IMAGE.copy()
    alpha = 1 - color[3]
    cv2.ellipse(IMAGE, (x, y), (sizeX, sizeY), rotation, startAngle, endAngle, color[:3], thickness)
    cv2.addWeighted(copy, alpha, IMAGE, 1 - alpha, 0, IMAGE)

def circle(x, y, radius, color, thickness):
    global IMAGE
    if len(color) == 3:
        cv2.circle(IMAGE, (x, y), radius, color[:3], thickness)
        return
    copy = IMAGE.copy()
    alpha = color[3]
    cv2.circle(IMAGE, (x, y), radius, color[:3], thickness)
    cv2.addWeighted(copy, alpha, IMAGE, 1 - alpha, 0, IMAGE)

def arc(x, y, radius, startAngle, endAngle, color, thickness):
    ellipse(x - radius, y - radius, x + radius, y + radius, color, thickness, 0, startAngle, endAngle)

def cubic_bezier(points, t):
    p = points

    q0 = lerp(p[0], p[1], t)
    q1 = lerp(p[1], p[2], t)
    q2 = lerp(p[2], p[3], t)

    r0 = lerp(q0, q1, t)
    r1 = lerp(q1, q2, t)

    point = lerp(r0, r1, t)
    return (int(point[0]), int(point[1]))

def bezier(x1, y1, x2, y2, x3, y3, x4, y4, color, thickness, samples = 20):
    points = np.array([
        cubic_bezier([
            (x1, y1),
            (x2, y2),
            (x3, y3),
            (x4, y4)],
            t / samples)
        for t in range(samples + 1)], dtype=np.int32)

    path(points, color, thickness)

def convolute(kernel):
    global IMAGE
    
    kernel = np.flip(np.array(kernel))
    # create empty output image of the same shape as the input
    output_image = np.zeros_like(IMAGE)

    # perform convolution for each color channel
    for channel in range(IMAGE.shape[2]):
        output_image[:, :, channel] = sp.signal.convolve2d(IMAGE[:, :, channel], kernel, mode='same', boundary='wrap')

    # restrict values to the valid range (0-255 for uint8 images)
    output_image = np.clip(output_image, 0, 255).astype(np.uint8)

    IMAGE = output_image

# cli processing

if len(sys.argv) != 2:
    print("Usage: py imaged.py <edit file>")
    sys.exit(1)
else:
    edit_filepath = sys.argv[1]

#edit_filepath = r'D:\Projects\Programming\Python Scripts\.image effects\imgfx\tied\outline.ed'

# session variables
lines = ""
terminal = [0]
timeElapsed = 0
programStartTime = time.time()
frame = 0
update_frame = 0
IMAGE = np.array([])
live = False
full_width = 10000000
for m in get_monitors():
    full_width = min(full_width, m.width)
window_size = 1000
running = True
lineNo = 0
hold = False

# another thread for interaction/preview
iThread = threading.Thread(target=pyg_thread, name="Interaction")

# seperate thread for terminal output
cThread = threading.Thread(target=curses_thread, name="Curses")

iThread.start()
cThread.start()

iterationStartTime = time.time()
update = False
lasthash = ''
while running:
    variables = {}
    terminal = [0]

    current_hash = get_file_hash(edit_filepath)
    # scan lines
    if current_hash != lasthash or (live and not hold): #only process file if it has changed or live update is on
        lasthash = current_hash
        with open(edit_filepath, 'r') as file:
            # set some live variables
            iterationStartTime = time.time()
            timeElapsed = time.time() - programStartTime

            # convert file into list and iterate over it
            lines = file.readlines()
            length = len(lines)
            l = 0
            while l < length:
                # get the current line and process it properly
                curLine = lines[l]
                curLine = handle_replacements(curLine)
                curLine = curLine.rstrip()
                
                # make sure this isn't the last line 
                if l + 1 < length:
                    # is the next line indented?
                    if lines[l + 1][0].isspace() and not lines[l + 1].isspace():
                        curLine += '\n'
                        l += 1
                        # keep adding lines until end of for loop or end of file
                        while lines[l][0].isspace():
                            # add this line to the line to process with replacements
                            curLine += handle_replacements(lines[l])

                            l += 1
                            if l == length:
                                break
                
                # try to execute line but print error if failure
                try:
                    exec(curLine.strip())
                except Exception as e:
                    ERROR(e, l)
                l += 1
                lineNo = l # set global line number variable

            terminal[0] = 1 # terminal is ready to be printed
            update = True   # image is ready to be drawn
    if not live: sleep(.002) # don't keep checking for performance optimization