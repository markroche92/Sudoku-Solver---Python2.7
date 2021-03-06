from functions import remaining, get_base
from get_ranges import get_row_range_wo, get_col_range_wo
from classes import Board
from functools import partial
import copy
import os
import csv
import time
#################################################################
#################################################################


def solve():

    """ Run a loop to fill in cell values
    which cannot be entered in neighbours"""
    i=0
    r=0
    while 0 in Grid_List[-1].full_list():                                                                       # While there are still empty grid cells
        update = False
        #print "{}".format(len(Grid_List))
        if not Grid_List[-1].is_valid() and len(Grid_List) > 1:

            del Grid_List[-1]
            if (record_random[-1][0],record_random[-1][1]) in Grid_List[-1].range_remove:
                Grid_List[-1].range_remove[(record_random[-1][0],record_random[-1][1])].add(record_random[-1][2])
            else:
                Grid_List[-1].range_remove[(record_random[-1][0],record_random[-1][1])] = set([record_random[-1][2]])

            Grid_List[-1].get_cell_ranges()

        else:

            for row in xrange(0,9):                                                                                  # Search each row (0 -> 8), zero based
                for col in xrange(0,9):                                                                              # Search each column in each row (0 -> 8), zero based

                    if Grid_List[-1].value[row][col] == 0:                                                          # If this cell is empty
                        i+=1
                        cell = Grid_List[-1].get_obj(row=row, col=col)                                                      # Get the (Row, Col, Unit, Cell) objects for the (row, col)

                        if try_fill_last_blank(cell=cell):

                            """ Solver Algorithm #1:
                            Check if there is a single blank cell remaining in
                            the row, column or unit. If so, fill this cell with the
                            appropriate value """

                            update = True
                            break

                        fill = check_if_only_in_range_this_cell(cell=cell)                                               # Considers values which can go in empty cells in the same unit. If a value can only go in this cell, return the value

                        if fill:                                                                                    # If fill not None

                            """ Solver Algorithm #2:
                            Check if there is a value in the range of the current cell,
                            which is not in the range of another cell in the row, col, or unit.
                            If so, update the cell with this value """

                            Grid_List[-1].update(row=row, col=col, val=fill)                                                    # Update objects
                            update = True
                            break


                        old_range = Grid_List[-1].range
                        x_wing(Cell=cell[3])
                        if old_range != Grid_List[-1].range:

                            """ Solver Algorithm #3:
                            Run x-wing for rows and x-wing for columns, using the current cell as
                            the base cell. If there is an update to the range of the grid, we
                            say that update = True """

                            update = True
                            break


                        if len(Grid_List[-1].range[row][col]) == 1:                                                 # If there is only 1 element in cell range (after x-wing)

                            """ Solver Algorithm #4:
                            If there is only 1 value remaining in the range of a cell,
                            fill the cell with this value  """

                            one_left_in_range(row=row, col=col)
                            update = True
                            break
                    else:                                                                                           # If the cell is populated, go to the next cell
                        pass
                if update:
                    break




            if not update:                                                                                          # If you have iterated through all rows and columns, without updating, consider preemptive sets

                """ Solver Algorithm #5:
                If no updates have occured, after considering all empty cells,
                apply premptive set logic to units, rows, columns of the
                grid. If cell ranges are updated, re-run the loop  """

                loop_again = preemptive_sets() # Returns True only if the range hs changed based on applying preemptive sets

                if not loop_again:

                    record_random.append(random_choice())
                    r+=1
                else:
                    pass

    if 0 not in Grid_List[-1].full_list():
        return (True, Grid_List, r)
    else:
        return (False, None, r)

""" Solver Algorithms: """

def try_fill_last_blank(cell):

    """ Solver Algorithm #1:
    Check if a value in the range of the current cell is
    not in the combined range of the other cells in it's row,
    or in the combined range of the other cells in it's col,
    or in the combined range of the other cells in it's unit """

    row, col = cell[0].row, cell[1].col

    (base_row, base_col) = get_base(row=row, col=col)
    (num_zeroes_row, num_zeroes_col, num_zeroes_unit) = \
          tuple(x.get_num_blanks() for x in [cell[0],cell[1],cell[2]])


    if num_zeroes_unit == 1:                                                            # If only one empty cell in this unit, just fill in the value
        (rel_row, rel_col) = cell[2].rel_find(0)
        val = 45 - sum([sum(x) for x in cell[2].value])
        Grid_List[-1].update(row= rel_row + base_row, col=rel_col + base_col, val=val)               # Value in num field is equal to the number missing from the unit
    elif num_zeroes_col == 1:
        abs_row = cell[1].abs_find(0)
        val =  45 - sum(cell[1].value)
        Grid_List[-1].update(row=abs_row, col=col, val=val)                                         # Value in num field is equal to the number missing from the unit
    elif num_zeroes_row == 1:
        abs_col = cell[0].abs_find(0)
        val = 45 - sum(cell[0].value)
        Grid_List[-1].update(row=row, col=abs_col, val=45 - sum(cell[0].value))                     # Value in num field is equal to the number missing from the unit
    else:
        return False

    return True

