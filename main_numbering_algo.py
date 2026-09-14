import pandas as pd
import numpy as np


import re
import pytesseract
from PIL import Image
import copy

from MatrixIterator import MatrixIterator
from MatrixCoordinator import MatrixCoordinator


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


#set up matrix board
matrix = np.zeros((13,13))
matrix = np.full((13,13), True, dtype = bool)

#set black boxs as false
matrix[0] = [1,1,0,0,0,0,0,1,1,1,0,0,0]
matrix[1] = [1,1,0,0,0,0,0,0,1,0,0,0,0]
matrix[2] = [1,1,0,0,0,0,0,0,1,0,0,0,0]
matrix[3] = [1,1,1,0,0,0,1,0,0,0,0,0,1]
matrix[4] = [1,0,0,0,0,1,0,0,0,1,0,0,0]
matrix[5] = [1,0,0,0,1,0,0,0,0,1,0,0,0]
matrix[6] = [0,0,0,1,0,0,0,0,0,1,0,0,0]
matrix[7] = [0,0,0,1,0,0,0,0,1,0,0,0,1]
matrix[8] = [0,0,0,1,0,0,0,1,0,0,0,0,1]
matrix[9] = [1,0,0,0,0,0,1,0,0,0,1,1,1]
matrix[10]= [0,0,0,0,1,0,0,0,0,0,0,1,1]
matrix[11]= [0,0,0,0,1,0,0,0,0,0,0,1,1]
matrix[12]= [0,0,0,1,1,1,0,0,0,0,0,1,1]

proper_matrix = ~matrix







attempt1 = MatrixCoordinator(None,proper_matrix, main_number_dict)
attempt1.main_coordinator()