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

def draw_head_outlines(image, all_landmarks):
    for landmarks in all_landmarks:
        # Extract all facial landmarks
        all_points = [(p.x, p.y) for p in landmarks.parts()]

        # Convert points to a NumPy array
        all_points = np.array(all_points, dtype=np.int32)

        # Create a convex hull around all facial landmarks
        hull = cv2.convexHull(all_points)

        # Draw the convex hull on the image
        cv2.polylines(image, [hull], isClosed=True, color=(255, 0, 0), thickness=2)

    return image

def main():
    image_path = 'IMG_8871.JPG'

    all_landmarks = get_face_landmarks(image_path)

    if all_landmarks is not None:
        image = cv2.imread(image_path)
        image = cv2.resize(image, None, fx=0.5, fy=0.5)  # Downscale by 50%
        image_with_outlines = draw_head_outlines(image.copy(), all_landmarks)

        # Display the original downscaled image and the image with head outlines
        cv2.imshow('Downscaled Image', image)
        cv2.imshow('Head Outlines', image_with_outlines)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
