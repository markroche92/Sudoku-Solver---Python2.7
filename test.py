import os
import csv
from solve import solve
from classes import Board

test_dir = os.path.join('C:\\','Users','markr','OneDrive','Documents','GitHub','Sudoku-Solver','Tests')
os.chdir(test_dir)
test_inputs = [(filename,filename.split('incomplete')[1]) for filename in os.listdir(os.curdir) if 'incomplete' in filename]
for filename in test_inputs:
    with open(filename[0]) as f:                                                                   # Open the incomplete sudoku puzzle
        reader = csv.reader(f, delimiter = ' ')                                                 # Read file
        grid_init = [list(map(int,num)) for num in reader]                                      # Import data as a list of lists of integers
        
        Grid = Board(grid = grid_init)

        for col in range(0,9):
            Grid.Cols[col].get_cells()
        Grid.get_cell_ranges()
        
        Grid_List = [Grid]            
                     
        solved = solve(Grid_List)
        
        
        
    if solved[0]:
        with open("".join("solution",filename[1]),"w") as text_file:
            for row in solved[1].value:
                for i,element in enumerate(row):
                    text_file.write(str(element))
                    if i == len(row)-1:
                        text_file.write("\n")
                    else:
                        text_file.write(" ")