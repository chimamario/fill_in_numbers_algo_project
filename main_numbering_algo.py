import pandas as pd
import numpy as np


import re
import pytesseract
from PIL import Image
import copy

from MatrixIterator import MatrixIterator
from MatrixCoordinator import MatrixCoordinator

import cv2


#Obtain numbers from the picture
img = Image.open("test_photo_v3.jpg")
extracted_text = pytesseract.image_to_string(img)
numbers = re.findall(r'\d+', extracted_text)
# numbers = [int(num) for num in numbers]
numbers = sorted(numbers)
numbers.remove('40060637')
numbers.remove('737')
numbers.remove('0420')
numbers = numbers + ['3273', '4737', '49447', '96283', '97114', '277034500', '940060637', '133', '841']
numbers = list(set(numbers))


#remove 737, 0420, remove40060637
#add 3273, 4737, 49447, 96283, 97114, all 9  numbers

main_number_dict = {}
for i in range(3,10):
    nums_test = [n for n in numbers if len(n) == i]
    if len(nums_test) > 0:
        main_number_dict[i] = nums_test


def preProcess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, warped = cv2.threshold(gray, 127,255, cv2.THRESH_BINARY)
    # imgBlur = cv2.GaussianBlur(imgGrey, (5,5), 1)
    # imgThreshold = cv2.adaptiveThreshold(imgBlur, 255,1,1,11,2)
    return warped



def preprocess_and_warp(image_path):
    # 1. Load the image and keep a copy
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image from {image_path}")
        
    orig = img.copy()
    
    # 2. Convert to grayscale and blur to remove texture/noise
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 3. Use Canny Edge Detection
    edged = cv2.Canny(blurred, 50, 150)
    
    # 4. Find all contours in the image
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area, keeping the largest ones
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    grid_contour = None
    
    # Loop through contours to find the largest 4-sided polygon
    for c in contours:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
        
        # If our contour has 4 points, we assume it's the grid boundary
        if len(approx) == 4:
            grid_contour = approx
            break
            
    if grid_contour is None:
        raise ValueError("Could not detect a 13x13 grid boundary in the image.")
        
    # 5. Reorder the 4 points consistently: [top-left, top-right, bottom-right, bottom-left]
    pts = grid_contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # top-left has smallest sum
    rect[2] = pts[np.argmax(s)] # bottom-right has largest sum
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # top-right has smallest difference
    rect[3] = pts[np.argmax(diff)] # bottom-left has largest difference

    # 6. Define the dimensions of our new output "flat" square image (e.g., 650x650 px)
    side_length = 650
    dst = np.array([[0,0],[side_length - 1, 0],
        [side_length - 1, side_length - 1],
        [0, side_length - 1]], dtype="float32")
    
    # 7. Apply Perspective Warp
    M = cv2.getPerspectiveTransform(rect, dst)
    warped_color = cv2.warpPerspective(orig, M, (side_length, side_length))
    
    # 8. Convert the warped square to a clean binary image (pure black & white)
    warped_gray = cv2.cvtColor(warped_color, cv2.COLOR_BGR2GRAY)
    _, warped_binary = cv2.threshold(warped_gray, 127, 255, cv2.THRESH_BINARY)
    
    return warped_binary

def create_matrix(image):
    GRID_SIZE = 13
    cell_w = image.shape[1] // GRID_SIZE
    cell_h = image.shape[0] // GRID_SIZE
    # Initialize the empty 13x13 matrix
    boolean_matrix = []

    # 2. Loop through every cell
    for row in range(GRID_SIZE):
        matrix_row = []
        for col in range(GRID_SIZE):
            # Define the pixel boundaries of the current cell
            x1 = col * cell_w
            y1 = row * cell_h
            x2 = x1 + cell_w
            y2 = y1 + cell_h
            
            # Crop just this cell
            cell = image[y1:y2, x1:x2]
            
            # Take a sample of the center (ignoring the cell's borders)
            h, w = cell.shape
            center_sample = cell[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
            
            # Calculate average brightness (0 to 255)
            avg_brightness = np.mean(center_sample)
            
            # If bright, it's a white space (True). If dark, it's blacked out (False).
            is_white = avg_brightness > 127
            matrix_row.append(is_white)
            
        boolean_matrix.append(matrix_row)
    
    boolean_matrix = np.array(boolean_matrix, dtype=int)
    return boolean_matrix


image = preprocess_and_warp("test_photo_v3.jpg")
cv2.imshow("image", image)
cv2.waitKey(0)
boolean_matrix = create_matrix(image)


# #set up matrix board
# matrix = np.zeros((13,13))
# matrix = np.full((13,13), True, dtype = bool)

# #set black boxs as false
# matrix[0] = [1,1,0,0,0,0,0,1,1,1,0,0,0]
# matrix[1] = [1,1,0,0,0,0,0,0,1,0,0,0,0]
# matrix[2] = [1,1,0,0,0,0,0,0,1,0,0,0,0]
# matrix[3] = [1,1,1,0,0,0,1,0,0,0,0,0,1]
# matrix[4] = [1,0,0,0,0,1,0,0,0,1,0,0,0]
# matrix[5] = [1,0,0,0,1,0,0,0,0,1,0,0,0]
# matrix[6] = [0,0,0,1,0,0,0,0,0,1,0,0,0]
# matrix[7] = [0,0,0,1,0,0,0,0,1,0,0,0,1]
# matrix[8] = [0,0,0,1,0,0,0,1,0,0,0,0,1]
# matrix[9] = [1,0,0,0,0,0,1,0,0,0,1,1,1]
# matrix[10]= [0,0,0,0,1,0,0,0,0,0,0,1,1]
# matrix[11]= [0,0,0,0,1,0,0,0,0,0,0,1,1]
# matrix[12]= [0,0,0,1,1,1,0,0,0,0,0,1,1]

# proper_matrix = ~matrix



attempt1 = MatrixCoordinator(None,boolean_matrix, main_number_dict)
final_matrix = attempt1.main_coordinator()
print(final_matrix)





