from functions import get_all_remaining, remaining, get_base, get_unit_row_column             # Import additional functions

from classes import Grid                                                                       # Import Grid object

#################################################################
#################################################################

def solve():

    """ Run a loop to fill in cell values
    which cannot be entered in neighbours"""
    i=0
    while 0 in Grid.full_list():                                                                            # While there are still empty grid cells
        update = False                                                                                      # Initialise update to False
        for row in range(0,9):                                                                              # Search each row (0 -> 8), zero based
            for col in range(0,9):                                                                          # Search each column in each row (0 -> 8), zero based

                if Grid.value[row][col] == 0:                                                               # If this cell is empty
                    i+=1

                    print "{}".format(i)
                    #print "Range (8,8):{}".format(Grid.range[8][8])
                    old_range = Grid.range
                    x_wing(row,col,i)
                    if old_range != Grid.range:
                        print "X-wing range update"
                        update = True
                        break


                    # If Unit has 1 remaining empty cell, fill it #
                    cell = Grid.get_obj(row, col)                                                           # Get the (Row, Col, Unit, Cell) objects for the (row, col)
                    fill_col = fill_only_option_col(cell[3])
                    
                    if fill_col:
                        Grid.update(row,col,fill_col)
                        
                        update = True
                        
                    fill_row = fill_only_option_row(cell[3])
                    if fill_row:
                        Grid.update(row,col,fill_row)
                        update = True
                        
                    last_filled = try_fill_last_blank(row, col, cell)
                    if last_filled:
                        if (row,col) == (8,8):
                            print "Flag 1"
                            aa=1
                        update = True
                        break

                    # If there is a value which is an option for this cell, but is not #
                    # an option for any other cell in the row/column, enter this value #
                    empty_cells_in_row_col = Grid.Cells[row][col].get_empty_cells()                             # Once we have identified an empty cell, get list of all empty cells in it's row and column. This is a list of Cell objects
                    empty_row_col_possibilities = get_all_remaining(empty_cells_in_row_col)                     # Get the set of all possible values which can go in all of the empty cell's neighbours (in it's col and row)
                    possibilities_this_cell = Grid.range[row][col]                                              # Return set of values which can go in this cell
                    options_for_only_this_cell = possibilities_this_cell.difference(empty_row_col_possibilities)# options_for_only_this_cell is the list of possibile values for this cell, which are not an option for any of the other empty cells in the unit
                    if len(options_for_only_this_cell) == 1:
                        num = options_for_only_this_cell.pop()                                                  # Convert set to integer
                        print "Update called b, cell {},{}, val: {}".format(row, col, num)
                        if (row,col) == (8,8):
                            print "Flag 21"
                        Grid.update(row, col, num)
                        if (row,col) == (8,8):
                            print "Flag 2"
                            print "Range* (8,8):{}".format(Grid.range[8][8])
                            aa=1
                        update = True
                        break

                    # If there is a value which is an option for this cell, but is not #
                    # an option for any other empty cell in the unit, enter this value #
                    final_value = check_empty_unit_possibilities(cell[2], row, col, possibilities_this_cell, i)    # Considers values which can go in empty cells in the same unit. If a value can only go in this cell, return the value
                    if final_value:                                                                             # If final_value not None
                        print "Update called c, cell {},{}, val: {}".format(row, col, final_value)
                        Grid.update(row, col, final_value)                                                      # Update objects
                        if (row,col) == (8,8):
                            print "Flag 3"
                            aa=1
                        update = True
                        break                                                                                   # If the cell has been updated, stop searching through possible values
                                                                                                                # If the cell has been updated, stop searching through possible values
                    else:
                        pass

                    if len(Grid.range[row][col]) == 1:                                  # If there is only 1 element in cell range (after x-wing)
                        print "x-wing update {},{}".format(row,col)
                        last_possibility = Grid.range[row][col].pop()
                        Grid.update(row, col, last_possibility)               # Set the cell value to the remaining value in the range
                        if (row,col) == (8,8):
                            print "Flag 4"
                            aa=1
                else:                                               # If the cell is populated, go to the next cell
                    pass
        if not update:                                              # If you have iterated through all rows and columns, without updating, quit and raise flag
            loop_again = False
            for unit_row in range(0,3):
                
                for unit_col in range(0,3):
                    
                    iii = (Grid.range[7][8],Grid.range[8][8])
                    aaa = Grid.Units[unit_row][unit_col].get_range()
                    bbb = Grid.Units[unit_row][unit_col].get_unit_range()
                    ccc = Grid.Units[unit_row][unit_col].get_unit_range_subsets()
                    ddd = Grid.Units[unit_row][unit_col].get_preemptive_cells()
                    fff = (Grid.range[7][8],Grid.range[8][8])
                    flag = Grid.Units[unit_row][unit_col].check_num_preemptive()
                    
                    if flag == True:
                        loop_again = True
            if not loop_again:
                print "Dead end reached. No more progress possible with basic algorithm"
                Grid.value
                break
    if 0 not in Grid.full_list():
        return True
    else:
        return False
        
