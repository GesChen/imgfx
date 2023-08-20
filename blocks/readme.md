# Blocks Filter
Uses "Machine Learning" (not sure what this even is) to recreate an image using rectangles of different sizes 
Supposed to get better over time by "training"
In the end you *should* get a relatively good image that represents the original to *some* degree of accuracy, so far though still needs lots of work.

### Algo layout/psuedo:
performance function factors
    +closeness in pixels to actual image
    -number of blocks

image structure:
    list of block dicts
    {bottom left, top right, color}

iteration:
    2d results list 
    groups are made on separate threads
    per group: 
        multiple "agents" are made, each make some number of changes (batch)
        grade performance
        return best performing
    compare best performing to get bestest performing 
    base next generation off bestest performing