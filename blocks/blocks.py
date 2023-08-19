import cv2
import numpy as np
import random
from matplotlib import pyplot as plt
import datetime

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
	if len(image) == 1:
		return blank
	
	for block in image[1:]:
		cv2.rectangle(blank, block['bottomleft'], block['topright'], (int(block['color'][0]), int(block['color'][1]),int(block['color'][2])), -1)
	return blank

# absolute element wise difference of colors
def difference(col1, col2):
	return np.sum(np.abs(col1-col2)) 

# calculate total pixel difference multiplied by number of blocks 
def performance(original, image): 
	actual = generate_image(image)
	total = 0
	for row in range(actual.shape[0]):
		for column in range(actual.shape[1]):
			total += difference(actual[row][column], original[row][column])
	return total# * (len(image) - 1)

# perform a random change to the image
def random_change(image):
	choice = random.randrange(0, 4) # pick a random choice
	if len(image) == 1: # force add a rect if empty image
		choice = 0
	match choice:
		case 0: # add a random rect
			image.append({
				'bottomleft' : (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1]))),
				'topright'   : (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1]))),
				'color'      : (np.random.randint(0, 255, 3))})
		
		case 1: # remove a random rect
			del image[random.randrange(1, len(image))]
		
		case 2: # move a random rect
			image[random.randrange(1, len(image))]['bottomleft'] = (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1])))
			image[random.randrange(1, len(image))]['topright']   = (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1])))

		case 3: # recolor a random rect
			image[random.randrange(1, len(image))]['color'] = (np.random.randint(0, 255, 3))
	return image 

def mutate(image, maxchanges):
	for c in range(random.randint(1, maxchanges)):
		image = random_change(image)
	perf = performance(original, image)
	return perf, image

# init
file = r"D:\Projects\Programming\Python Scripts\.image effects\imgfx\blocks\candle_downscale.png"
original = cv2.cvtColor(
	cv2.imread(file),
	cv2.COLOR_BGR2RGB)

iterations = 1000
batch_size = 50
changes = 5
batch = [[{'size' : original.shape[:2]}]] * batch_size # create a bunch of image 

perf_history = []
result = None
last_lowest = np.Infinity
i = 0
# main loop
while datetime.datetime.now().hour != 6:
	closest_image = batch[0]
	lowest_performance = last_lowest
	for image in batch[1:]:
		perf, image = mutate(image, changes)
		
		if perf < lowest_performance:
			lowest_performance = perf
			closest_image = image		
	
	batch = [closest_image] * batch_size	

	if lowest_performance == last_lowest:
		print(f"iteration {i} had no improvements, best perf {lowest_performance}")
	else:
		print(f"iteration {i} best perf {lowest_performance}")
	
	last_lowest = lowest_performance
	perf_history.append(lowest_performance)
	result = closest_image
	i+=1

final = generate_image(result)
cv2.imwrite(r"D:\Projects\Programming\Python Scripts\.image effects\imgfx\blocks\output.png", final)
plt.imshow(final)
plt.show()