def fill_only_option_row(Cell):
    
    cell_range = Cell.range
    row_range_wo = get_row_range_wo(Cell.row,Cell.col,0)
    fill = None
    for val in cell_range:
        if val not in row_range_wo:
            fill = val
            break
    return fill

def fill_only_option_col(Cell):

    cell_range = Cell.range
    col_range_wo = get_col_range_wo(Cell.row,Cell.col,0)
    
    fill = None
    for val in cell_range:
        if val not in col_range_wo:
            fill = val
            break
    return fill
    

def get_row_range_wo(row,col,col_step):

    """ Return the set of values in the
    range of all cells in a row, except for
    the cells corresponding to col and col + 2"""

    list_sets = [x.range for i,x in enumerate(Grid.Cells[row][:]) if (i!=col and i!=col+col_step)]
    full_set = set().union(*list_sets)
    return full_set

def get_col_range_wo(row,col, row_step):

    """ Return the set of values in the
    range of all cells in a col, except for
    the cells corresponding to row and row + 2"""

    list_sets = [x.get_range() for i,x in enumerate(Grid.Cols[col].Cells) if (i!=row and i!=row+row_step)]
    full_set = set().union(*list_sets)
    return full_set



def x_wing(row,col,j):                                                            # The input cell is the cell at the top left of the x-wing
    #l=0
    for row_step in range(1,9-row):
        for col_step in range(1,9-col):
            #print "row: {}, col: {}, row_step: {}, col_step: {}".format(row,col,row_step,col_step)
            if row + row_step <= 8 and col + col_step <=8 and \
               (Grid.value[row][col] == 0 and \
                Grid.value[row + row_step][col] == 0 and \
                Grid.value[row][col + col_step] == 0 and \
                Grid.value[row + row_step][col + col_step] == 0):                                                    # Otherwise this function will exceed list dimensions

                in_cell_range = Grid.range[row][col]

                for val in in_cell_range:

                    this_row_range_set = get_row_range_wo(row,col,col_step)
                    parallel_row_range_set = get_row_range_wo(row + row_step,col, col_step)

                    if (val in Grid.range[row][col + col_step]) and \
                       (val not in this_row_range_set) and (val in Grid.range[row + row_step][col]) and \
                       (val in Grid.range[row + row_step][col + col_step]) and (val not in parallel_row_range_set):

                        """ If value is in the range of the cell 2 columns over AND
               the value is NOT in the range of any cell in this row, excluding thsi cell and that 2 columns over AND
               the value is in the range of the cell 2 rows below this cell AND
               the value is the range of the cell 2 diagonally right of this cell AND
               the value is NOT in the range of any of the cells in the row 2 rows below, excluding the cell corresponing to this col and that 2 to the right"""

                        print "Activate Row X-Wing row: {}, col: {}, row_step: {}, col_step: {}, val:{}".format(row,col,row_step,col_step, val)
                        row_list = set(range(0,9)).difference(set([row,row + row_step]))
                        rows =[]
                        cols = []
                        for y in row_list:
                            rows.append(y)
                            cols.append(col)
                        for y in row_list:
                            rows.append(y)
                            cols.append(col+col_step)
                        Grid.remove_from_range(rows,cols,val)
                        Grid.get_cell_ranges()


                    this_col_range_set = get_col_range_wo(row,col, row_step)
                    parallel_col_range_set = get_col_range_wo(row,col + col_step, row_step)

                    if (val in Grid.range[row + row_step][col]) and \
                       (val not in this_col_range_set) and (val in Grid.range[row][col + col_step]) and \
                       (val in Grid.range[row + row_step][col + col_step]) and (val not in parallel_col_range_set):

                        """ If value is in the range of the cell 2 rows over AND
           the value is NOT in the range of any cell in this col, excluding this cell and that 2 rows over AND
           the value is in the range of the cell 2 rows below this cell AND
           the value is in the range of the cell 2 diagonally right of this cell AND
           the value is NOT in the range of any of the cells in the col 2 cols over, excluding the cell corresponding to this row and that 2 rows down"""

                        print "Activate Col X-Wing row: {}, col: {}, row_step: {}, col_step: {}, val: {}".format(row,col,row_step,col_step, val)
                        col_list = set(range(0,9)).difference(set([col,col + col_step]))
                        rows =[]
                        cols = []
                        for z in col_list:
                            rows.append(row)
                            cols.append(z)

                        for z in col_list:
                            rows.append(row + row_step)
                            cols.append(z)
                        Grid.remove_from_range(rows,cols,val)
                        Grid.get_cell_ranges()



