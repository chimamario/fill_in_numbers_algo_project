import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import re
import pytesseract
from PIL import Image
import copy

from MatrixIterator import MatrixIterator
from MatrixCoordinator import MatrixCoordinator
from extract_matrix_and_nums import extract_matrix_and_nums

import cv2
import tkinter as tk
import customtkinter as ctk

def show_matrix(matrix):
    plt.imshow(matrix, cmap='gray', interpolation='nearest')
    # Remove ticks and labels
    plt.xticks([])
    plt.yticks([])

    # Add grid lines between cells
    plt.grid(
        which='major',
        color='black',
        linestyle='-',
        linewidth=1
    )

    # Put grid lines at cell boundaries
    plt.xticks([x - 0.5 for x in range(1, 13)])
    plt.yticks([y - 0.5 for y in range(1, 13)])

     # Remove ticks and labels
    plt.tick_params(
        which='both',
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False
    )

    plt.title("13 x 13 Grid")
    plt.show()

def show_matrix_v2(boolean_matrix, final_matrix,main_number_dict, current_set):

    boolean_matrix = np.array(boolean_matrix, dtype=float)

    # print(boolean_matrix)

    plt.imshow(boolean_matrix, cmap='grey', interpolation='nearest')

    # Add values to cells
    for r in range(13):
        for c in range(13):

            if final_matrix[r][c] is not None:

                plt.text(
                    c,
                    r,
                    final_matrix[r][c],
                    ha='center',
                    va='center',
                    color='black',
                    fontsize=16
                )

    # Cell boundaries
    plt.xticks([x - 0.5 for x in range(1, 13)], minor=True)
    plt.yticks([y - 0.5 for y in range(1, 13)], minor=True)

    plt.grid(
        which='minor',
        color='black',
        linestyle='-',
        linewidth=1
    )

    # Remove ticks and labels
    plt.tick_params(
        which='both',
        bottom=False,
        left=False,
        labelbottom=False,
        labelleft=False
    )

    plt.title("13 x 13 Grid")

    if current_set:
        plt.title(f"Failed on current set: {current_set}")
        remaining_numbers = main_number_dict.values()
        extra_info = f"Remaining numbers left: {remaining_numbers}"
        plt.figtext(
        0.78, 0.5, 
        extra_info, 
        fontsize=10, 
        va='center',          # Vertically centers the text box
        ha='left',            # Aligns text inside to the left
        multialignment='left',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='whitesmoke', edgecolor='gray', alpha=0.5)
        )
    else:
        plt.title("Complete grid!!")

    plt.show()




if __name__ == "__main__":
    #Puzzle 11
    # boolean_matrix, main_number_dict = extract_matrix_and_nums("test_photo_v3.jpg", add_nums=['533', '133', '3273'], remove_nums=['0420'], confirmed = True) 

    #Puzzle 12
    boolean_matrix, main_number_dict = extract_matrix_and_nums("Testing Folder/Puzzle 12 v2.jpg", remove_nums=['141', '229'], confirmed = True) 
   

    #initial matrix without inputs
    # show_matrix(boolean_matrix)
    # correct_matrix = input("is matrix correct? [y or n]: ")
    # correct_matrix = correct_matrix.capitalize()

    correct_matrix = 'Y'
    if correct_matrix == 'Y':
        # main_number_dict = create_number_dict(numbers)
        attempt1 = MatrixCoordinator(None,boolean_matrix.copy(), main_number_dict)
        final_matrix, main_number_dict, current_set = attempt1.main_coordinator()
        show_matrix_v2(boolean_matrix, final_matrix, main_number_dict, current_set)
    else:
        print("Boolean_matrix is incorrect. Readjust photo.")




    





