import imageio.v2 as imageio
import os

path = input("Path: ")
fileout = input("Output file: ")
fps = input("FPS: ")

writer = imageio.get_writer(os.path.join(os.path.dirname(path),fileout), fps = float(fps))
for file in os.listdir(path):
    fullpath = os.path.join(path, file)
    if os.path.isfile(fullpath):
        im = imageio.imread(fullpath)
        writer.append_data(im)
writer.close()

print("Complete")
