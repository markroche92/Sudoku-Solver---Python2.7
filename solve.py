from functions import remaining, get_base
from get_ranges import get_row_range_wo, get_col_range_wo

from classes import Grid                                                                                        # Import Grid object

#################################################################
#################################################################

def solve():

    """ Run a loop to fill in cell values
    which cannot be entered in neighbours"""
    i=0
    while 0 in Grid.full_list():                                                                                # While there are still empty grid cells
        update = False                                                                                          # Initialise update to False
        for row in range(0,9):                                                                                  # Search each row (0 -> 8), zero based
            for col in range(0,9):                                                                              # Search each column in each row (0 -> 8), zero based

                if Grid.value[row][col] == 0:                                                                   # If this cell is empty
                    i+=1
                    print "{}".format(i)
                    cell = Grid.get_obj(row, col)                                                               # Get the (Row, Col, Unit, Cell) objects for the (row, col)

                    if try_fill_last_blank(cell):

                        """ Solver Algorithm #1:
                        Check if there is a single blank cell remaining in
                        the row, column or unit. If so, fill this cell with the
                        appropriate value """

                        update = True
                        break

                    fill = check_if_only_in_range_this_cell(cell)                                # Considers values which can go in empty cells in the same unit. If a value can only go in this cell, return the value
                    if fill:                                                                                    # If fill not None

                        """ Solver Algorithm #2:
                        Check if there is a value in the range of the current cell,
                        which is not in the range of another cell in the row, col, or unit.
                        If so, update the cell with this value """

                        Grid.update(row, col, fill)                                                             # Update objects
                        update = True
                        break


                    old_range = Grid.range
                    x_wing(row,col)
                    if old_range != Grid.range:

                        """ Solver Algorithm #3:
                        Run x-wing for rows and x-wing for columns, using the current cell as
                        the base cell. If there is an update to the range of the grid, we
                        say that update = True """

                        update = True
                        break


                    if len(Grid.range[row][col]) == 1:                                                          # If there is only 1 element in cell range (after x-wing)

                        """ Solver Algorithm #4:
                        If there is only 1 value remaining in the range of a cell,
                        fill the cell with this value  """

                        one_left_in_range(row,col)
                        update = True
                        break

                else:                                                                                           # If the cell is populated, go to the next cell
                    pass

        if not update:                                                                                          # If you have iterated through all rows and columns, without updating, consider preemptive sets

            """ Solver Algorithm #5:
            If no updates have occured, after considering all empty cells,
            apply premptive set logic to units, rows, columns of the
            grid. If cell ranges are updated, re-run the loop  """

            loop_again = preemptive_sets()

            if not loop_again:
                print "Dead end reached. No more progress possible with basic algorithm"
                Grid.value
                break
    if 0 not in Grid.full_list():
        return True
    else:
        return False

""" Solver Algorithms: """

def try_fill_last_blank(cell):

    """ Solver Algorithm #1:
    Check if a value in the range of the current cell is
    not in the combined range of the other cells in it's row,
    or in the combined range of the other cells in it's col,
    or in the combined range of the other cells in it's unit """

    row = cell[0].row
    col = cell[1].col

    (base_row, base_col) = get_base(row, col)
    num_zeroes_unit = cell[2].get_num_blanks()                                          # Get the number of empty cells in the unit of this cell
    num_zeroes_col = cell[1].get_num_blanks()                                           # Get the number of empty cells in the column of this cell
    num_zeroes_row = cell[0].get_num_blanks()                                           # Get the number of empty cells in the row of this cell

    if num_zeroes_unit == 1:                                                            # If only one empty cell in this unit, just fill in the value
        (rel_row, rel_col) = cell[2].rel_find(0)
        #print "Update last element of a unit {},{} -> {}".format(base_row+rel_row, base_col+rel_col, 45 - sum([sum(x) for x in cell[2].value]))
        Grid.update(rel_row + base_row, rel_col + base_col, \
                    45 - sum([sum(x) for x in cell[2].value]))                          # Value in num field is equal to the number missing from the unit

        return True
    elif num_zeroes_col == 1:
        abs_row = cell[1].abs_find(0)
        #print "Update last in col, cell {},{} -> {}".format(abs_row, col, 45 - sum(cell[1].value))
        Grid.update(abs_row, col, \
                    45 - sum(cell[1].value))                          # Value in num field is equal to the number missing from the unit

        return True
    elif num_zeroes_row == 1:
        abs_col = cell[0].abs_find(0)
        #print "Update last in row, cell {},{} -> {}".format(row, abs_col, 45 - sum(cell[0].value))
        Grid.update(row, abs_col, \
                    45 - sum(cell[0].value))                          # Value in num field is equal to the number missing from the unit

        return True
    else:
        return False

