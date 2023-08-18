import cv2
import numpy as np
import os
import threading
import time
import warnings
warnings.filterwarnings("ignore")

def totalAbsColorDiff(a, b):
	return abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])

imagepath = input("Path: ")
imagename = input("Image name: ")

threshold = 0
total_lines = 0

def process_image(start, end):
	global image
	global total_lines

	for column in range(start, end):
		curcol = image[column][0]
		totalCol = np.zeros(3)
		width = 0
		for row in range(image.shape[1]):
			pixel = image[column][row]
			width += 1
			totalCol = np.add(totalCol, pixel)
			if totalAbsColorDiff(pixel, curcol) >= threshold or row == image.shape[1] - 1 and row != 0:
				averageCol = np.divide(totalCol, width)
				for i in range(width):
					image[column][row - width + i] = averageCol
				
				width = 0
				totalCol = np.zeros(3)
				curcol = pixel
		total_lines += 1
		#print(total_lines)

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

for i in range(240):
	image = cv2.cvtColor(
	cv2.imread(os.path.join(imagepath, imagename)),
	cv2.COLOR_BGR2RGB)

	threads = []
	threads.append(threading.Thread(target = progessBar))
	for t in range(round(image.shape[0]/10)):
		threads.append(threading.Thread(target = process_image, args = (t * 10, (t + 1) * 10)))

	for t in threads:
		t.start()

	for t in threads:
		t.join()

	cv2.imwrite(os.path.join(imagepath,str(i).zfill(4)+".jpg"),cv2.cvtColor(image,cv2.COLOR_RGB2BGR))

	threshold += 1
	total_lines = 0

#plt.imshow(image)
#plt.show()

