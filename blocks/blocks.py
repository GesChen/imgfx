import cv2
import numpy as np
import random
from matplotlib import pyplot as plt
import datetime
import os
import threading
import time

# get the average color over a region of an image
def region_average(image, pos0, pos1):
    region = image[
        min(pos0[0], pos1[0]):max(pos0[0], pos1[0]), 
        min(pos0[1], pos1[1]):max(pos0[1], pos1[1])]
    return np.mean(region, axis=(0,1))

# use image structure to generate image using rectangles 
def generate_image(image, original):
    blank = np.zeros([image[0]['size'][1], image[0]['size'][0], 3], dtype=np.uint8)
    if len(image) == 1:
        return blank
    
    for block in image[1:]:
        cv2.rectangle(blank, block['pos0'], block['pos1'], region_average(original, block['pos0'], block['pos1']), -1)
    return blank

# absolute element wise difference of colors
def difference(col1, col2):
    return np.sum(np.abs(col1 - col2)) 

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
    choice = random.randrange(0, 6) # pick a random choice
    if choice < 3: choice = 0
    else: choice -= 3

    if len(image) == 1: # force add a rect if empty image
        choice = 0
    match choice:
        case 0: # add a random rect
            image.append({
                'pos0'  : (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1]))),
                'pos1'  : (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1]))),
            })
        case 1: # remove a random rect
            del image[random.randrange(1, len(image))]
        
        case 2: # move a random rect
            image[random.randrange(1, len(image))]['pos0'] = (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1])))
            image[random.randrange(1, len(image))]['pos1'] = (int(random.randrange(0, image[0]['size'][0])), int(random.randrange(0, image[0]['size'][1])))
    return image 

# performs random number of random changes to an 
# image and sets the resulting performance and image in results
def mutate(image, maxchanges):
    for c in range(maxchanges):
        image = random_change(image)
    perf = performance(original, image)
    return perf, image

# performs batch number of mutations as a group
def group(image, maxchanges, batch_size, output, group_index):
    global total_mutations

    best_performance = np.inf
    best_image = None

    for i in range(batch_size):
        #print(f"processing item {i} in group {group_index}", flush=True)
        perf, thisImage = mutate(image[::], maxchanges)
        if perf < best_performance:
            best_performance = perf
            best_image = thisImage
        total_mutations += 1
    
    output[group_index] = [best_performance, best_image]

def progressBar(max_mutations, _):
	global total_mutations

	startTime = time.time()
	barlength = 30
	
	while total_mutations < max_mutations:
		progress = total_mutations / max_mutations
		chars = round(progress * barlength)
		progressText = "Progress: [" + "="*chars + "-"*(barlength - chars) + "] {:.2f}%".format(progress * 100)
		
		print(progressText ,end='\r')
	print("\nFinished! Processing took {:.2f} seconds.".format(time.time() - startTime))

# init
path = r"D:\Projects\Programming\Python Scripts\.image effects\imgfx\blocks\output"
file = r"D:\Projects\Programming\Python Scripts\.image effects\imgfx\blocks\candle_downscale.png"
original = cv2.cvtColor(
    cv2.imread(file),
    cv2.COLOR_BGR2RGB)

iterations = 10
groups = 30
batch_size = 20
changes = 50
closest_image = [{'size' : original.shape[:2][::-1]}] # create a blank image 
total_mutations = 0

perf_history = []
final = None
last_lowest = np.Infinity

i = 0
# main loop
while datetime.datetime.now().hour != 6:
    print(f"Starting iter {i}")
    threads = []
    results = [[]] * groups
    for t in range(groups):
        #print(f"processing group {t}")
        thread = threading.Thread(target=group, args=(closest_image, changes, batch_size, results, t))
        threads.append(thread)
        thread.name = "Group " + str(t)
        thread.start()
    max_mutations = groups * batch_size
    progressBarThread = threading.Thread(target=progressBar, args=(max_mutations, 0), name="Progress Bar")
    threads.append(progressBarThread)
    progressBarThread.start() 
    
    for t in threads:
        t.join()
    
    lowest_performance = last_lowest
    for g, result in enumerate(results):
        perf, image = result
        #print(f"group index {g} had a best performance of {perf}")
        if perf < lowest_performance:
            lowest_performance = perf
            closest_image = image
    
    if lowest_performance == last_lowest:
        print(f"iteration {i} had no improvements, best perf {lowest_performance}")
    else:
        print(f"iteration {i} best perf {lowest_performance}")
    
    last_lowest = lowest_performance
    perf_history.append(lowest_performance)
    final = closest_image
    total_mutations = 0
    i+=1

final_image = generate_image(final, original)

# find the highest outputted file name and add 1 
output_files = [filename for filename in os.listdir(path) if filename.startswith('output')]
highest_number = max([int(filename[6:-4]) for filename in output_files])

filename = f"output{highest_number + 1}.png"
cv2.imwrite(os.path.join(path, filename), cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR))

x_axis = range(len(perf_history))
plt.plot(x_axis, perf_history)
plt.title('best performance by iteration')
plt.xlabel('iteration')
plt.ylabel('best performance')
plt.show()