def check_if_only_in_range_this_cell(cell):

    """ Solver Algorithm #2:
    Check if a value in the range of the current cell is
    not in the combined range of the other cells in it's row,
    or in the combined range of the other cells in it's col,
    or in the combined range of the other cells in it's unit """

    def fill_only_option_row_col(Cell, choice):

        """ Nested function #1:
        Check if there is a value in the range of the
        input cell which is not in the range of any other
        cell in the same row/col """

        cell_range = Cell.range

        if choice == 'row':
            """ If row is choice, get the row range without this cell """
            range_wo = get_row_range_wo(Cell=Cell, row=Cell.row, col=Cell.col)
        elif choice == 'col':
            """ If col is choice, get the col range without this cell """
            range_wo = get_col_range_wo(Cell=Cell, row=Cell.row, col=Cell.col)
        else:
            return None                                                                 # If neither row nor col is the choice, return None

        for val in cell_range:
            if val not in range_wo:
                fill = val
                break
        else:                                                                           # Note, this is an else case on for -> return None if loop runs unbroken
            return None
        return fill

    def fill_only_option_unit(Unit, Cell):

        """Nested Function #2:
        Check the other empty cells in the unit. If an element of the range of the input cell
        is not an option for any of the other empty cells in this unit, return this cell value """

        row, col = Cell.row, Cell.col

        possibilities_this_cell = iter(Grid_List[-1].range[row][col])

        (base_row, base_col) = get_base(row=row, col=col)                                               # Get the base column and row for the row and column of the cell being considered
        fill = None                                                                             # Initialise the final_value to None
        for num in possibilities_this_cell:                                                     # Search all cells in unit, for if they can take each possibility for input cell
            not_valid = False                                                                   # Every possible number if initially considered valid
            for i in xrange(0,3):                                                               # Iterate from 0 -> 2 (all rows in a unit)
                for j in xrange(0,3):                                                           # Iterate from 0 -> 2 (all columns in a unit)
                    if Unit.value[i][j] == 0 and (base_row + i,base_col + j) != \
                     (row, col) and not not_valid:
                                                                                                # If (i,j) is the position of an empty cell, but not the position of the input empty cell, and not_valid flag has not been raised
                        if (base_row + i != row) and (base_col + j != col):                     # If neither on same row nor column as the input cell
                            (Row, Col) = Grid_List[-1].get_obj(row=base_row + i, col=base_col + j)[0:2]  # Get the Row and Column object for cell which is neither on same column or row as the input cell
                            if (num not in Row.value) and (num not in Col.value):               # If number is possible for this cell, stop considering this number
                                not_valid = True
                        elif base_row + i != row:                                               # If not on the same column as the input cell
                            Row = Grid_List[-1].get_obj(row=base_row + i, col=base_col + j)[0]           # Get the Row object for cell which is not on same row as input cell
                            if (num not in Row.value):                                          # If number is possible for this cell, stop considering this number
                                not_valid = True
                        elif base_col + j != col:                                               # If not on the same column as the input cell
                            Col = Grid_List[-1].get_obj(row=base_row + i, col=base_col + j)[1]           # Get the Column object for the cell which is not on same column as input cell
                            if (num not in Col.value):                                          # If number is possible for this cell, stop considering this number
                                not_valid = True
                    else:                                                                       # Skip populated cells, and the input cell
                        pass
            if not not_valid:                                                                   # If for all of the other empty cells in the unit, the not_valid flag was not raised
                fill = num                                                                      # Then output the num which was considered over this loop,  and break out of loop (no need to keep searching, as a valid value has been found)
                break
        return fill

    Unit, Cell = cell[2], cell[3]
    fill = fill_only_option_row_col(Cell=Cell, choice = 'row')
    if not fill:
        fill = fill_only_option_row_col(Cell=Cell, choice = 'col')
        if not fill:
            fill = fill_only_option_unit(Unit=Unit, Cell=Cell)
    return fill

