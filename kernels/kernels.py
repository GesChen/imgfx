import cv2
import numpy as np
import os
import threading
from matplotlib import pyplot as plt
import time
import math
import warnings
#warnings.filterwarnings("ignore")

imagepath = input("Path: ")
imagename = input("Image name: ")
imageout  = input("Output name: ")

image = cv2.cvtColor(
	cv2.imread(os.path.join(imagepath, imagename)),
	cv2.COLOR_BGR2RGB)
total_lines = 0

kernel = [
	[1,0,-1],
	[2,1,-2],
	[1,0,-1]
]
total = float(np.sum(kernel))
dim = len(kernel)
offset = math.floor(dim/2)

def process_image(start, end):
	global image
	global total_lines
	
	for column in range(start, end):
		for row in range(image.shape[1]):
			pixel = image[column][row]
			sum = np.zeros(3)
			for x in range(dim):
				for y in range(dim):
					tocheck = (x - offset + row, y - offset + column)
					if tocheck[0] >= 0 and tocheck[0] < image.shape[1] \
						and tocheck[1] >= 0 and tocheck[1] < image.shape[0]:
						sum += image[tocheck[1]][tocheck[0]] * kernel[y][x]
			image[column][row] = np.divide(sum, total)

		total_lines += 1

def progessBar():
	global image
	global total_lines

	startTime = time.time()
	barlength = 30
	
	while total_lines < image.shape[0]:
		progress = total_lines / image.shape[0]
		chars = round(progress * barlength)
		progressText = "Progress: [" + "="*chars + "-"*(barlength - chars) + "] {:.2f}%".format(progress * 100)
		
		print(progressText ,end='\r')
	print("\nFinished! Processing took {:.2f} seconds.".format(time.time() - startTime))

threads = []
threads.append(threading.Thread(target = progessBar))
for t in range(round(image.shape[0]/10)):
	threads.append(threading.Thread(target = process_image, args = (t * 10, (t + 1) * 10)))

for t in threads:
	t.start()

for t in threads:
	t.join()

plt.imshow(image)
plt.show()

cv2.imwrite(os.path.join(imagepath,imageout),cv2.cvtColor(image,cv2.COLOR_RGB2BGR))