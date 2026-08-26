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

#obtain all coordinates of all 'True Space values'
def obtain_coordinates(matrix):
    coordinates =  []
    for i, array in enumerate(matrix):
        current_set = [] #obtain connected cells, add to dictionary and then reset for other set
        trigger=False
        for x, a in enumerate(array):
            
            #starts with false
            if a == False and trigger == False:
                continue
            elif a==True and trigger == False:
                # curent_set = []
                trigger = True
                current_set.append((i,x))
            elif a == True and trigger == True:
                current_set.append((i,x))
            elif a == False and trigger == True: #assume num section has ended and set needs to be reset
                trigger = False
                coordinates.append(current_set)
                current_set = []
            if x == (len(array) - 1): #check when loop is at the end of array
                if len(current_set) == 0:
                    continue
                coordinates.append(current_set)
    return coordinates

hori_coords = obtain_coordinates(proper_matrix)

#get transpose of matrix and obtain those coordinates as well
vertical_matrix = proper_matrix.T
vert_coords = obtain_coordinates(vertical_matrix)
#now flip these coordinate directions (to align with hori_coords)

new_vert_coords = []
for array in vert_coords:
    new_array = []
    for coord in array:
        x,y = coord
        new_array.append((y,x))
    new_vert_coords.append(new_array)


#this needs to be here so that pop does not keep iterating
quick_dict = {}
for i in range(3,10):
    nums_test = [n for n in numbers if len(n) == i]
    if len(nums_test) > 0:
        quick_dict[i] = nums_test

number_dict = quick_dict

#im thinking we all the two lists together to be in one place
all_coords = new_vert_coords + hori_coords
coords_ranked = sorted(all_coords, key=len, reverse=True)#now create hiearchy system to decide which order to try number cells

current_set = coords_ranked[0] #might use pop method later
current_set = set(current_set)

#check which sets have the same coords
common_sets = []
for check_set in coords_ranked:
    check_set = set(check_set)
    common_coords = current_set.intersection(check_set)
    if check_set != current_set and len(common_coords) > 0:
        common_sets.append(check_set)

vicinity_set = []
for x,y in current_set:
    up = x + 1
    down = x-1
    left = y-1
    right = y+1
    vicinity_set.extend([(up,y), (down, y), (x,left), (x,right)])


vicinity_set = set(vicinity_set)

vicinity_set = vicinity_set - current_set


#number_list is based on the length of the selected set of coords
length = len(current_set)
number_list = main_number_dict[length] 

#initial matrixt should be created. And within the Class script the main guess should be added
current_matrix = [[None for i in range(13)] for i in range(13)]
#MatrixIterator needs the following (note that well need another class or full on function to get these values):

first_guess = number_list[3]
print(f"first_guess: {first_guess}") #numbers of 1st guess
print(f"current_set: {current_set}")#coordinates of main guess
print(f"main_number_dict: {main_number_dict}") #list of all numbers (organized)
print(f"common_sets: {common_sets}") #list of coordinates that include the same coordinates as current_set
print(f"vicinity_set: {vicinity_set}") #list of coordinates that are in the vicinity
#debating if we need all that code about orientation (tbh)

