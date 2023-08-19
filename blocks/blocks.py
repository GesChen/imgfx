import cv2
import numpy as np
import random
from matplotlib import pyplot as plt
import datetime
import os

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

# get the average color over a region of an image
def region_average(image, pos0, pos1):
	return np.mean(image[
		min(pos0[0], pos1[0]):max(pos0[0],pos1[0]), 
		min(pos0[1], pos1[1]):max(pos0[1],pos1[1])])

# use image structure to generate image using rectangles 
def generate_image(image, original):
	blank = np.zeros([image[0]['size'][0],image[0]['size'][1],3], dtype=np.uint8)
	if len(image) == 1:
		return blank
	
	for block in image[1:]:
		cv2.rectangle(blank, block['pos0'], block['pos1'], region_average(original, block['pos0'], block['pos1']), -1)
	return blank

# absolute element wise difference of colors
def difference(col1, col2):
	return np.sum(np.abs(col1-col2)) 

# calculate total pixel difference multiplied by number of blocks 
def performance(original, image): 
	actual = generate_image(image, original)
	total = 0
	for row in range(actual.shape[0]):
		for column in range(actual.shape[1]):
			total += difference(actual[row][column], original[row][column])
	return total# * (len(image) - 1)

# perform a random change to the image
def random_change(image):
	choice = random.randrange(0, 3) # pick a random choice
	if len(image) == 1: # force add a rect if empty image
		choice = 0
	match choice:
		case 0: # add a random rect
			image.append({
				'pos0'  : (int(random.randrange(0, image[0]['size'][1])), int(random.randrange(0, image[0]['size'][0]))),
				'pos1'  : (int(random.randrange(0, image[0]['size'][1])), int(random.randrange(0, image[0]['size'][0]))),
			})
		case 1: # remove a random rect
			del image[random.randrange(1, len(image))]
		
		case 2: # move a random rect
			image[random.randrange(1, len(image))]['pos0'] = (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1])))
			image[random.randrange(1, len(image))]['pos1']   = (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1])))
	return image 

def mutate(image, maxchanges):
	for c in range(random.randint(1, maxchanges)):
		image = random_change(image)
	perf = performance(original, image)
	return perf, image

# init
path = r"D:\Projects\Programming\Python Scripts\.image effects\imgfx\blocks\output"
file = r"D:\Projects\Programming\Python Scripts\.image effects\imgfx\blocks\candle_downscale.png"
original = cv2.cvtColor(
	cv2.imread(file),
	cv2.COLOR_BGR2RGB)

iterations = 10
batch_size = 5
changes = 30
batch = [[{'size' : original.shape[:2]}]] * batch_size # create a bunch of image 

perf_history = []
result = None
last_lowest = np.Infinity
# main loop
for i in range(iterations):
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

final = generate_image(result, original)

# find the highest outputted file name and add 1 
output_files = [filename for filename in os.listdir(path) if filename.startswith('output')]
highest_number = max([int(filename[6:-4]) for filename in output_files])

filename = f"output{highest_number + 1}.png"
cv2.imwrite(os.path.join(path, filename), cv2.cvtColor(final, cv2.COLOR_RGB2BGR))

plt.imshow(final)
plt.show()