def x_wing(Cell):

    """ Solver Algorithm #3:
    Run row-based x-wing algorithm and col-based x-wing algorithm
    for the input cell, and for a row gap and col gap ranging from 1 to
    the limit of the bottom and right hand side of the sudoku grid """                                                                                      # The input cell is the cell at the top left of the x-wing

    def x_wing_row(Cell,row_step,col_step,val):

            """ Nested function #1:
            X-Wing for rows """

            row, col = Cell.row, Cell.col

            func_r = lambda x: get_row_range_wo(Cell=Cell, row=x, col=col, col_step=col_step)
            (this_row_range_set, parallel_row_range_set) = tuple(map(func_r, [row, row+row_step]))

            if (val in Grid_List[-1].range[row][col + col_step]) and \
               (val not in this_row_range_set) and (val in Grid_List[-1].range[row + row_step][col]) and \
               (val in Grid_List[-1].range[row + row_step][col + col_step]) and (val not in parallel_row_range_set):

                """ If value is in the range of the cell 2 columns over AND
                the value is NOT in the range of any cell in this row, excluding thsi cell and that 2 columns over AND
                the value is in the range of the cell 2 rows below this cell AND
                the value is the range of the cell 2 diagonally right of this cell AND
                the value is NOT in the range of any of the cells in the row 2 rows below, excluding the cell corresponing to this col and that 2 to the right"""

                row_list = set(xrange(0,9)).difference(set([row,row + row_step]))
                rows, cols = [], []
                for y in row_list:
                    rows.extend([y,y])
                    cols.extend([col,col+col_step])
                Grid_List[-1].remove_from_range(rows=rows, cols=cols, val=val)
                Grid_List[-1].get_cell_ranges()

    def x_wing_col(Cell,row_step,col_step,val):

            """ Nested function #1:
            X-Wing for cols """

            row,col = Cell.row, Cell.col

            func_c = lambda x: get_col_range_wo(Cell=Cell, row=x, col=col, row_step=row_step)
            (this_col_range_set, parallel_col_range_set) = tuple(map(func_c, [col, col+col_step]))

            if (val in Grid_List[-1].range[row + row_step][col]) and \
               (val not in this_col_range_set) and (val in Grid_List[-1].range[row][col + col_step]) and \
               (val in Grid_List[-1].range[row + row_step][col + col_step]) and (val not in parallel_col_range_set):

                """ If value is in the range of the cell 2 rows over AND
                the value is NOT in the range of any cell in this col, excluding this cell and that 2 rows over AND
                the value is in the range of the cell 2 rows below this cell AND
                the value is in the range of the cell 2 diagonally right of this cell AND
                the value is NOT in the range of any of the cells in the col 2 cols over, excluding the cell corresponding to this row and that 2 rows down"""

                col_list = set(range(0,9)).difference(set([col,col + col_step]))
                rows, cols = [],[]
                for z in col_list:
                    rows.extend([row,row + row_step])
                    cols.extend([z,z])

                Grid_List[-1].remove_from_range(rows=rows, cols=cols, val=val)
                Grid_List[-1].get_cell_ranges()

    (row, col) = (Cell.row, Cell.col)

    for row_step in xrange(1,9-row):                                                                         # row_step is the row width of the x-wing. It will not exceed grid bottom
        for col_step in xrange(1,9-col):                                                                     # col_step is the col width of the x-wing. It will not exceed grid width
            if row + row_step <= 8 and col + col_step <=8 and \
               (Grid_List[-1].value[row][col] == 0 and \
                Grid_List[-1].value[row + row_step][col] == 0 and \
                Grid_List[-1].value[row][col + col_step] == 0 and \
                Grid_List[-1].value[row + row_step][col + col_step] == 0):

                # If inside the grid row dimensions
                # If inside the grid col dimensions
                # If the value of the considered cell is zero (input cell)
                # If the value of the cell in the considered row, but common column, is zero
                # If the value of the cell in the common row, and considered column, is zero
                # If the value of the cell in the comsidered row and considered column, is zero

                in_cell_range = Grid_List[-1].range[row][col]                                                        # Get the range of the input cell

                for val in in_cell_range:                                                                   # For each vaue in the range of the input cel
                    x_wing_row(Cell=Cell, row_step=row_step, col_step=col_step, val=val)                                               # Run x_wing on rows
                    x_wing_col(Cell=Cell, row_step=row_step, col_step=col_step, val=val)                                               # Run x-wing on columns

def one_left_in_range(row,col):
    """ Solver Algorithm #4:
    If there is only one value remaining in the range of
    the input cell, fill it with this value """

    last_possibility = Grid_List[-1].range[row][col].pop()
    Grid_List[-1].update(row=row, col=col, val=last_possibility)

