import cv2
import numpy as np
import pygame
from matplotlib import pyplot as plt

def blur(image, region, radius):
    blurred_image = cv2.GaussianBlur(image, (radius, radius), 0)
    
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [polygon_pts], 1)
    mask = cv2.GaussianBlur(mask, (blur_radius, blur_radius), 0)
    
    return cv2.addWeighted(image, 1-mask, blurred_image, mask, 0)
    
imagepath = input("Image Path: ")
image = cv2.imread(imagepath)
radius = 20

polygons = []
adding = True
while adding:
    
    
for polygon in polygons:
    image = blur(image, polygon, radius)

plt.imshow(cv2.cvtColor(image, cv2.BGR2RGB))
plt.show()

cv2.imwrite(image)