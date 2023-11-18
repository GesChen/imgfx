import cv2
import dlib 
import numpy as np
from os import path

def sort_and_blend_pixels(image, bbox, blend_ratio=0.3):
    # Extract the bounding box coordinates
    x, y, w, h = bbox

    # Crop the region of interest (ROI) based on bounding box coordinates
    roi = image[y:y+h, x:x+w]

    # Convert the ROI to the HSV color space
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Sort pixels horizontally by saturation
    sorted_roi = np.array(sorted(hsv_roi.reshape(-1, 3), key=lambda x: (x[1], x[0]))).reshape(hsv_roi.shape)

    # Sort pixels vertically by value
    sorted_roi = np.array(sorted(sorted_roi.reshape(-1, 3), key=lambda x: x[2])).reshape(sorted_roi.shape)

    # Blur the original ROI
    blurred_roi = cv2.GaussianBlur(roi, (15, 15), 0)

    # Blend the original blurred ROI with the sorted ROI
    blended_roi = cv2.addWeighted(blurred_roi, blend_ratio, cv2.cvtColor(sorted_roi, cv2.COLOR_HSV2BGR), 1 - blend_ratio, 0)

    # Replace the original ROI with the blended one
    image[y:y+h, x:x+w] = blended_roi

    return image
def sort_pixels(image, bbox):
    # Extract the bounding box coordinates
    x, y, w, h = bbox
    x = abs(x)
    y = abs(y)
    w = abs(w)
    h = abs(h)

    # Crop the region of interest (ROI) based on bounding box coordinates
    roi = image[y:y+h, x:x+w]

    # Convert the ROI to the HSV color space
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Sort pixels horizontally by saturation
    sorted_roi = np.array(sorted(hsv_roi.reshape(-1, 3), key=lambda x: (x[1], x[0]))).reshape(hsv_roi.shape)

    # Sort pixels vertically by value
    sorted_roi = np.array(sorted(sorted_roi.reshape(-1, 3), key=lambda x: x[2], reverse=True)).reshape(sorted_roi.shape)

    # Replace the original ROI with the sorted one
    image[y:y+h, x:x+w] = cv2.cvtColor(sorted_roi, cv2.COLOR_HSV2BGR)

    return image
def blur_region(image, bbox, blur_factor=5):
    # Extract the bounding box coordinates
    x, y, w, h = bbox

    # Extract the region of interest (ROI)
    roi = image[y:y+h, x:x+w]

    # Apply Gaussian blur to the ROI
    blurred_roi = cv2.GaussianBlur(roi, (blur_factor, blur_factor), 0)

    # Replace the original region with the blurred one
    image[y:y+h, x:x+w] = blurred_roi

    return image

imagePath = input("path: ")

img = cv2.imread(imagePath)

grayscale = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

## start detect 

detector = dlib.get_frontal_face_detector()
faces = detector(grayscale, upsample_num_times=5)

## end detect

for i, face in enumerate(faces):
    bbox = (face.left(), face.top(), face.width(), face.height())
    print(f"scrubbing face number {i}")
    img = sort_pixels(img.copy(), bbox)

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

filename, extension = path.splitext(path.basename(imagePath))
new_filename = filename + "_scrubbed" + '.png'

print(f"wrote to {new_filename}")
cv2.imwrite(new_filename, img)
