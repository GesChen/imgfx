import cv2
import numpy as np
import os
import curses
import threading
import hashlib
from time import sleep
from datetime import datetime
from screeninfo import get_monitors
import pygame

## supporting functions
def is_path(string):
    return os.path.isabs(string) or os.path.exists(string)

def get_file_hash(file_path):
    with open(file_path, 'rb') as file:
        return hashlib.md5(file.read()).hexdigest()

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
    stdscr.clear()

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) #type:ignore
    ERROR_COLOR = curses.color_pair(1)                        #type:ignore

    while True:
        if terminal[0] == 1:
            stdscr.erase()

            for l, line in enumerate(terminal[1:]):
                line = str(line)
                try:
                    if line[:5] == "Error":
                        stdscr.addstr(l, 0, repr(line).strip("'"), ERROR_COLOR)
                    else:
                        stdscr.addstr(l, 0, repr(line).strip("'"))
                except:
                    pass

            stdscr.refresh()
            terminal[0] = 0

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

def pygame_thread():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.mouse.set_cursor(*pygame.cursors.tri_left)
    lastScreen = None
    while True:
        clock.tick(60)
        events = pygame.event.get()

        check_for_resize(lastScreen)
        screen = update_screen(lastScreen)

        lastScreen = screen

def update_screen(lastScreen):
    global update
    if IMAGE.shape[0] != 0 and update == True:
        dimensions = IMAGE.shape[:2][::-1]
        factor = dimensions[0] / window_size
        resized = cv2.resize(IMAGE, (int(dimensions[0] / factor), int(dimensions[1] / factor)))

        screen = pygame.display.set_mode(resized.shape[1::-1], pygame.RESIZABLE | pygame.HWSURFACE)
        pyimage = pygame.image.frombuffer(resized.tobytes(), resized.shape[1::-1], "RGB")
        screen.blit(pyimage, (0,0))

        pygame.display.flip()
        update = False

        return screen
    return lastScreen

last_width = 0
def check_for_resize(screen):
    if screen is None:
        return

    global last_width
    global window_size
    global update

    width, _ = screen.get_size()
    print_(width)
    if width != last_width:
        print_("updating size")
        window_size = width
        update = True
        print_("updating")
    last_width = width

## editing debug
def edit(path):
    global IMAGE
    IMAGE = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)

def dim():
    print_(IMAGE.shape[:2][::-1])

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
        cv2.polylines(IMAGE, points, closed, color[:3], thickness)
        return
    copy = IMAGE.copy()
    alpha = color[3]
    cv2.polylines(IMAGE, [points], closed, color[:3], thickness)
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




edit_filepath = r'D:\Projects\Programming\Python Scripts\.image effects\imgfx\editor\test.ed'

terminal = [0]

# seperate thread for terminal output
cThread = threading.Thread(target=curses_thread, name="Curses")
cThread.start()

# another thread for interaction/preview
iThread = threading.Thread(target=pygame_thread, name="Interaction")
iThread.start()

# session variables
time = 0
IMAGE = np.array([])
live = False
full_width = 10000000
for m in get_monitors():
    full_width = min(full_width, m.width)
window_size = 1000

update = False
starttime = datetime.now()
lasthash = ''
while True:
    variables = {}
    terminal = [0]

    current_hash = get_file_hash(edit_filepath)
    # scan lines
    if current_hash != lasthash or live: #only process file if it has changed or live update is on
        lasthash = current_hash
        with open(edit_filepath, 'r') as file:
            for l, curLine in enumerate(file):
                time = datetime.now() - starttime

                curLine = curLine.replace('print', 'print_')
                try:
                    exec(curLine.strip())
                except Exception as e:
                    ERROR(e, l)

            terminal[0] = 1 # terminal is ready to be printed
            update = True   # image is ready to be drawn
    if not live: sleep(.002)