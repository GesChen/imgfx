import cv2
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import os 
import pygame
import numpy as np
import math

def create_polygon_mask(image_dims, polygon):
    height, width = image_dims[:2]
    mask = np.zeros((height, width), dtype=np.uint8)  # Create empty mask

    # Convert polygon to a format suitable for cv2.fillPoly
    pts = np.array([polygon], dtype=np.int32)

    # Fill the polygon with white pixels (value 255) in the mask
    cv2.fillPoly(mask, pts, 255)

    return mask

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
blurradius = int(input("blur radius (must be odd): "))
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
            truepos = ((pos[0] - offset[0])/scale, (pos[1] - offset[1])/scale)
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

blurred = cv2.GaussianBlur(im, (blurradius, blurradius), 0)
mask = create_polygon_mask(im.shape, polygon)

new = im * (1 - mask) + blurred * mask

cv2.imwrite(os.path.join(imgpath,nameout), cv2.cvtColor(new,cv2.COLOR_RGB2BGR))