def preemptive_sets():

    """ Solver Algorithm #5:
    Eliminate values from the ranges of cells by applying
    preemptive set logic to each row, column and unit
    in the grid """

    def preemptive_logic(method):

        """ Nested Function #1:
        Preemptive Sets """

        loop_again = False

        if method == 'Units':
            for unit_row in xrange(0,3):
                for unit_col in xrange(0,3):

                    Grid_List[-1].Units[unit_row][unit_col].get_range()
                    Grid_List[-1].Units[unit_row][unit_col].get_combined_range()
                    Grid_List[-1].Units[unit_row][unit_col].get_combined_range_subsets()
                    Grid_List[-1].Units[unit_row][unit_col].get_preemptive_cells()
                    if Grid_List[-1].Units[unit_row][unit_col].check_num_preemptive():
                        loop_again = True
                        break
                if loop_again:
                    break
        else:
            if method == 'Rows':
                obj = Grid_List[-1].Rows
            elif method == 'Cols':
                obj = Grid_List[-1].Cols
            for element in xrange(0,9):

                obj[element].get_range()
                obj[element].get_combined_range()
                obj[element].get_combined_range_subsets()
                obj[element].get_preemptive_cells()
                if obj[element].check_num_preemptive():
                    loop_again = True
                    break
        return loop_again

    if not preemptive_logic('Units'):

        if not preemptive_logic('Rows'):

            if not preemptive_logic('Cols'):

                loop_again = False
            else:
                loop_again = True
        else:
            loop_again = True
    else:
        loop_again = True

    return loop_again

def random_choice():

    """ Solver Algorithm #6:
    If preemtive sets cannot further reduce the range of
    cells within the grid, randomly enter a value from the
    range of a cell with the smallest range in the grid  """

    def find_row_col_val():

        """ Function to iterate through the rows and columns of
        the range of the latest Grid object. Identify the cell in
        which to perform random choice. Output the row, col and
        randomly chosen value """

        sizes = set()
        for row in Grid_List[-1].range:
            for element in row:
                sizes.add(len(element))
        min_size = min(sizes.difference(set([0])))

        col_rand , row_rand  = None, None
        for i, row in enumerate(Grid_List[-1].range):
            for j, element in enumerate(row):
                if len(element) == min_size:
                    row_rand,col_rand = i,j
                    break
            if col_rand:
                break

        for element in Grid_List[-1].range[row_rand][col_rand]:
            random_choice = element
            break
        return (row_rand, col_rand, random_choice)

    def create_next_grid(row_rand, col_rand, val):

        """ Function to add a new Board object to the list Grid_List,
        and update the new Board with the random choice value """

        Grid_List.append(Board(grid = copy.deepcopy(Grid_List[-1].value)))

        for col in xrange(0,9):
            Grid_List[-1].Cols[col].get_cells()

        Grid_List[-1].get_cell_ranges()

        Grid_List[-1].update(row=row_rand, col=col_rand, val=val)

    (row,col,val) = find_row_col_val()
    create_next_grid(row_rand=row, col_rand=col, val=val)
    return (row,col,val)



test_dir = os.path.join('D:\\','GitHub','Sudoku-Solver','Tests')
code_dir = os.path.join('D:\\','GitHub','Sudoku-Solver')
os.chdir(test_dir)
test_inputs = iter((filename,filename.split('incomplete')[1]) for filename in os.listdir(os.curdir) if 'incomplete' in filename)
counter = 0
time_base = time.time()
for filename in test_inputs:
    with open(filename[0]) as f:
        counter += 1
        reader = csv.reader(f, delimiter = ' ')
        grid_init = [list(map(int,num)) for num in reader]
        Grid_List = []
        Grid = Board(grid = grid_init)

        for col in xrange(0,9):
            Grid.Cols[col].get_cells()
        Grid.get_cell_ranges()
        record_random = []
        Grid_List = [Grid]

        os.chdir(code_dir)
        solved = solve()
        if solved[1][-1].is_valid() and solved[1][-1].is_complete():
           print "Test {} PASSED. Time taken so far: {}. {} random inserts. Final random insert depth: {}".format(counter, time.time() - time_base, solved[2], len(solved[1])-1)
        else:
           print "Test {} FAILED. Time taken so far: {). {} random inserts. Final random insert depth: {}.".format(counter, time.time() - time_base, solved[2], len(solved[1])-1)
        if solved[0]:
            os.chdir(test_dir)
            with open("".join(["solution",filename[1]]),"w") as text_file:
                for row in solved[1][-1].value:
                    for i,element in enumerate(row):
                        text_file.write(str(element))
                        if i == len(row)-1:
                            text_file.write("\n")
                        else:
                            text_file.write(" ")
