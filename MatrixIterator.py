import numpy as np
import copy

#If you want previous git history of this Class look m_n_a_v4.ipynb

#Extremely important functions
def sort_coord_list(x_list, order):
        if order == 'row':
            return sorted(x_list, key=lambda item:item[1])
        else:
            return sorted(x_list)

def get_common_set_quickly(c_set, all_coords): #if works, you can add this function to obtain_all_sets function to reduce redundancy
    c_set = set(c_set)
    quick_common_sets = []
    for check_set in all_coords: #2 for 1 with the coords ranked later
        check_set = set(check_set)
        common_coords = c_set.intersection(check_set)
        if check_set != c_set and len(common_coords) > 0:
            check_set = list(check_set)
            quick_common_sets.append(check_set)
    
    return quick_common_sets

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

def obtain_all_sets_v2(matrix, current_set_num, main_number_dict,  current_matrix = None, all_coords = None, first_guess = True):

    #get all the coordinates
    if first_guess: #creation of all_coords
        hori_coords = obtain_coordinates(matrix)
        vertical_matrix = matrix.T
        vert_coords = obtain_coordinates(vertical_matrix)

        new_vert_coords = []
        for array in vert_coords:
            new_array = []
            for coord in array:
                x,y = coord
                new_array.append((y,x))
            new_vert_coords.append(new_array)
        
        all_coords = new_vert_coords + hori_coords

    
    coords_ranked = sorted(all_coords, key=len, reverse=True)
    

    #select the current_set you want to test (adjust later)
    
    current_set = coords_ranked[current_set_num] #might use pop method later
    current_set = set(current_set)

    common_sets = []
    for check_set in coords_ranked: #2 for 1 with the coords ranked later
        check_set = set(check_set)
        common_coords = current_set.intersection(check_set)
        if check_set != current_set and len(common_coords) > 0:
            common_sets.append(check_set)
    #obtain number list to select from.
    length = len(current_set)
    number_list = main_number_dict[length] 

    #obtain guess based off selection
    # guess = number_list[number_list_num]

    #initial matrixt should be created. And within the Class script the main guess should be added
    if first_guess:
        current_matrix = [[None for i in range(13)] for i in range(13)]
    # if '6103' in number_list:
    #     print(f"guesses: {number_list}") #numbers of 1st guess
    #     print(f"current_set: {current_set}")#coordinates of main guess
    #     print(f"main_number_dict: {main_number_dict}") #list of all numbers (organized)
    #     print(f"common_sets: {common_sets}") #list of coordinates that include the same coordinates as current_set

    return number_list, current_set, common_sets, main_number_dict, current_matrix, all_coords

