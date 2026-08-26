import numpy as np

rows = {}
new_rows = {}
row1 = np.ones(13)

#initialize rows to all be true
for i in range(0,13):
    rows[i] = np.full(13, True)

#placement of black boxes (no number option)
list1 = [1,2,8,9,10]
list2 = [1,2,9]
list3 = [1,2,9]
list4 = [1,2,3,7,13]
list5 = [1,6,10]
list6 = [1,5,10]
list7 = [4,10]
list8 = [4,9,13]
list9 = [4,8,13]
list10 = [1,7, 11,12,13]
list11 = [5,12,13]
list12 = [5,12,13]
list13 = [4,5,6,12,13]

list_of_lists = [list1, list2, list3, list4, list5, list6, list7, list8, list9, list10, list11, list12, list13]

#i meessed up the ordering by one
def new_list(list):
    new_list = []
    for num in list:
        new_num = num - 1
        new_list.append(new_num)
    return new_list
new_list_of_lists = []

for list_i in list_of_lists:
    list_i = new_list(list_i)
    new_list_of_lists.append(list_i)

# print(new_list_of_lists)

#changing name to original
list_of_lists = new_list_of_lists

row_keys = rows.keys()

row_key_list_dict = dict(zip(row_keys, list_of_lists))


for row_name in row_keys:
    row_i = rows[row_name]
    list_i = row_key_list_dict[row_name]

    for i in list_i:
        row_i[i] = False
    
    new_rows[row_name] = row_i
    
rows = new_rows

columns = []



test_rows = rows.values()




n_cols = len(rows[0])

for i in range(n_cols):
    column_i = [row[i] for row in test_rows]
    columns.append(column_i)


# for row in rows

columns = [[bool(x) for x in col] for col in columns]
rows = [[bool(x) for x in col] for col in test_rows]

print(f"columns: {columns}")
print(f"rows:{rows}")



# #maybe creating a class that connects the rows and columns 
#creating class to connect the relation between rows and columns
#there is a coordinate that relates to rows and columns. 

#if I wanted to do a search thorugh a 5 spaces horizontal (for example)
# - then I'd have to use the check if values are there vertically

#if I correctly find a value veritcally, then I'd need to add that value 
#to each row


#2026 we back.

#review the game again

#retracing steps
