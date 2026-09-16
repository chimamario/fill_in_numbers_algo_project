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

def create_number_dict(numbers):
    main_number_dict = {}
    for i in range(3,10):
        nums_test = [n for n in numbers if len(n) == i]
        if len(nums_test) > 0:
            main_number_dict[i] = nums_test
    return main_number_dict

main_number_dict = create_number_dict(numbers)

def preProcess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, warped = cv2.threshold(gray, 127,255, cv2.THRESH_BINARY)
    return warped



def preprocess_and_warp(image_path):
    
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image from {image_path}")
        
    orig = img.copy()
    
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    
    edged = cv2.Canny(blurred, 50, 150)
    
    
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    grid_contour = None
    
    
    for c in contours:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
        
        
        if len(approx) == 4:
            grid_contour = approx
            break
            
    if grid_contour is None:
        raise ValueError("Could not detect a 13x13 grid boundary in the image.")
        
    
    pts = grid_contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # top-left has smallest sum
    rect[2] = pts[np.argmax(s)] # bottom-right has largest sum
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # top-right has smallest difference
    rect[3] = pts[np.argmax(diff)] # bottom-left has largest difference

    #define the dimensions of our new output "flat" square image (e.g., 650x650 px)
    side_length = 650
    dst = np.array([[0,0],[side_length - 1, 0],
        [side_length - 1, side_length - 1],
        [0, side_length - 1]], dtype="float32")
    
    
    M = cv2.getPerspectiveTransform(rect, dst)
    warped_color = cv2.warpPerspective(orig, M, (side_length, side_length))
    
    
    warped_gray = cv2.cvtColor(warped_color, cv2.COLOR_BGR2GRAY)
    _, warped_binary = cv2.threshold(warped_gray, 127, 255, cv2.THRESH_BINARY)
    
    return warped_binary

def create_matrix(image):
    GRID_SIZE = 13
    cell_w = image.shape[1] // GRID_SIZE
    cell_h = image.shape[0] // GRID_SIZE
    
    boolean_matrix = []

    
    for row in range(GRID_SIZE):
        matrix_row = []
        for col in range(GRID_SIZE):
            
            x1 = col * cell_w
            y1 = row * cell_h
            x2 = x1 + cell_w
            y2 = y1 + cell_h
            
            
            cell = image[y1:y2, x1:x2]
            
            
            h, w = cell.shape
            center_sample = cell[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
            
            
            avg_brightness = np.mean(center_sample)
            
            
            is_white = avg_brightness > 127
            matrix_row.append(is_white)
            
        boolean_matrix.append(matrix_row)
    
    boolean_matrix = np.array(boolean_matrix, dtype=int)
    return boolean_matrix


def extract_clean_numbers(image_path):
    # 1. Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # 2. Resize (Tesseract prefers larger, clear text; at least 30-40px high)
    # Upscaling by 2x or 3x using cubic interpolation reduces pixelation
    img = cv2.resize(img, None, fx=6, fy=3, interpolation=cv2.INTER_CUBIC)

    # cv2.imshow("img", img)
    # cv2.waitKey(0)

    
    # # 3. Apply Thresholding (Converts to crisp black text on pure white background)
    # # Otsu's thresholding automatically calculates the optimal threshold value
    # # _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # thresh = cv2.adaptiveThreshold(
    #     img,
    #     255,
    #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #     cv2.THRESH_BINARY,
    #     11,
    #     2
    # )   

    # cv2.imshow("img", thresh)
    # cv2.waitKey(0)
    
    # 4. Strict Tesseract Configuration
    # --psm 11: Tells Tesseract to look for sparse, unordered text chunks
    # tessedit_char_whitelist: Strictly forces Tesseract to only see digits
    custom_config = r'--psm 11 --oem 3 -c tessedit_char_whitelist=0123456789'
    
    # 5. Extract text
    raw_text = pytesseract.image_to_string(img, config=custom_config)
    
    # 6. Parse numbers into a clean Python list using regex
    numbers_list = [num for num in re.findall(r'\d+', raw_text)]
    
    return numbers_list




# Usage
if __name__ == "__main__":

    numbers_v2 = extract_clean_numbers("test_photo_v7.jpg")
    # #make slight adjustments
    main_number_dict_v2 = create_number_dict(numbers_v2)

    for key, value in main_number_dict.items():
        print(f"{key}: {sorted(value)}")

    print("\n")
    for key, value in main_number_dict_v2.items():
        print(f"{key}: {sorted(value)}")
    # print(f"main_number_dict: {main_number_dict}")
    # print(f"main_number_dict_v2: {main_number_dict_v2}")
    print(len(numbers))
    print(len(numbers_v2))


    # image = preprocess_and_warp("test_photo_v3.jpg")
    # cv2.imshow("image", image)
    # cv2.waitKey(0)
    # boolean_matrix = create_matrix(image)


    # attempt1 = MatrixCoordinator(None,boolean_matrix, main_number_dict)
    # final_matrix = attempt1.main_coordinator()
    # print(final_matrix)





