import pandas as pd
import numpy as np


import re
import pytesseract
from PIL import Image


#Obtain numbers from the picture
img = Image.open("test_photo_v3.jpg")
extracted_text = pytesseract.image_to_string(img)
numbers = re.findall(r'\d+', extracted_text)
# numbers = [int(num) for num in numbers]
numbers = sorted(numbers)
numbers.remove('40060637')
numbers.remove('737')
numbers.remove('0420')
numbers = numbers + ['3273', '4737', '49447', '96283', '97114', '277034500', '940060637']
numbers = list(set(numbers))
# print(numbers)
# print(len(numbers))

#remove 737, 0420, remove40060637
#add 3273, 4737, 49447, 96283, 97114, all 9  numbers

main_number_dict = {}
for i in range(3,10):
    nums_test = [n for n in numbers if len(n) == i]
    if len(nums_test) > 0:
        main_number_dict[i] = nums_test
print(main_number_dict)