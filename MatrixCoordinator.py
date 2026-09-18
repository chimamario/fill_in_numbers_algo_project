import numpy as np

from MatrixIterator import MatrixIterator
from MatrixIterator import obtain_all_sets_v2
import copy

#If you want previous git history of this Class look m_n_a_v4.ipynb

def create_object_copy(number_list, current_set, common_sets, main_number_dict, current_matrix, all_coords, main_object = False):
    tracker_dict = {}
    for i, guess in enumerate(number_list):
        # Create isolated copies of everything being modified in main_function
        copied_current_set = copy.deepcopy(current_set)
        copied_common_sets = copy.deepcopy(common_sets)
        copied_main_dict   = copy.deepcopy(main_number_dict)
        copied_matrix      = copy.deepcopy(current_matrix)
        copied_coords      = copy.deepcopy(all_coords)

        # Pass the isolated copies into the instance
        if main_object:
            tracker_dict[f"{i}_{guess}"] = [ 
                None, 
                MatrixIterator(guess, copied_current_set, copied_common_sets, copied_main_dict, copied_matrix, copied_coords,main_object
                )
            ]
        else:
            tracker_dict[f"{i}_{guess}"] = [ 
                None, 
                MatrixIterator(guess, copied_current_set, copied_common_sets, copied_main_dict, copied_matrix, copied_coords)
            ]
            
        
    
    return tracker_dict





class MatrixCoordinator:

    def __init__(self, matrix_iterator, proper_matrix, main_number_dict):
        self.potential_kings = {} #a list of objects that pass the first check
        self.proper_matrix = proper_matrix
        self.main_number_dict = main_number_dict
        self.current_set_num = 0 
        self.node_storage = {}
        self.max_score = np.sum(proper_matrix)
        self.proper_matrix = proper_matrix
        self.final_matrix = None
        

    
    def get_max_score(self):
        object_values = list(self.node_storage.values())
        scores = []
        for section in object_values:
            scores.append(section[0])
        max_score = max(scores)
        return max_score
    
    def get_king_nodes(self):
        current_set_num = 0 #adjust later
        number_list, current_set, common_sets, main_number_dict, current_matrix, all_coords = obtain_all_sets_v2(self.proper_matrix, current_set_num, self.main_number_dict)
        print(number_list)
        tracker_dict = create_object_copy(number_list, current_set, common_sets, main_number_dict, current_matrix, all_coords)

        for name, item_and_ranking in tracker_dict.items(): 
            class_object = item_and_ranking[1]
            # print(f"main guess for iteation: {class_object.first_guess}")
            # print(f"the current set for main guess: {class_object.current_set}")
            class_object.main_function()
            
            if class_object.remove_node is False:
                item_and_ranking[0] = class_object.ranking

                print(f"{name} has the following remove_node status: {class_object.remove_node}")
                # self.potential_kings[name] = class_object #ranking should be stored in object so we don't have to keep track of it here
                self.potential_kings[name] = [class_object.ranking, class_object]

                
                # self.node_storage[name] = [class_object.ranking, class_object]

                # test1.add_children(name, class_object) #very useful for iteration section but for king section, rmoeve
        
        if len([*self.potential_kings.values()]) == 0:
            print("no solution with first guess, head over to second")
            print('I am thinking we make the whole function a while loop that stops once the len of this list is > 1')

    def iterate_and_create_nodes(self, main_object, prev_score): #figure out how to make this iterative without manually creating next step
       
        while prev_score < self.max_score: #we've reached infinite loop
            # if current_score == self.max_score:
            #     return True
                
            main_number_dict, current_matrix, all_coords= main_object.return_matrix_variables()
            if len(all_coords) == 0: #matrix is completely filled, end function
                self.final_matrix = main_object.show_matrix()
                return True
            
                
            
            number_list, current_set, common_sets, main_number_dict, current_matrix, all_coords = obtain_all_sets_v2(self.proper_matrix, self.current_set_num, main_number_dict, current_matrix, all_coords, first_guess = False) 
            tracker_dict = create_object_copy(number_list, current_set, common_sets, main_number_dict, current_matrix, all_coords, main_object = main_object)

            for name, item_and_ranking in tracker_dict.items(): 
                class_object = item_and_ranking[1]
                
                
                class_object.main_function()
                
                if class_object.remove_node is False:
                    # print(f"main guess and set:  {class_object.first_guess} and {class_object.current_set}")
                    item_and_ranking[0] = class_object.ranking
                    # self.potential_kings[name] = class_object #ranking should be stored in object so we don't have to keep track of it here
                    main_object.add_children(name, class_object)

                    #only continue recursion if class_object is worth exploring
                    current_score = self.get_max_score()
                    self.node_storage[name] = [class_object.ranking, class_object]
                    # self.iterate_and_create_nodes(class_object, current_score)
                    
                    if self.iterate_and_create_nodes(class_object, current_score):
                        return True
                else:
                    continue
        
            return False
           
            
            


    
    def main_coordinator(self):
        #establish the king nodes
        self.get_king_nodes()

        #calculate entire tree structure
        print(self.max_score)
        # current_score = self.get_max_score()

        temp_potential_kings = self.potential_kings.copy()

        for king, [ranking, main_object] in temp_potential_kings.items():
            self.node_storage = {}
            self.node_storage[king] = [main_object.ranking, main_object]
            
            print(temp_potential_kings)
            
            current_score = self.get_max_score() #note that if we do have more than 1 king I need to figure out how to reset score (don't use for loop, instead reset the self.node storage for every run.) #if king run doesn't work then just delete the storage
            found_solution = self.iterate_and_create_nodes(main_object, current_score)

            if found_solution:
                print(f'SOLUTION FOUND for {king}')
                break
            else:
                print(f"no solution in {king} iterate to next king")
                del self.potential_kings[king]
                
                continue

        print('matrix is complete I hope')
        print(self.final_matrix)
        return self.final_matrix
    




            
