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



def preprocess_and_warp(image_path, matrix_confirm):
    
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image from {image_path}")
    
    #crop photo for better contours
    height, width = img.shape[:2]
    img = img[:int(height * 2/3), :int(width * 8/10)]
    circle_img = img.copy()

    # cv2.imshow("Cropped", cropped)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
        
    orig = img.copy()
    
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    
    edged = cv2.Canny(blurred, 50, 150)

    
    
    
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cont_area = [(c, cv2.contourArea(c, False)) for c in contours]
    cont_area.sort(key=lambda x: x[1], reverse=True)
    num_to_filter = max(1, int(len(contours) * 0.10))
    filtered_contours = [c for c, p in cont_area[num_to_filter:]]
    
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
   

    #Important to check contour 
    # Draw all contours
    if not matrix_confirm:
        cv2.drawContours(
            img,           # image to draw on
            contours,      # contour list
            -1,            # -1 means draw all contours
            (0, 0, 255),   # Red in BGR
            7              # line thickness
        )

        # Display image
        cv2.imshow("Contours", img)

        # Wait until key is pressed
        cv2.waitKey(0)

        # Close window
        cv2.destroyAllWindows()


    
    
    c_dict = []
    print(f"contour length: {len(contours)}")
    for i, c in enumerate(contours):
    #printing out contour options for user to select
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
        # if (cv2.contourArea(c) > 25000) and (cv2.contourArea(c) < 40000) and (len(approx) == 4):
        if (cv2.contourArea(c) > 25000) and  (len(approx) == 4):
        # if len(c_dict) == 0:
            print(f"Contour {i}")
            print(f"Number of points: {len(c)}")
            print(f"Area: {cv2.contourArea(c)}")
            print(f"Bounding box: {cv2.boundingRect(c)}")
            print()
   
    for i, c in enumerate(contours):
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
        
        #if extremely large grid is detected
        if (cv2.contourArea(c) > 100_000) and (len(approx) == 4):

            x,y, w,h  = cv2.boundingRect(c)

            center_x = x + w / 2
            center_y = y + h / 2

            c_dict.append({
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "cx": center_x,
                "cy": center_y
            })
            print("large box detected")
            print(f"contour area: {cv2.contourArea(c)}")
            break
       
        
        # print("small box detected")
        if (cv2.contourArea(c) > 25000) and (cv2.contourArea(c) < 40000) and (len(approx) == 4): #note that width and height from cv2.boundingRect(c) should be very similar
            #we could even filter this out better by grouping the area values that way we know its one of the cells
            
            #figure out more robust way to filter

            x,y, w,h  = cv2.boundingRect(c)

            center_x = x + w / 2
            center_y = y + h / 2

            c_dict.append({
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "cx": center_x,
                "cy": center_y
            })

        
        #printing out contour options for user to select
        # print(f"Contour {i}")
        # print(f"Number of points: {len(c)}")
        # print(f"Area: {cv2.contourArea(c)}")
        # print(f"Bounding box: {cv2.boundingRect(c)}")
        # print()

    print(f"c_dict: {c_dict}")
    min_x = min(cell["x"] for cell in c_dict)
    min_y = min(cell["y"] for cell in c_dict)

    max_x = max(cell["x"] + cell["w"] for cell in c_dict)
    max_y = max(cell["y"] + cell["h"] for cell in c_dict)

    print(min_x, min_y)
    print(max_x, max_y)

    cv2.circle(circle_img, (min_x, min_y), 10, (0, 0, 255), -1)
    cv2.circle(circle_img, (min_x, max_y), 10, (0, 0, 255), -1)
    cv2.circle(circle_img, (max_x, min_y), 10, (0, 0, 255), -1)
    cv2.circle(circle_img, (max_x, max_y), 10, (0, 0, 255), -1)

    #important to check if correct coordinates were selected
    if not matrix_confirm:
        cv2.imshow("Image", circle_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    points = [
        (min_x, min_y), (min_x, max_y), (max_x, min_y), (max_x, max_y)
    ]
    contour = np.array(points, dtype=np.int32).reshape((4,2))

    pts = contour 
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

def extract_matrix_and_nums(image_path, remove_nums = None, add_nums = None, confirmed = False, matrix_confirm = False):
    image = preprocess_and_warp(image_path, matrix_confirm)
    if not matrix_confirm:
        cv2.imshow("test", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    boolean_matrix = create_matrix(image)

    numbers= extract_clean_numbers(image_path)
    
    

    if remove_nums:
        numbers = [item for item in numbers if item not in remove_nums]
    if add_nums:
        numbers.extend(add_nums)
    
    
    main_number_dict= create_number_dict(numbers)
    for key, value in main_number_dict.items():
        print(f"{key}: {sorted(value)}")
    print("\n")
    if not confirmed:
        input("Please Check if Numbers match, Press anything to continue: ")

    
    return boolean_matrix, main_number_dict


if __name__ == '__main__':
    preprocess_and_warp("Testing Folder/Puzzle 12 v2.jpg") 
    # preprocess_and_warp("test_photo_v3.jpg")