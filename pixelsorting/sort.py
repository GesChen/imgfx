import cv2
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import os 
import pygame

def mergeSort(arr):
    if len(arr) > 1:

        r = len(arr)//2
        leftArr = arr[:r]
        rightArr = arr[r:]

        mergeSort(leftArr)
        mergeSort(rightArr)

        i = j = k = 0

       
        while i < len(leftArr) and j < len(rightArr):
            if leftArr[i][0] < rightArr[j][0]:
                arr[k] = leftArr[i]
                i += 1
            else:
                arr[k] = rightArr[j]
                j += 1
            k += 1

       
        while i < len(leftArr):
            arr[k] = leftArr[i]
            i += 1
            k += 1

        while j < len(rightArr):
            arr[k] = rightArr[j]
            j += 1
            k += 1

def draw_polygon_alpha(surface, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    surface.blit(shape_surf, target_rect)

imgpath = input("path: ")
imgname = input("name: ")
nameout = input("name out: ")
im = cv2.imread(os.path.join(imgpath,imgname))

im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)

#interactive polygon select with pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(im.shape[1::-1], pygame.RESIZABLE)
pyimage = pygame.image.frombuffer(im.tobytes(), im.shape[1::-1], "RGB")
screen.blit(pyimage, (0,0))
pygame.display.flip()

polygon = []

status = True
xlaststatus = False
while status:
    events = pygame.event.get()
    clock.tick(60)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        status = False
    if keys[pygame.K_x] != xlaststatus and keys[pygame.K_x] and len(polygon) > 0:
        polygon.pop(len(polygon)-1)
    xlaststatus = keys[pygame.K_x]
    
    size = pygame.display.get_window_size()
    scale = (size[0] / im.shape[1]) if size[0] / im.shape[1] < size[1] / im.shape[0] else (size[1] / im.shape[0])
    offset = ((size[0] - im.shape[1] * scale)/2, (size[1] - im.shape[0] * scale)/2)
    screen.blit(pygame.transform.scale(pyimage, (im.shape[1] * scale, im.shape[0] * scale)), offset)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            print(pos)
            truepos = ((pos[0] - offset[0])/scale, (pos[1] - offset[1])/scale)
            print(truepos)
            if truepos[0] >= 0 and truepos[1] >= 0:
                polygon.append(truepos)
    
    def im2sc(point):
        return (point[0]*scale+offset[0],point[1]*scale+offset[1])

    for point in polygon:
        pygame.draw.circle(screen,(255,0,0),im2sc(point),2)
    
    if len(polygon) > 1:
        for p in range(len(polygon)-1):
            pygame.draw.line(screen,(255,0,0),im2sc(polygon[p]),im2sc(polygon[p+1]),1)
    if len(polygon) > 2:
        draw_polygon_alpha(screen,(255,0,0,50),[im2sc(p) for p in polygon])
        
    pygame.display.flip()
pygame.quit()

total = []
for y in range(im.shape[0]):
    print("row %i"%y)
    rowpoints = []
    for x in range(im.shape[1]):
        if Polygon(polygon).contains(Point(x,y)):
            rowpoints.append((x,y))
    total.append(rowpoints)

#merge sort sorts grayscale values, entires are in a list, first item gray val second actual color
grayim = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
for row in total:
    if len(row) != 0:
        mergedlist = []
        for pos in row:
            mergedlist.append([grayim[pos[1]][pos[0]],im[pos[1]][pos[0]].tolist()])
        mergeSort(mergedlist)
        mergedlist.reverse()
        for i in range(len(row)):
            im[row[i][1]][row[i][0]] = mergedlist[i][1]

cv2.imwrite(os.path.join(imgpath,nameout),cv2.cvtColor(im,cv2.COLOR_RGB2BGR))