def check_if_only_in_range_this_cell(cell):

    """ Solver Algorithm #2:
    Check if a value in the range of the current cell is
    not in the combined range of the other cells in it's row,
    or in the combined range of the other cells in it's col,
    or in the combined range of the other cells in it's unit """

    def fill_only_option_row(Cell):

        """ Nested function #1:
        Check if there is a value in the range of the
        input cell which is not in the range of any other
        cell in the same row """

        cell_range = Cell.range
        row_range_wo = get_row_range_wo(Cell.row,Cell.col)
        fill = None
        for val in cell_range:
            if val not in row_range_wo:
                fill = val
                break
        return fill

    def fill_only_option_col(Cell):

        """ Nested Function #2:
        Check if there is a value in the range of the
        input cell which is not in the range of any other
        cell in the same column """

        cell_range = Cell.range
        col_range_wo = get_col_range_wo(Cell.row,Cell.col)

        fill = None
        for val in cell_range:
            if val not in col_range_wo:
                fill = val
                break
        return fill

    def fill_only_option_unit(Unit, Cell):

        """Nested Function #3:
        Check the other empty cells in the unit. If an element of the range of the input cell
        is not an option for any of the other empty cells in this unit, return this cell value """

        row = Cell.row
        col = Cell.col
        possibilities_this_cell = Grid.range[row][col]

        (base_row, base_col) = get_base(row, col)                               # Get the base column and row for the row and column of the cell being considered
        fill = None                                                             # Initialise the final_value to None
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
                fill = num                                                      # Then output the num which was considered over this loop,  and break out of loop (no need to keep searching, as a valid value has been found)
                break
        return fill

    Unit = cell[2]
    Cell = cell[3]
    fill = fill_only_option_row(Cell)
    if not fill:
        fill = fill_only_option_col(Cell)
        if not fill:
            fill = fill_only_option_unit(Unit, Cell)
    return fill

def x_wing(row,col):

    """ Solver Algorithm #3:
    Run row-based x-wing algorithm and col-based x-wing algorithm
    for the input cell, and for a row gap and col gap ranging from 1 to
    the limit of the bottom and right hand side of the sudoku grid """                                                                                      # The input cell is the cell at the top left of the x-wing

    def x_wing_row(row,col,row_step,col_step,val):

            """ Nested function #1:
            X-Wing for rows """

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

    def x_wing_col(row,col,row_step,col_step,val):

            """ Nested function #1:
            X-Wing for cols """

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

    for row_step in range(1,9-row):                                                                         # row_step is the row width of the x-wing. It will not exceed grid bottom
        for col_step in range(1,9-col):                                                                     # col_step is the col width of the x-wing. It will not exceed grid width
            #print "row: {}, col: {}, row_step: {}, col_step: {}".format(row,col,row_step,col_step)
            if row + row_step <= 8 and col + col_step <=8 and \
               (Grid.value[row][col] == 0 and \
                Grid.value[row + row_step][col] == 0 and \
                Grid.value[row][col + col_step] == 0 and \
                Grid.value[row + row_step][col + col_step] == 0):

                # If inside the grid row dimensions
                # If inside the grid col dimensions
                # If the value of the considered cell is zero (input cell)
                # If the value of the cell in the considered row, but common column, is zero
                # If the value of the cell in the common row, and considered column, is zero
                # If the value of the cell in the comsidered row and considered column, is zero

                in_cell_range = Grid.range[row][col]                                                        # Get the range of the input cell

                for val in in_cell_range:                                                                   # For each vaue in the range of the input cel
                    x_wing_row(row,col,row_step,col_step,val)                                               # Run x_wing on rows
                    x_wing_col(row,col,row_step,col_step,val)                                               # Run x-wing on columns

def one_left_in_range(row,col):
    """ Solver Algorithm #4:
    If there is only one value remaining in the range of
    the input cell, fill it with this value """

    last_possibility = Grid.range[row][col].pop()
    Grid.update(row, col, last_possibility)

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
            print "Preemptive Units"
            for unit_row in range(0,3):
                for unit_col in range(0,3):

                    Grid.Units[unit_row][unit_col].get_range()
                    print "Called Unit get_range"
                    Grid.Units[unit_row][unit_col].get_combined_range()
                    print "Called Unit get_combined_range"
                    Grid.Units[unit_row][unit_col].get_combined_range_subsets()
                    print "Called Unit get_combined_range_subsets"
                    Grid.Units[unit_row][unit_col].get_preemptive_cells()
                    print "Called Unit get_preemptive_cells"
                    if Grid.Units[unit_row][unit_col].check_num_preemptive():
                        print "Called Unit check_num_preemptive"
                        loop_again = True
                        break
                if loop_again:
                    break
        else:
            if method == 'Rows':
                obj = Grid.Rows
                print "Preemptive Rows"
            elif method == 'Cols':
                obj = Grid.Cols
                print "Preemptive Cols"
            for element in range(0,9):

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
