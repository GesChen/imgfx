import cv2
import numpy as np
import os
import threading
import time
import warnings
#warnings.filterwarnings("ignore")

imagepath = input("Path: ")
imagename = input("Image name: ")
imageout  = input("Output name: ")

image = cv2.cvtColor(
	cv2.imread(os.path.join(imagepath, imagename)),
	cv2.COLOR_BGR2RGB)
total_lines = 0

def process_image(start, end):
	global image
	global total_lines

	for column in range(start, end):
		for row in range(image.shape[1]):
			pixel = image[column][row]
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

#plt.imshow(image)
#plt.show()

cv2.imwrite(os.path.join(imagepath,imageout),cv2.cvtColor(image,cv2.COLOR_RGB2BGR))