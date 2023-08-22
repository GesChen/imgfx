import cv2
import numpy as np
import time
#import pyaudio

def rgb2bgr(col):
	return col[::-1]

def clamp(x, low, high):
	return max(low, min(high, x))

def hsv2rgb(h, s, v, a):
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

def mapRange(value, from_min, from_max, to_min, to_max):
	slope = (to_max - to_min) / (from_max - from_min)
	return to_max + slope * (value - from_min)

class Item:
	def __init__(self, pos, thick, color):
		self.pos = pos
		self.thick = thick
		self.color = color
		self.enabled = True

	def draw(self, image):
		return

class Text(Item):
	def __init__(self, pos, size, thick, color, font, content):
		super().__init__(pos, thick, color)
		self.size = size
		self.font = font
		self.content = content
	
	def draw(self, image):
		copy = image.copy()
		alpha = self.color[3]
		
		cv2.putText(copy, self.content, self.pos, self.font, self.size, rgb2bgr(self.color[:3]), self.thick)

		cv2.addWeighted(copy, alpha, image, 1 - alpha, 0, image)

class Line(Item):
	def __init__(self, pos1, pos2, thick, color):
		super().__init__(pos1, thick, color)
		self.pos2 = pos2
	
	def draw(self, image):
		copy = image.copy()
		alpha = self.color[3]

		cv2.line(copy, self.pos, self.pos2, rgb2bgr(self.color[:3]), self.thick)

		cv2.addWeighted(copy, alpha, image, 1 - alpha, 0, image)

class Circle(Item):
	def __init__(self, pos, radius, thick, color):
		super().__init__(pos, thick, color)
		self.radius = radius
	
	def draw(self, image):
		copy = image.copy()
		alpha = self.color[3]

		cv2.circle(copy, self.pos, self.radius, rgb2bgr(self.color[:3]), self.thick)

		cv2.addWeighted(copy, alpha, image, 1 - alpha, 0, image)

class Rect(Item):
	def __init__(self, pos, size, thick, color):
		super().__init__(pos, thick, color)
		self.size = size
	
	def draw(self, image):
		copy = image.copy()
		alpha = self.color[3]

		cv2.rectangle(copy, self.pos, np.add(self.pos, self.size), rgb2bgr(self.color[:3]), self.thick)

		cv2.addWeighted(copy, alpha, image, 1 - alpha, 0, image)

class AngledBox():
	def __init__(self, pos1, pos2, angles, thick, color):
		self.pos1 = pos1
		self.pos2 = pos2
		self.angles = angles
		self.thick = thick
		self.color = color
		self.enabled = True

	def draw(self, image):
		p1 = self.pos1
		p2 = self.pos2
		an = self.angles
		alpha = self.color[3]
		copy = image.copy()

		u1 = (p1[0] + an[0], p1[1])
		u2 = (p2[0] - an[1], p1[1])
		r1 = (p2[0], p1[1] + an[1])
		r2 = (p2[0], p2[1] - an[2])
		b1 = (p2[0] - an[2], p2[1])
		b2 = (p1[0] + an[3], p2[1])
		l1 = (p1[0], p2[1] - an[3])
		l2 = (p1[0], p1[1] + an[0])

		# main lines

		cv2.line(copy, u1, u2, rgb2bgr(self.color[:3]), self.thick)
		cv2.line(copy, r1, r2, rgb2bgr(self.color[:3]), self.thick)
		cv2.line(copy, b1, b2, rgb2bgr(self.color[:3]), self.thick)
		cv2.line(copy, l1, l2, rgb2bgr(self.color[:3]), self.thick)

		# corners

		cv2.line(copy, u1, l2, rgb2bgr(self.color[:3]), self.thick)
		cv2.line(copy, u2, r1, rgb2bgr(self.color[:3]), self.thick)
		cv2.line(copy, b1, r2, rgb2bgr(self.color[:3]), self.thick)
		cv2.line(copy, b2, l1, rgb2bgr(self.color[:3]), self.thick)

		cv2.addWeighted(copy, alpha, image, 1 - alpha, 0, image)	

vid = cv2.VideoCapture(0)
_, frame = vid.read()
size = frame.shape[:2][::-1] # cuts it off and reverses it

# audio visualizer
avPos = (20, size[1] - 50)
avBars = 10
avSpacing = 3
avScale = 10
avThickness = 2
avData = []

red =  (250, 30, 30, 1)
blue = (30, 30, 250, 1)
overlay = {
	#Text((0, 50), 1.5, 2, (100, 100, 255, .5), cv2.FONT_HERSHEY_SIMPLEX, 'test'),
	#AngledBox((10,10), (150, 50), [10,0,10,0], 2, (0,0,255, 1))
	"border":[AngledBox((3,3), (size[0] - 3, size[1] - 3), [7, 0, 7, 0], 1, blue)],
	"recordingIndicator":[Circle((size[0] - 20, 20), 8, 1, red)],
	"time":[Text((6, 35), 1, 1, blue, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 'time')],
	"weather":[
		Text((10,65), .7, 1, blue, cv2.FONT_HERSHEY_SIMPLEX, '69C'),
	    Text((10,85), .7, 1, blue, cv2.FONT_HERSHEY_SIMPLEX, 'sunny')],
	"audioVisualizer":[],
	"battery":[
		Rect((size[0] - 20, 5), (15, 10), 1, blue)
	]
}

# i have no idea what half these do gl
glowSize = 15
glowFalloff = 3
glowAlphaCoef = .005
glowIters = 2
glowIntensity = 51
doGlow = 1

while True:

	ret, frame = vid.read()
	
	overlay["time"][0].content = time.strftime("%H:%M:%S", time.localtime())
	overlay["recordingIndicator"][0].enabled = False #time.localtime().tm_sec % 2 == 0
	for piece in overlay.keys():
		for item in overlay[piece]:
			if item.enabled:
				if doGlow:
					initCol = item.color
					initThick = item.thick
					
					for i in range(glowIters):
						v = 1 + (2 / (glowIters - 1)) * i
						item.color = initCol[:3] + tuple([glowAlphaCoef * v ** 2])
						item.thick = clamp(round(-glowFalloff * v + glowSize), 1, 100)
						item.draw(frame)

					item.color = tuple([clamp(initCol[i] + glowIntensity, 0, 255) if i < 3 else initCol[3] for i in range(4)])
					item.thick = initThick
					item.draw(frame)

					item.color = initCol
					item.thick = initThick
				else:
					item.draw(frame)
	
	cv2.imshow("frame", frame)

	if cv2.waitKey(1) == ord('q'):
		break

vid.release()

cv2.destroyAllWindows()