#################################################################
#################################################################

def check_empty_unit_possibilities(Unit, row, col, possibilities_this_cell,k):

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
                        Row = Grid.get_obj(base_row + i,base_col + j)[0]    # Get the Row object for cell which is not on same row as input cell
                        if (num not in Row.value):                          # If number is possible for this cell, stop considering this number
                            not_valid = True
                    elif base_col + j != col:                               # If not on the same column as the input cell
                        Col = Grid.get_obj(base_row + i,base_col + j)[1]    # Get the Column object for the cell which is not on same column as input cell
                        if (num not in Col.value):                          # If number is possible for this cell, stop considering this number
                            not_valid = True
                else:                                                       # Skip populated cells, and the input cell
                    pass
        if not not_valid:                                                   # If for all of the other empty cells in the unit, the not_valid flag was not raised
            final_value = num                                               # Then output the num which was considered over this loop,  and break out of loop (no need to keep searching, as a valid value has been found)
            #print "Final val {}".format(final_value)
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
        (rel_row, rel_col) = cell[2].rel_find(0)
        #print "Update last element of a unit {},{} -> {}".format(base_row+rel_row, base_col+rel_col, 45 - sum([sum(x) for x in cell[2].value]))
        if (rel_row + base_row, rel_col + base_col) == (8,8):
            print "Flag 5"
            aa=1
        Grid.update(rel_row + base_row, rel_col + base_col, \
                    45 - sum([sum(x) for x in cell[2].value]))                          # Value in num field is equal to the number missing from the unit

        return True
    elif num_zeroes_col == 1:
        abs_row = cell[1].abs_find(0)
        #print "Update last in col, cell {},{} -> {}".format(abs_row, col, 45 - sum(cell[1].value))
        if (abs_row,col) == (8,8):
            print "Flag 6"
            aa=1
        Grid.update(abs_row, col, \
                    45 - sum(cell[1].value))                          # Value in num field is equal to the number missing from the unit

        return True
    elif num_zeroes_row == 1:
        abs_col = cell[0].abs_find(0)
        #print "Update last in row, cell {},{} -> {}".format(row, abs_col, 45 - sum(cell[0].value))
        if (row,abs_col) == (8,8):
            print "Flag 7"
            aa=1
        Grid.update(row, abs_col, \
                    45 - sum(cell[0].value))                          # Value in num field is equal to the number missing from the unit

        return True
    else:
        return False


# Run this code #

solved = solve()
for row in Grid.value:
    print "{}".format(row)

if solved:
    with open("solution.txt","w") as text_file:
        text_file.write("Solution:\n")
        for row in Grid.value:
            text_file.write(str(row)+"\n")
