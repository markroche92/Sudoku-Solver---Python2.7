import csv
from functions import get_all_remaining, remaining, get_unit_row_column
# Load the initial grid from a text file

with open('incomplete.txt') as f:                   # Open the incomplete sudoku puzzle
    reader = csv.reader(f, delimiter = ' ')         # Read file
    grid = [list(map(int,num)) for num in reader]   # Import data as a list of lists of integers

#################################################################
#################################################################

# Define classes which represent each aspect of the sudoku grid #

class Board:
    
    def __init__(self, grid = grid):
        self.value = grid
        
    def full_list(self):
        
        """ Return all elements of the grid 
        as a single list """
        
        full_list = []
        for row in grid:
            full_list.extend(row)
        return full_list
        
    def update(self, row, col, val):
        
        """ Updates a single cell of the board
        with a certain value """
        
        self.value[row][col] = val
    
#################################################################

class Unit:
    
    def __init__(self, i, j, grid = grid):           # i is the row of the unit (1,2 or 3), j if the column of the unit (1,2 or 3)
        
        # Start and end rows, columns of the unit
        row_start = 3*i 
        col_start = 3*j
        row_end = 3*i + 2
        col_end = 3*j + 3
        
        # Extract the unit data as a list of lists        
        self.value = [grid[row_start][col_start:col_end], \
                       grid[row_start+1][col_start:col_end], \
                       grid[row_end][col_start:col_end]]
    
    def update(self, row, col, val):
        
        """ Change an element of the unit
        to a certain value """

        self.value[row][col] = val

    def total(self):
        
        """ Calculate the sum of values
        in the unit of the grid """
        
        total = 0
        for row in self.value:
            total+=sum(row)
        return total
        
    def check(self, val):
        
        """ Check if a certain value is
        present in the unit """
        
        flag = False
        for row in self.value:
            if val in row:
                flag = True
                break
        return flag
        
    def full_list(self):
        
        """ Get the full set of values present
        in a unit """
        
        full_list = set()
        for row in self.value:
            for num in row:
                full_list.add(num)
        return full_list
    
    def get_num_blanks(self):
        
        """ Get the number of blank cells
        within the unit """
        count = 0
        for row in self.value:
            for element in row:
                if element == 0:
                    count += 1
        return count
               
                
    
#################################################################
        
class Row:

    def __init__(self, row, grid = grid):
        self.value = grid[row]                       # Simply extract the row from the grid. This is a single list
        
    def update(self, col, val):
        
        """ Change an element of the row
        to a certain value """
        
        self.value[col] = val                        # Update the element with the value "val"
        
    def total(self):
        
        """ Calculate the sum of values
        in the row of the grid """
        
        return sum(self.value)
        
    def check(self, val):
        
        """ Check if a certain value is 
        present in the row """
        
        if val in self.value:
            return True
        else:
            return False

#################################################################
    
class Col:
    
    def __init__(self, col, grid = grid):
        self.value = []
        for row in range(0,9):
            self.value.append(grid[row][col])        # Column is a list
            
    def update(self, row, val):
        
        """ Change an element of the column
        to a certain value """
        
        self.value[row] =val                         # Update the element with the value "val"
        
    def total(self):
        
        """ Calculate the sum of values
        in the column of the grid """
        
        return sum(self.value)
        
    def check(self, val):
        
        """ Check if a certain value is 
        present in the column """
        
        if val in self.value:
            return True
        else:
            return False
    
        
#################################################################
#################################################################

# Create objects based on defined classes #

Grid = Board()

Row_0 = Row(0)
Row_1 = Row(1)    
Row_2 = Row(2)      
Row_3 = Row(3)
Row_4 = Row(4)    
Row_5 = Row(5)     
Row_6 = Row(6)      
Row_7 = Row(7)
Row_8 = Row(8)
RowList = [Row_0, Row_1, Row_2, Row_3, Row_4, Row_5, Row_6, Row_7, Row_8]    
      
Col_0 = Col(0)
Col_1 = Col(1)    
Col_2 = Col(2)      
Col_3 = Col(3)
Col_4 = Col(4)    
Col_5 = Col(5)
Col_6 = Col(6)
Col_7 = Col(7)    
Col_8 = Col(8)
ColList = [Col_0, Col_1, Col_2, Col_3, Col_4, Col_5, Col_6, Col_7, Col_8]

Unit_00 = Unit(0,0)
Unit_01 = Unit(0,1)                          
Unit_02 = Unit(0,2)    
Unit_10 = Unit(1,0)    
Unit_11 = Unit(1,1)    
Unit_12 = Unit(1,2)    
Unit_20 = Unit(2,0)    
Unit_21 = Unit(2,1)    
Unit_22 = Unit(2,2)

#################################################################
#################################################################

