import cv2
import numpy as np
import random
from matplotlib import pyplot as plt

'''
performance function factors
	+closeness in pixels to actual image
	-number of blocks
iteration:
	multiple "agents" are made, each make some number of changes
	grade performance
	base next generation off best performing

image structure:
	list of block dicts
	{bottom left, top right, color}
'''

# use image structure to generate image using rectangles 
def generate_image(image):
	blank = np.zeros([image[0]['size'][0],image[0]['size'][1],3], dtype=np.uint8)
	for block in image[1:]:
		cv2.rectangle(blank, block['bottomleft'], block['topright'], block['color'])
	return blank

# absolute element wise difference of colors
def difference(col1, col2):
	return np.sum(np.abs(col1-col2)) 

# calculate total pixel difference multiplied by number of blocks 
def performance(original, image): 
	actual = generate_image(image)
	total = 0
	for row in range(actual.shape[1]):
		for column in range(actual.shape[0]):
			total += difference(actual[column][row], original[column][row])
	return total * (len(image) - 1)

# perform a random change to the image
def random_change(image):
	choice = random.randrange(0, 4)
	match choice:
		case 0: # add a random rect
			image.append({
				'bottomleft' : (random.randrange(0, image[0]['size'][0]), random.randrange(0, image[0]['size'][1])),
				'topright'   : (random.randrange(0, image[0]['size'][0]), random.randrange(0, image[0]['size'][1])),
				'color'      : (np.random.randint(0, 255, 3))})
		
		case 1: # remove a random rect
			del image[random.randrange(1, len(image))]
		
		case 2: # move a random rect
			image[random.randrange(1, len(image))]['bottomleft'] = (random.randrange(0, image[0]['size'][0]), random.randrange(0, image[0]['size'][1]))
			image[random.randrange(1, len(image))]['topright']   = (random.randrange(0, image[0]['size'][0]), random.randrange(0, image[0]['size'][1]))

		case 3: # recolor a random rect
			image[random.randrange(1, len(image))]['color'] = (np.random.randint(0, 255, 3))
	return image 

# init
file = r"D:\Projects\Programming\Python Scripts\.image effects\imgfx\blocks\candle_downscale.png"
original = cv2.cvtColor(
	cv2.imread(file),
	cv2.COLOR_BGR2RGB)

iterations = 1000
batch_size = 100
changes = 2
batch = [{'size' : original.shape[:2][::-1]}] * batch_size # create a bunch of image 
result = None
# main loop
for i in range(iterations):
	for image in batch:
		image = random_change(image)
	
	closest_image = None
	lowest_performance = np.Infinity
	for image in batch:
		perf = performance(original, image)
		if perf < lowest_performance:
			lowest_performance = perf
			closest_image = image
	
	batch = [closest_image] * batch_size

	if i == iterations - 1:
		result = closest_image

final = generate_image(result)
plt.imshow(final)
plt.show()