class MatrixIterator:
    def __init__(self, first_guess, current_set, common_sets, vicinity_set, main_number_dict, current_matrix):
        self.first_guess = first_guess
        self.current_set = current_set
        self.common_sets = common_sets
        self.vicinity_set = vicinity_set
        self.main_number_dict = main_number_dict

        self.child_nodes = {}
        self.ranking = None
        
        #a lil check to determine if guesses are horizontal or vertical
        #this is to help with order of coordinates
        self.which_axis = None
        which_check_set = list(current_set)
        if which_check_set[0][0] == which_check_set[1][0]: #same row
            self.which_axis= 'row'
            correct_order_first_guess = sorted(which_check_set, key=lambda item:item[1])
        else: #does down col row
            self.which_axis = 'col'
            correct_order_first_guess = sorted(which_check_set)

        # add init code to store guess into current matrix
            #making sure order of current_set is preserved before adding into matrix
        
        for i, (x,y) in enumerate(correct_order_first_guess):
            current_matrix[x][y] = self.first_guess[i]
        
        self.current_matrix = current_matrix
        
        #note to self - if which_axis is col, then common_sets are rows and need to be
        #treated accordingly
    
    def check_iso_guess_cases(self, iterator_check = False):
        iso_list = [] #add all guesses that have one 1 input into list
        intermiediate_common_sets = self.common_sets.copy() #doing this because we can't adjust the list we are iterating mid way
        for c_set in intermiediate_common_sets: #scoop all possible numbers based on length
  
            

            intermediate_iso_list = []
            c_length = len(c_set)
            c_numbers = self.main_number_dict[c_length].copy()
        
            #now check for the same coordinates (only 1 set) in first guess and c_numbers
            common_coord = self.current_set & c_set
            common_coord = list(common_coord)[0]
            
            #based of which_axis, make sure to order common set so that we are comparing the correct number
            
            if self.which_axis == 'col':
                c_set = sorted(c_set, key=lambda item: item[1])
            else:
                c_set = sorted(c_set)
            
            c_set = list(c_set)

            if self.which_axis == 'col':
                c_set = sorted(c_set, key=lambda item: item[1])
            else:
                c_set = sorted(c_set)
            
            #obtain number based on coordinate and order of c_set
            position = c_set.index(common_coord)
            first_guess_number = self.current_matrix[common_coord[0]][common_coord[1]]
            potential_numbers = []
            for nums in c_numbers:
                if first_guess_number == nums[position]:
                    potential_numbers.append(nums)
                
            if len(potential_numbers) == 0:
                print(f"c_set: {c_set}, potential guesses: {potential_numbers}")
                if iterator_check == False: #if means this is the first itearation 
                    self.ranking = 0
                    return False, [], False
                else:
                    continue
            elif len(potential_numbers) == 1: #input value into matrix
                print(f"c_set: {c_set}, potential guesses: {potential_numbers}")
                
                pot_num = potential_numbers[0] #extract number
                iso_list.append(pot_num)
                intermediate_iso_list.append(pot_num)
                
                for i, (x,y) in enumerate(c_set): #add to matrix
                    self.current_matrix[x][y] = pot_num[i]
                
                #IMPORTANT YOU ALSO NEED TO REMOVE SET FROM COMMON_SET
                #remove number from dictionary
                    
                #REMOVING VALUE DAMAGES THE ORDER AND THEREFORE SKIPS STEPS
                c_numbers.remove(pot_num) 
                # print(common_sets)
                print(f"gonna remove this c-set: {c_set}")
                c_set = set(c_set)
                self.common_sets.remove(c_set)

                self.main_number_dict[c_length] = c_numbers 
            else:
                print(f"c_set: {c_set}, potential guesses: {potential_numbers}")
                
                
            #NEXT  - store all the potential_numbers with 1 guess, remove the numbers from
            #main_number_dict and run through process again

            #how to - this function needs a self.matrix input for iterations. This function
            #also needs to be broken up to make it repeatable (another function that iterates until
            #there are no more iso guesses) 

            #if a value is filled in, then it must also be removed from the common_set dictionary.
        iterator_check = True
        return True, iso_list, iterator_check
            

    
    def main_function(self):
        iso_check, iso_list, iterator_check = self.check_iso_guess_cases()
        if iso_check == False:
            print(f"missing guesses so guess {self.first_guess} is ending its loop here, leaving a score of {self.ranking}")
        else:
            print(f"this guess ({self.first_guess}) has potential lets keep going")
            #this only accounts for two iterations, while loop will account for more
            iso_check, iso_list, iterator_check = self.check_iso_guess_cases(iterator_check) #make a while loop until iso list is empty
            #
        
        # if len(iso_list) > 0:
        #     #check for length of one number
        #     iso_length = len(iso_list[0])
        #     c_number_list = self.main_number_dict[iso_length] 

        #     # iso_set = set(iso_list)
        #     # filtered_list = [item for item in c_number_list if item not in iso_set]

        #     # print(iso_list)
        #     # print(filtered_list)

            

    def show_matrix(self):
        return self.current_matrix 
    
    def show_num_dict(self):
        return self.main_number_dict
            


    # def create_child_nodes(self, list_of_children):
        #after all the iso guess are iterated through, create the nodes new iterations to be created

    #functions required
    #1. storing child node object and results
        
    #2. creating guessing nodes
        
    #3. iterating through iso guesses and 


first_guess = first_guess = number_list[2]
print(number_list)
test1 = MatrixIterator(first_guess, current_set, common_sets, vicinity_set, main_number_dict, current_matrix)
test1.main_function()