class MatrixIterator:
    def __init__(self, first_guess, current_set, common_sets, main_number_dict, current_matrix, all_coords, father = None):
        self.first_guess = first_guess
        self.current_set = current_set
        self.common_sets = common_sets
        
        self.all_coords = all_coords
        self.main_number_dict = main_number_dict

        self.removed_sets = []
        self.removed_nums = []

        self.child_nodes = {}
        self.father = father
        self.ranking = None
        self.remove_node = False

        #first remove guess from dictionary
        g_length =len(first_guess)
        g_list = self.main_number_dict[g_length].copy()
        if first_guess in g_list:
            g_list.remove(first_guess)
        self.main_number_dict[g_length] = g_list
        
        #a lil check to determine if guesses are horizontal or vertical
        #this is to help with order of coordinates
        self.which_axis = None
        which_check_set = list(current_set)
        if which_check_set[0][0] == which_check_set[1][0]: #same row
            self.which_axis= 'row'
            self.correct_order_first_guess = sorted(which_check_set, key=lambda item:item[1])
        else: #does down col row
            self.which_axis = 'col'
            self.correct_order_first_guess = sorted(which_check_set)

        #inputs from instance have to be adjusted now based on row and col option?
        
        
        
        self.current_matrix = current_matrix
    
    # def check_if_num_in_matrix(self, c_set):
        
    def quick_current_set_check(self):

        potential_num = []
        
        current_list = sort_coord_list(list(self.current_set), self.which_axis)
        for (x,y) in current_list:
            potential_num.append(self.current_matrix[x][y])
        
        if all(item is None for item in potential_num):
            
            #this means matrix is empty at these slots
            return True
        elif any(item is None for item in potential_num):
            
                
            #partially filled, lets check it matches with the first guess we have
            #note that we are trusting that 
            for i, digit in enumerate(potential_num):
                if digit:
                    digit_check = self.first_guess[i] == digit 
                    if not digit_check:
                        return False
            return True #all digits match
        else: #make assumption that if it hits this condition, all numbers match:
            return True

        
    def matrix_check(self):
        temp_all_coords = self.all_coords.copy()
        acc_matrix = True
        for coord_list in temp_all_coords:
            c_list = sort_coord_list(coord_list, self.which_axis)
            n_list = self.main_number_dict[len(coord_list)]
            potential_number = []
            for (x,y) in coord_list:
                potential_number.append(self.current_matrix[x][y])
            
            if None not in potential_number:
                result  = "".join(num for num in potential_number)
                if result in n_list:
                    # print(f'{result} was not removed from main_number_dict')
                    self.all_coords.remove(coord_list)
                    n_list.remove(result)
                    self.main_number_dict[len(coord_list)] = n_list
                else:
                    print(f"{result} is not in matrix")
                    # self.remove_node = True
                    acc_matrix = False
                    
        return acc_matrix
    
    def check_iso_guess_cases(self, iterator_check = False):
        iso_list = [] #add all guesses that have one 1 input into list
        intermiediate_common_sets = self.common_sets.copy() #doing this because we can't adjust the list we are iterating mid way
        
        for c_set in intermiediate_common_sets: #scoop all possible numbers based on length
  
            c_length = len(c_set)
            c_numbers = self.main_number_dict[c_length].copy()
        
            #now check for the same coordinates (only 1 set) in first guess and c_numbers
            common_coord = self.current_set & c_set
            common_coord = list(common_coord)[0]
            
            #based of which_axis, make sure to order common set so that we are comparing the correct number
            
            if self.which_axis == 'col': #switch to row and first out which index is correct
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
            
            # if self.first_guess == '6073':
            #     print(f"{self.first_guess} for c_set {c_set} has the following potential_numbers: {potential_numbers}")
                
            if len(potential_numbers) == 0:
                
                if iterator_check == False: #if means this is the first itearation 
                    self.ranking = 0
                    return False, [], False
                else:
                    continue
            elif len(potential_numbers) == 1: #input value into matrix


                pot_num = potential_numbers[0] #extract number
                iso_list.append(pot_num)
                

                # print(f"current iso_list:{iso_list}")

              
                #get common coordinae sets of c_set (current common set we are iterating through)
                quick_common_sets = get_common_set_quickly(c_set, self.all_coords)
                quick_set_with_num = [set(q_list) for q_list in quick_common_sets if any(self.current_matrix[x][y] is not None for (x,y) in q_list)]
                if self.current_set in quick_set_with_num:
                    quick_set_with_num.remove(self.current_set) #removing the current set since it is redundant
                quick_set_with_num = [list(q_set) for q_set in quick_set_with_num]
                
                # print(f"set {c_set} has the following potential numbers: {pot_num} and here is quick_set_with_num: {quick_set_with_num}")
                

                for i, (x,y) in enumerate(c_set): #add to matrix
                    self.current_matrix[x][y] = pot_num[i]
                
            

                if len(quick_set_with_num) == 0:
                     # honestly I should just remove statement
                    iso_list.remove(pot_num)
                else:
                    for q_set in quick_set_with_num: #not sure why its called q_set but I want to be consisent
                        q_set = sort_coord_list(q_set, self.which_axis) #make sure list is in order
                        r_value = [self.current_matrix[x][y] for (x,y) in q_set] # this should provide a list of numbers and/or NONes
                        r_length = len(r_value)
                        r_number_list = self.main_number_dict[r_length]

                        if None not in r_value: #fully filled out list
                            r_num  = "".join(num for num in r_value if num is not None)
                            
                            if any(num == r_num for num in r_number_list):
                                #note that if number if fully listed, it is already in the matrix. just remove the r_set and the number from respective lists
                                r_number_list.remove(r_num)
                                self.main_number_dict[r_length] = r_number_list
                                self.all_coords.remove(q_set)
                                #check if q_set is also in common set
                                q_set = set(q_set)
                                if q_set in self.common_sets:
                                    self.common_sets.remove(q_set)

                                self.removed_sets.append(q_set)
                                self.removed_nums.append(r_num)
                            else:
                                if r_num in self.removed_nums:
                                    continue
                                    
                                else:
                                    continue
                                    # print(f"no number exists for r_value: {r_value} aka r_num: {r_num} here and since its only 1 option, we have to believe this combination is incorrect") #NOTE debug line
                                
                        
                        elif any(q_set): #for nums that are partially filled
                            # print("this set is partially filled") #NOTE debug line

                            potential_r_nums = {}
                            for i, digit in enumerate(r_value): 
                                if digit:
                                    add_to_list = [r_num for r_num in r_number_list if r_num[i] == digit]
                                    potential_r_nums[i] = add_to_list
                            
                            potential_r_nums_set = (set(sublist) for sublist in potential_r_nums.values())
                            potential_r_nums = list(set.intersection(*potential_r_nums_set))
                            # if self.first_guess == '6073':
                            #     print(f"potenital_r_num: {potential_r_nums} ")
                            # potential_r_nums = list(set(potential_r_nums)) #remove duplicates

                            # print(f"for {q_set}, here are the following numbers: {potential_r_nums}") #NOTE debug line
                            if len(potential_r_nums) == 1: #we found the only solution, add to matrix
                                
                                
                                for i, (x,y) in enumerate(q_set):
                                    self.current_matrix[x][y] = potential_r_nums[0][i]
                                if q_set in self.common_sets:
                                    self.common_sets.remove(q_set)
                                
                                r_number_list.remove(potential_r_nums[0])
                                self.main_number_dict[r_length] = r_number_list
                                self.all_coords
                                self.removed_sets.append(q_set)
                                self.removed_nums.append(potential_r_nums[0])

                                
                                self.all_coords.remove(q_set)
                                #check if q_set is also in common set
                                q_set = set(q_set)
                                if q_set in self.common_sets:
                                    self.common_sets.remove(q_set)
                                
                    
                #REMOVING VALUE DAMAGES THE ORDER AND THEREFORE SKIPS STEPS
                                    
                

                c_numbers.remove(pot_num) #REMOVE SET FROM COMMON_SET
                if c_set in self.all_coords:
                    self.all_coords.remove(c_set)
                c_set = set(c_set)
                self.common_sets.remove(c_set)
                self.removed_sets.append(c_set)
                self.removed_nums.append(potential_numbers[0]) 
                
                self.main_number_dict[c_length] = c_numbers #remove number from dictionary
            else:
                # if self.first_guess == '6073':
                #     print(f"just checking if {self.first_guess} hits this else condition ")
                # print(f"we are removing {c_set} from coords and common sets, {pot_num} from dictionary")
                continue
                
        iterator_check = True
        # print(f"iso_list: {iso_list}")
        return True, iso_list, iterator_check


    def vicinity_axis_check(self):

        vicinity_set = []

        if self.which_axis == 'row':
            #extract consistent row value
            get_coord = next(iter(self.current_set))[0] 
            # only look for coords above and below
            for (row, col) in self.current_set:
                vicinity_set.extend([(row - 1, col), (row + 1, col)])
            coord_to_check = [row-1, row+1]

            c_set_idx = 0
        else:
            #everything here might just be the function and the if statement will be within main function?
            get_coord = next(iter(self.current_set))[1] #make sure to do the same thing for rows #TODO get_coord_idx
            # print(get_coord)
            for (row, col) in self.current_set: #obtain all possible common sets in vicinity slots
                vicinity_set.extend([(row, col - 1), (row, col + 1)])
            #index values for function when necessary
            
            c_set_idx = 1
        return vicinity_set, c_set_idx, get_coord
    
    def check_vicinity_sets_v2(self): #testing function
        
        vicinity_set, c_set_idx, get_coord = self.vicinity_axis_check()
        #get vicinity sets here since its already organized
    
        intermiediate_all_coords = self.all_coords.copy()
        potential_vicinity_sets = []
        for c_set in intermiediate_all_coords:
            
            c_set = list(c_set)
            
            if (c_set[0][c_set_idx] == c_set[1][c_set_idx]) and abs(int(c_set[0][c_set_idx]) - int(get_coord)) == 1: #TODO for row, it will be if (c_set[0][0] == c_set[1][0]) and abs(int(c_set[0][0]) - int(get_coord)) 
                if any(item in vicinity_set for item in c_set):
                    potential_vicinity_sets.append(c_set)
        
        
        if len(potential_vicinity_sets) > 0: #note that it is impossible for this list to be empty. 
            #variable for all 
            for p_set in potential_vicinity_sets: #logic only works if we're assuming the coords are in order
                pot_vic_nums = []
                p_length = len(p_set)
                n_list = self.main_number_dict[p_length]
                

                #can we vectorize the approach above to only consider numbers that have more than 1 common connection
                vin_array = np.empty(len(p_set), dtype='object')
                for i, (x,y) in enumerate(p_set): #stores all real values from matrix into arrays (if not, None remains)
                    if self.current_matrix[x][y]:
                        vin_array[i] = self.current_matrix[x][y]
                
                pot_vic_nums = [ #selects all numbers that contain any digits from vin_array
                    num for num in n_list 
                    if all(vin_array[i] is None or num[i] == vin_array[i] for i in range(len(vin_array)))
                    ]

                
                #note that the for loops above may be inefficient and should be looked at later

                pot_vic_nums = set(pot_vic_nums) #remove duplicates numbers
                pot_vic_nums = list(pot_vic_nums)

                #after all vicinity values with only 1 option is added, now we can vet out the other cases
                if len(pot_vic_nums) >= 1:
                    
                    r_sets = [ #obtain all common sets that have a coordinate in p_set
                        sort_coord_list(list(r_set), self.which_axis) for r_set in self.common_sets
                        if any(item in r_set for item in p_set)
                    ]

                    r_arrays = {} #store the real numbers from r_sets. if cell is empty, "None" is in its place
                    p_set_r_or_c = []
                    if self.which_axis == 'row':
                        continue
                    else:
                        for i, (x,y) in enumerate(p_set):
                            if i == 0: #we need the first coord so that the numbering order with num_index is accurate
                                first_x = x #NOTE this has to change if the guess is a row instead
                                first_y = y

                            
                            p_set_r_or_c.append((x,y))
                            # if self.current_matrix[x][y] == None:
                            #     p_set_r_or_c.append((x,y))

                    #you have to order r_sets with respect to p_set_r_or_c
                    if self.which_axis == 'col':
                        r_sets = sorted(r_sets, key=lambda inner_list: inner_list[0][0])
                        
                    debug=3
                    for i, r_set in enumerate(r_sets): 
                        #use the row column instead
                        r_array = [self.current_matrix[x][y] if self.current_matrix[x][y] else None for (x,y) in r_set] 
                        key_value = tuple(p_set_r_or_c[i])
                        r_arrays[key_value] = r_array
                        
                    
                    pot_vic_nums_for_iter = pot_vic_nums.copy()
                    for num in pot_vic_nums_for_iter:
                        
                        for (x,y), array in r_arrays.items(): #this only looks at first value not entire set of coords
                            test_array = array.copy() #use a copy. don't change arrays until we found the number
                            
                            if self.current_matrix[x][y]:
                                continue
                            else: 
                                num_index = x - first_x 
                                array_index = y - first_y 

                                # print(f"array: {array}")
                                # print(f"num_index: {num_index}")
                                # print(f"array_index: {array_index}")

                                #replace None with respective num value #NOTE is this correct?
                                
                                num_input = num[num_index]
                                test_array[array_index] = num_input

                                result  = "".join(num for num in test_array if num is not None)

                                # print(f"result:{result}")

                                #now check there is a number in n_list that has the same number combination as result
                                num_check = [num for num in n_list if result in num]
                                if len(num_check) == 0: #no possible number
                                    # print(f"{num} does not work")
                                    pot_vic_nums.remove(num)
                                    # array = original_array
                                    # r_arrays[(x,y)] = original_array
                                    break
                    # print(f"new_ potential_vic numbers: {pot_vic_nums}")  #NOTE debug print value 

                    if len(pot_vic_nums) == 1:
                        # print(f"adding {pot_vic_nums[0]} to matrix") 
                        final_number = pot_vic_nums[0]

                        #first vicinity number to matrix and remove from main number list 
                        for i, (x,y) in enumerate(p_set): 
                            self.current_matrix[x][y] = pot_vic_nums[0][i]
                        
                        n_list.remove(pot_vic_nums[0])
                        self.main_number_dict[p_length] = n_list
                        #remove the all_coords list as well
                        intermiediate_all_coords.remove(p_set)

                        # now check for arrays
                        for (x,y) in p_set: #note that I wanted to only have 1 for loop but I need to remove values from main number list before looking at array for efficiency
                            # get array
                            another_array = r_arrays.get((x,y), None)
                            # print(f"r_sets: {r_sets}")
                            r_set_order = [s for s in r_sets if (x, y) in s]

                            # print(f"r_set_order: {r_set_order}")
                            
                            if another_array and len(r_set_order) == 1:
                                # print(f"another_array: {another_array}")
                                r_set_order = [s for s in r_sets if (x, y) in s][0] #confusing. I can just say r_set_order = r_set_order[0]

                                #find what index of the number based off (x,y) position in p_set
                                p_index = p_set.index((x,y))
                                # print(p_index) #NOTE debug print value
                                digit = final_number[p_index]

                                #find index of r_set based on r_set position
                                r_index = r_set_order.index((x,y))
                                debug = 1
                                #store value in r_set
                                another_array[r_index] = final_number[p_index]
                                # print(f"updated array: {another_array}") #NOTE debug print value
                                
                                another_array_length = len(another_array)
                                p_list = self.main_number_dict[another_array_length]
                                another_num_list = [ #selects all numbers that contain any digits from another_array
                                num for num in p_list 
                                if all(another_array[i] is None or num[i] == another_array[i] for i in range(len(another_array)))
                                ]
                                
                                # print(f"anothter_num_list: {another_num_list}") #NOTE debug print value

                                if len(another_num_list) == 1: #only 1 option for r_set
                                    # print(f"adding {another_num_list[0]} to {r_set_order}") #NOTE debug print value
                                    for  i, (x,y) in enumerate(r_set_order):
                                        self.current_matrix[x][y] = another_num_list[0][i]
                                    
                                    #removing number discovered in r_set case
                                    p_list.remove(another_num_list[0])
                                    self.main_number_dict[another_array_length] = p_list  
                                    intermiediate_all_coords.remove(r_set_order)

                # elif len(pot_vic_nums) == 1: #this is checked after (len > 1) check to make the next iteration easier
                #     last_num = pot_vic_nums[0]
                #     for i, (x,y) in enumerate(p_set):
                #         self.current_matrix[x][y] = last_num[i]  

                        
                #     n_list.remove(pot_vic_nums[0])
                #     self.main_number_dict[p_length] = n_list   
                #     intermiediate_all_coords.remove(p_set)
            

        #this section is using the coords list as a way to determine if any changes happened to the matrix.
        else: #for some reason, _ is empty
            intermiediate_all_coords = self.all_coords
            # print("found edge case") #NOTE debug line

        self.all_coords = intermiediate_all_coords
        # print(f"intermediate_coords: {intermiediate_all_coords}") #NOTE debug line             
        
        return intermiediate_all_coords

    def main_function(self):

        initial_check = self.quick_current_set_check()
        acc_mat_check = self.matrix_check()

        # #added this here so it can be conditional
        if initial_check and acc_mat_check:

            # print(f"{self.first_guess} attempt for set: {self.current_set}")

            for i, (x,y) in enumerate(self.correct_order_first_guess):
                self.current_matrix[x][y] = self.first_guess[i]
        
            


            iso_check, iso_list, iterator_check = self.check_iso_guess_cases()
            if (iso_check == True) or (len(iso_list) > 0):
                # print(f"this guess ({self.first_guess}) has potential lets keep going") #NOTE debug line

                #iso list (for 6103) is empty letting is skip while loop
                while len(iso_list) > 0:
                # while iterator_check == True:
                    iso_check, iso_list, iterator_check = self.check_iso_guess_cases(iterator_check) #make a while loop until iso list is empty
                    

            
                remaining_coords = self.check_vicinity_sets_v2()
                old_remaining_coords = []
                while remaining_coords != old_remaining_coords:
                    old_remaining_coords = remaining_coords
                    remaining_coords = self.check_vicinity_sets_v2()

                # self.matrix_check() #adjusts self.remove node to true if it finds incorrect number
        
            else:
                # print(f"{self.first_guess} failed the iso check (there were sections that had no solutions so it is not added to father dictionary)")
                self.ranking = sum(1 for row in self.current_matrix for val in row if val is not None)
                self.remove_node = True
                
        else:
            print(f'{self.first_guess} does not match with current matrix for cells {self.current_set}')
            self.remove_node = True

        
        debug = 4
        #ranking should be more so about the number of connections made but for now lets test just using the number of non_None values
        self.ranking = sum(1 for row in self.current_matrix for val in row if val is not None)
        if self.remove_node == False:
            print(f"Loop ends here for {self.current_set}. '{self.first_guess}' with False remove_node status. score of {self.ranking} ")
            debug = 5

    def show_matrix(self):
        return self.current_matrix 
    
    def show_num_dict(self):
        return self.main_number_dict
    
    def return_matrix_variables(self):
        #temporary - gonna remove self.current_set from coord list to make life easier but the "Matrix Coordinator" class should deal with it
        temp_current_set = sorted(list(self.current_set))
        if temp_current_set in self.all_coords:
            self.all_coords.remove(temp_current_set)

        debug=6
        return copy.deepcopy(self.main_number_dict), copy.deepcopy(self.current_matrix), copy.deepcopy(self.all_coords)
    
    def get_ranking(self):
        return self.ranking
    
    def add_children(self, name, child):
        self.child_nodes[name] = [child, child.ranking]

    


    

    
    
            


    