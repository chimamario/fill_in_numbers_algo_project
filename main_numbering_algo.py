import pandas as pd
import numpy as np


import re
import pytesseract
from PIL import Image
import copy

from MatrixIterator import MatrixIterator
from MatrixCoordinator import MatrixCoordinator
from extract_matrix_and_nums import extract_matrix_and_nums

import cv2
import tkinter as tk







if __name__ == "__main__":
    boolean_matrix, main_number_dict = extract_matrix_and_nums("test_photo_v3.jpg", ['79552', '93775'], ['795521', '937751']) 
    print(boolean_matrix)
    # main_number_dict = create_number_dict(numbers)
    attempt1 = MatrixCoordinator(None,boolean_matrix, main_number_dict)
    final_matrix = attempt1.main_coordinator()


    