def solve():
    
    """ Run a loop to fill in cell values
    which cannot be entered in neighbours"""
    
    while 0 in Grid.full_list():                                                                            # While there are still empty grid cells
        update = False                                                                                      # Initialise update to False
        for row in range(0,9):                                                                              # Search each row (0 -> 8), zero based
            for col in range(0,9):                                                                          # Search each column in each row (0 -> 8), zero based
                if Grid.value[row][col] == 0:                                                               # If this cell is empty
                    print "Searching for {},{}".format(row,col)  
                    empty_cells = get_empty_cells(row,col)                                                  # Once we have identified an empty cell, get list of all empty cells in it's row and column. This is a list of (Row, Column) tuples.
                    other_cell_possibilities = get_all_remaining(empty_cells)                               # Get the set of all possible values which can go in all of the empty cell's neighbours (in it's col and row)
                    cell = get_obj(row, col)                                                                # Get the Row, Col, Unit object corresponding to the cell

                    num_zeroes = cell[2].get_num_blanks()                                                   # Get the number of empty cells in the unit of this cell
                    if num_zeroes == 1:                                                                     # If only one empty cell in this unit, just fill in the value
                        update_all(row,col,45 - sum([sum(x) for x in cell[2].value]))                       # Value in num field is equal to the number missing from the unit
                        print "Update called (new 2), cell {},{}".format(row, col)        
                        update = True
                        break
                    possibilities_this_cell = remaining(cell[0], cell[1], cell[2])                          # Return set of values which can go in this cell
                    final_value = check_empty_unit_possibilities(cell[2], row, col, possibilities_this_cell)# Considers values which can go in empty cells in the same unit. If a value can only go in this cell, return the value
                    options_for_only_this_cell = possibilities_this_cell.difference(other_cell_possibilities)# options_for_only_this_cell is the list of possibile values for this cell, which are not an option for any of the other empty cells in the unit
                    
                    if final_value:                                                                         # If final_value not None
                        update_all(row, col, final_value)                                                   # Update objects
                        print "Update called (new), cell {},{}".format(row, col)
                        update = True
                        break                                                                               # If the cell has been updated, stop searching through possible values
                    elif len(options_for_only_this_cell) == 1:
                        num = options_for_only_this_cell.pop()                                              # Convert set to integer
                        update_all(row, col, num)
                        print "Update called, cell {},{}".format(row, col)
                        update = True
                        break                                                                               # If the cell has been updated, stop searching through possible values
                    else:
                        pass
                else:                                               # If the cell is populated, go to the next cell
                    pass
        if not update:                                              # If you have iterated through all rows and columns, without updating, quit and raise flag
            print "Dead end reached. No more progress possible with basic algorithm"
            Grid.value
            break
    if 0 not in Grid.full_list():
        return True
    else:
        return False

#################################################################
#################################################################
        
def check_empty_unit_possibilities(Unit, row, col, possibilities_this_cell):
    
    """ Check the other empty cells in the unit. If an element of possibilities_this_cell
    is not an option for any of the other empty cells in this unit, return this cell value """
    
    (base_row, base_col) = get_base(row, col)                               # Get the base column and row for the row and column of the cell being considered
    final_value = None                                                      # Initialise the final_value to None
    for num in possibilities_this_cell:                                     # Search all cells in unit, for if they can take each possibility for input cell
        not_valid = False                                                   # Every possible number if initially considered valid
        for i in range(0,3):                                                # Iterate from 0 -> 2 (all rows in a unit)
            for j in range(0,3):                                            # Iterate from 0 -> 2 (all columns in a unit)
                if Unit.value[i][j] == 0 and (i,j) != (row,col) and (not not_valid):# If (i,j) is the position of an empty cell, but not the position of the input empty cell, and not_valid flag has not been raised
                    if (base_row + i != row) and (base_col + j != col):     # Iif neither on same row nor column as the input cell
                        (Row, Col) = get_obj(base_row + i,base_col + j)[0:2]# Get the Row and Column object for cell which is neither on same column or row as the input cell
                        if (num not in Row.value) and (num not in Col.value):# If number is possible for this cell, stop considering this number
                            not_valid = True
                    elif base_row + i != row:                               # If not on the same column as the input cell
                        Row = get_obj(base_row + i,base_col + j)[0]         # Get the Row object for cell which is not on same row as input cell
                        if (num not in Row.value):                          # If number is possible for this cell, stop considering this number
                            not_valid = True
                    elif base_col + j != col:                               # If not on the same column as the input cell
                        Col = get_obj(base_row + i,base_col + j)[1]         # Get the Column object for the cell which is not on same column as input cell
                        if (num not in Col.value):                          # If number is possible for this cell, stop considering this number
                            not_valid = True
                else:                                                       # Skip populated cells, and the input cell
                    pass
        if not not_valid:                                                   # If for all of the other empty cells in the unit, the not_valid flag was not raised
            final_value = num                                               # Then output the num which was considered over this loop,  and break out of loop (no need to keep searching, as a valid value has been found)
            break
    return final_value
                    




        
