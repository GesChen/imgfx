import dlib
import cv2
import numpy as np

def get_face_landmarks(image_path):
    # Load the image and downscale by 50%
    image = cv2.imread(image_path)
    image = cv2.resize(image, None, fx=0.5, fy=0.5)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load the pre-trained face detector
    detector = dlib.get_frontal_face_detector()

    # Detect faces in the image
    faces = detector(gray)

    if len(faces) == 0:
        print("No faces found in the image.")
        return None

    # Load the alternative facial landmarks predictor with 81 points
    predictor = dlib.shape_predictor("shape_predictor_81_face_landmarks.dat")

    # Get landmarks for all detected faces
    all_landmarks = [predictor(gray, face) for face in faces]

    return all_landmarks
def apply_blur_inside_polygon(image, polygon, blur_radius):
    # Create a mask with the polygon filled with white
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [polygon], (255, 255, 255))

    # Convert the mask to a binary mask
    binary_mask = cv2.threshold(cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY), 128, 255, cv2.THRESH_BINARY)[1]

    # Blur the entire image
    blurred_image = cv2.GaussianBlur(image, (blur_radius * 2 + 1, blur_radius * 2 + 1), 0)

    # Replace the pixels inside the polygon with the corresponding pixels from the blurred image
    result = image.copy()
    for i in range(image.shape[2]):
        result[:, :, i][binary_mask != 0] = blurred_image[:, :, i][binary_mask != 0]

    return result


def blur_convex_hull(image, all_landmarks):
    for landmarks in all_landmarks:
        # Extract all facial landmarks
        all_points = [(p.x, p.y) for p in landmarks.parts()]

        # Convert points to a NumPy array
        all_points = np.array(all_points, dtype=np.int32)

        # Create a convex hull around all facial landmarks
        hull = cv2.convexHull(all_points)

        # Draw the convex hull on the image
        
        image = apply_blur_inside_polygon(image.copy(), hull, 200)

    return image

def main():
    image_path = 'tennis.png'

    all_landmarks = get_face_landmarks(image_path)

    if all_landmarks is not None:
        image = cv2.imread(image_path)
        image = cv2.resize(image, None, fx=0.5, fy=0.5)  # Downscale by 50%
        image_with_outlines = blur_convex_hull(image.copy(), all_landmarks)

        # Display the original downscaled image and the image with head outlines
        cv2.imshow('Downscaled Image', image)
        cv2.imshow('Head Outlines', image_with_outlines)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
