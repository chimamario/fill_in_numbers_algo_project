import pandas as pd
import numpy as np


import re
import pytesseract
from PIL import Image
import copy
import cv2

def create_number_dict(numbers):
    main_number_dict = {}
    for i in range(3,10):
        nums_test = [n for n in numbers if len(n) == i]
        if len(nums_test) > 0:
            main_number_dict[i] = nums_test
    return main_number_dict

# main_number_dict = create_number_dict(numbers)

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
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    custom_config = r'--psm 11 --oem 3 -c tessedit_char_whitelist=0123456789'
    
    raw_text = pytesseract.image_to_string(img, config=custom_config)
    
    numbers_list = [num for num in re.findall(r'\d+', raw_text)]
    
    return numbers_list

def extract_matrix_and_nums(image_path, remove_nums = None, add_nums = None):
    image = preprocess_and_warp(image_path)
    boolean_matrix = create_matrix(image)

    numbers= extract_clean_numbers("test_photo_v7.jpg")
    
    

    if remove_nums:
        numbers = [item for item in numbers if item not in remove_nums]
    if add_nums:
        numbers.extend(add_nums)
    
    
    main_number_dict= create_number_dict(numbers)
    for key, value in main_number_dict.items():
        print(f"{key}: {sorted(value)}")
    print("\n")
    input("Please Check if Numbers match, Press anything to continue: ")

    
    return boolean_matrix, main_number_dict