#################################################################
#################################################################      

def get_base(row, col):
    
    """ Return the base row and column
    of the unit for a given cell """
    
    if row >= 6:                                                    # For row number, get the base row number (i.e. where the unit starts)
        base_row = 6
    elif row >= 3:
        base_row = 3
    else:
        base_row = 0
        
    if col >= 6:                                                    # For column number, get the base column number (i.e. where the unit starts)
        base_col = 6
    elif col >= 3:
        base_col = 3
    else:
        base_col = 0
    
    return (base_row, base_col)                                     # Return base (row, column) tuple
        
#################################################################
#################################################################


def get_empty_cells(row,col):
    
    """ Get the list of cells which are empty,
    within the column and row of the considered cell """
    
    (Row, Col, Unit) = get_obj(row, col)                            # Get (Row, Col, Unit) objects for the row and column number 
    empty_cells = []                                                # Initialise empty cell list
    for j, c in enumerate(Row.value):
        if j == col:                                                # Skip the input cell
            pass
        elif c == 0:
            empty_cells.append(get_obj(row,j))
        else:
            pass
    for i, r in enumerate(Col.value):
        if i == row:                                                # Skip the input cell
            pass
        elif r == 0:
            empty_cells.append(get_obj(i,col))
        else:
            pass
    return empty_cells                                              # Return the list of (Row,Cell) obects in tuple format
    
#################################################################
#################################################################

def get_obj(row, col):
    
    """ Return the Row, Column, Unit objects 
    for an input row and column """
    
    if row == 0:                                                    # Check row number    
        Row = Row_0
    elif row == 1:
        Row = Row_1
    elif row == 2:
        Row = Row_2
    elif row == 3:
        Row = Row_3
    elif row == 4:
        Row = Row_4
    elif row == 5:
        Row = Row_5
    elif row == 6:
        Row = Row_6
    elif row == 7:
        Row = Row_7
    elif row == 8:
        Row = Row_8
    else:
        Row = None

    if col == 0:                                                    # Check column number
        Col = Col_0
    elif col == 1:
        Col = Col_1
    elif col == 2:
        Col = Col_2
    elif col == 3:
        Col = Col_3
    elif col == 4:
        Col = Col_4
    elif col == 5:
        Col = Col_5
    elif col == 6:
        Col = Col_6
    elif col == 7:
        Col = Col_7
    elif col == 8:
        Col = Col_8
    else:
        Col = None
        
    (u_row, u_col) = get_unit_row_column(row, col)                  # Get the unit row and column number for the actual row and column number
       
    if u_row == 0 and u_col == 0:
        Unit = Unit_00
    elif u_row == 0 and u_col == 1:
        Unit = Unit_01   
    elif u_row == 0 and u_col == 2:
        Unit = Unit_02           
    elif u_row == 1 and u_col == 0:
        Unit = Unit_10           
    elif u_row == 1 and u_col == 1:
        Unit = Unit_11   
    elif u_row == 1 and u_col == 2:
        Unit = Unit_12   
    elif u_row == 2 and u_col == 0:
        Unit = Unit_20  
    elif u_row == 2 and u_col == 1:
        Unit = Unit_21
    elif u_row == 2 and u_col == 2:
        Unit = Unit_22     
    else:
        Unit = None
          
    return (Row, Col, Unit)                                         # Return a tuple of (Row, Column, Unit)
    
#################################################################
#################################################################

 
def check_unit_row_col(row, col, val):
    
    """ Function checks the appropriate
    unit, col, row of the sudoku board for a value"""
    
    flag = False                                                    # Initialise flag
    (Row, Col, Unit) = get_obj(row, col)                            # Get the Row, Column, Unit for the row and column number
    flag = Unit.check(val) or Row.check(val) or Col.check(val)      # If value is in Row, Column, Unit, raise the flag
    return flag                                                     # Return True if the value is in the row, column of the unit of the input cell
    
#################################################################
#################################################################


def update_all(row, col, val):
    
    """ Function changes the appropriate objects of the sudoku board
    for an input row, column and value """
    
    Grid.update(row, col, val)                                      # Update the Grid, Row, Column, Unit objects
    (Row, Col, Unit) = get_obj(row, col)                            # For the row and column number, get the Row, Column, Unit objects
    Row.update(col, val)                                            # Update row object
    Col.update(row, val)                                            # Update column object
    (base_row, base_col) = get_base(row, col)                       # Get the base row and column of the unit within the board
    Unit.update(row - base_row, col - base_col, val)                # Update unit object
        
#################################################################
#################################################################


# Run this code #

solved = solve()
 
if solved:
    with open("solution.txt","w") as text_file:
        text_file.write("Solution:\n")
        for row in Grid.value:
            text_file.write(str(row)+"\n")
