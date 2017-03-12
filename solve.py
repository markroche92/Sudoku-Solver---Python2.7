from functions import get_all_remaining, remaining, get_base, get_unit_row_column             # Import additional functions

from classes import Grid                                                                       # Import Grid object

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
                    
                    # If Unit has 1 remaining empty cell, fill it #
                    cell = Grid.get_obj(row, col)                                                           # Get the (Row, Col, Unit, Cell) objects for the (row, col)
                    last_filled = try_fill_last_blank(row, col, cell)
                    if last_filled:
                        update = True
                        break
                    
                    # If there is a value which is an option for this cell, but is not #
                    # an option for any other cell in the row/column, enter this value #
                    empty_cells_in_row_col = Grid.Cells[row][col].get_empty_cells()                             # Once we have identified an empty cell, get list of all empty cells in it's row and column. This is a list of Cell objects
                    empty_row_col_possibilities = get_all_remaining(empty_cells_in_row_col)                     # Get the set of all possible values which can go in all of the empty cell's neighbours (in it's col and row)
                    possibilities_this_cell = remaining(cell[0], cell[1], cell[2], cell[3])                     # Return set of values which can go in this cell
                    options_for_only_this_cell = possibilities_this_cell.difference(empty_row_col_possibilities)# options_for_only_this_cell is the list of possibile values for this cell, which are not an option for any of the other empty cells in the unit
                    if len(options_for_only_this_cell) == 1:
                        num = options_for_only_this_cell.pop()                                                  # Convert set to integer
                        print "Update called, cell {},{}".format(row, col)
                        Grid.update(row, col, num)
                        update = True
                        break   
                    
                    # If there is a value which is an option for this cell, but is not #
                    # an option for any other empty cell in the unit, enter this value #
                    final_value = check_empty_unit_possibilities(cell[2], row, col, possibilities_this_cell)    # Considers values which can go in empty cells in the same unit. If a value can only go in this cell, return the value
                    if final_value:                                                                             # If final_value not None
                        print "Update called (new), cell {},{}".format(row, col)
                        Grid.update(row, col, final_value)                                                      # Update objects
                        update = True
                        break                                                                                   # If the cell has been updated, stop searching through possible values
                                                                                                                # If the cell has been updated, stop searching through possible values
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
                if Unit.value[i][j] == 0 and (base_row + i,base_col + j) != (row, col) and (not not_valid):# If (i,j) is the position of an empty cell, but not the position of the input empty cell, and not_valid flag has not been raised
                    if (base_row + i != row) and (base_col + j != col):     # If neither on same row nor column as the input cell
                        (Row, Col) = Grid.get_obj(base_row + i,base_col + j)[0:2]# Get the Row and Column object for cell which is neither on same column or row as the input cell
                        if (num not in Row.value) and (num not in Col.value):# If number is possible for this cell, stop considering this number
                            not_valid = True
                    elif base_row + i != row:                               # If not on the same column as the input cell
                        Row = Grid.get_obj(base_row + i,base_col + j)[0]         # Get the Row object for cell which is not on same row as input cell
                        if (num not in Row.value):                          # If number is possible for this cell, stop considering this number
                            not_valid = True
                    elif base_col + j != col:                               # If not on the same column as the input cell
                        Col = Grid.get_obj(base_row + i,base_col + j)[1]         # Get the Column object for the cell which is not on same column as input cell
                        if (num not in Col.value):                          # If number is possible for this cell, stop considering this number
                            not_valid = True
                else:                                                       # Skip populated cells, and the input cell
                    pass
        if not not_valid:                                                   # If for all of the other empty cells in the unit, the not_valid flag was not raised
            final_value = num                                               # Then output the num which was considered over this loop,  and break out of loop (no need to keep searching, as a valid value has been found)
            print "final val: {}".format(final_value)
            break
    return final_value
                    

#################################################################
#################################################################    

def try_fill_last_blank(row, col, cell):
    
    """ Basic attempt to update the final cell of a unit """
    
    (base_row, base_col) = get_base(row, col)                                            
    num_zeroes_unit = cell[2].get_num_blanks()                                          # Get the number of empty cells in the unit of this cell
    num_zeroes_col = cell[1].get_num_blanks()                                           # Get the number of empty cells in the column of this cell
    num_zeroes_row = cell[0].get_num_blanks()                                           # Get the number of empty cells in the row of this cell
    
    if num_zeroes_unit == 1:                                                            # If only one empty cell in this unit, just fill in the value
        print "Update last element of a unit"
        (rel_row, rel_col) = cell[2].rel_find(0)
        Grid.update(rel_row + base_row, rel_col + base_col, \
                    45 - sum([sum(x) for x in cell[2].value]))                          # Value in num field is equal to the number missing from the unit
        
        return True
    elif num_zeroes_col == 1:
        print "Update last element of a column"
        abs_row = cell[1].abs_find(0)
        Grid.update(abs_row, col, \
                    45 - sum(cell[1].value))                          # Value in num field is equal to the number missing from the unit
        
        return True
    elif num_zeroes_row == 1:
        print "Update last element of a row"
        abs_col = cell[0].abs_find(0)
        Grid.update(row, abs_col, \
                    45 - sum(cell[0].value))                          # Value in num field is equal to the number missing from the unit
        
        return True
    else:
        return False


  

# Run this code #

solved = solve()
 
if solved:
    with open("solution.txt","w") as text_file:
        text_file.write("Solution:\n")
        for row in Grid.value:
            text_file.write(str(row)+"\n")
