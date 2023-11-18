import cv2
import numpy as np
import os

imagepath = input("Path: ")
imagename = input("Image name: ")
imageout  = input("Output name: ")

image = cv2.cvtColor(
	cv2.imread(os.path.join(imagepath, imagename)),
	cv2.COLOR_BGR2RGB)

def process_image():
	global image

	for column in range(image.shape[0]):
		for row in range(image.shape[1]):
			pixel = image[column][row]

			if abs(sum(np.subtract(pixel, (242,242,242)))) < 7:
				image[column][row] = (247, 248, 248)

process_image()

#plt.imshow(image)
#plt.show()

cv2.imwrite(os.path.join(imagepath,imageout),cv2.cvtColor(image,cv2.COLOR_RGB2BGR))