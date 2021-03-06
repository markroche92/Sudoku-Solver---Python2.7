from functions import remaining, get_unit_row_column, get_base
from itertools import combinations, chain
import csv

#################################################################
###### Parent class for Unit, Col, Row. Reusable methods. #######
#################################################################

class CommonAttributesMethods:

    """ This class initialises common attributes, and defines
    common methods for Unit, Row, Col, Cell classes """

    def __init__(self):

        """ Initialise common attributes for Rows,
        Columns and Units """

        self.combined_range = set()
        self.range_subsets = []
        self.preemptive_dict = {}

    def get_num_blanks(self):

        """ Get the number of blank cells
        within the unit/row/column """

        if 'Row' in self.__str__() or 'Col' in self.__str__():
            return self.value.count(0)
        else:
            return sum([row.count(0) for row in self.value])

    def get_combined_range(self):

        """ Returns the set of all remaining values
        to be filled in, in this unit/row/col """

        combine = lambda x: set().union(*x)

        if 'Unit' in self.__str__():
            range_list = [item for sublist in self.range for item in sublist]                 # Convert list of lists to list
        else:
            range_list = self.range
        self.combined_range = combine(range_list)
        return self.combined_range

    def get_combined_range_subsets(self):

        """ Returns the list of all subsets (as tuples) of 2 or
        more elements for the superset of combined_range """

        self.range_subsets = list(chain(*[combinations(list(self.combined_range), \
                             length) for length in xrange(2,10)]))
        return self.range_subsets

    def get_preemptive_cells(self):

        """ Return the dictionary of range subset tuples : Cells
        which contain the entire subset within its range """

        def conditional(row,col):

            """ Nested Function:
            Iterate through the range subsets, and create the
            preemptive dictionary. Nested function because the
            external code allows this to be called for Row, Col
            and Unit objects"""

            for subset in self.range_subsets:

                if self.Parent.Cells[row][col].range <=set(subset) and \
                   len(self.Parent.Cells[row][col].range)>1:

                    if subset in self.preemptive_dict.keys():
                        self.preemptive_dict[subset].add(self.Parent.Cells[row][col])
                    else:
                        self.preemptive_dict[subset] = set([self.Parent.Cells[row][col]])


        if 'Unit' in self.__str__():
            for row in xrange(self.row_start, self.row_end+1):
                for col in xrange(self.col_start, self.col_end):
                    conditional(row=row, col=col)

        elif 'Row' in self.__str__():
            for col in xrange(0,9):
                conditional(row=self.row, col=col)

        elif 'Col' in self.__str__():
            for row in xrange(0,9):
                conditional(row=row, col=self.col)

        else:
            return None
        return self.preemptive_dict

    def check_num_preemptive(self):

        """ Function returns true if there has been a range
        update within the Row/Col/Unit, after applying
        preemptive cell logic """

        def get_cells(self):

            """ Nested Function:
            Get the list of cells in the Unit/Row/Col
            as, depending on the object in question """

            cells = []
            if 'Unit' in self.__str__():
                for row in xrange(self.row_start, self.row_end+1):
                    for col in xrange(self.col_start, self.col_end):
                        cells.append(self.Parent.Cells[row][col])

            elif 'Row' in self.__str__():
                for col in xrange(0,9):
                    cells.append(self.Parent.Cells[self.row][col])

            elif 'Col' in self.__str__():
                for row in xrange(0,9):
                    cells.append(self.Parent.Cells[row][self.col])
            return cells

        range_update = False
        for key in self.preemptive_dict:

            if len(key) == len(self.preemptive_dict[key]):

                cells = get_cells(self)

                for cell in cells:
                    if cell not in self.preemptive_dict[key]:
                        rows,cols = [],[]
                        for val in key:
                            if cell.value == 0:
                                range_old = self.Parent.range
                                rows.append(cell.row)
                                cols.append(cell.col)
                                self.Parent.remove_from_range(rows=rows, cols=cols, val=val)
                                self.Parent.get_cell_ranges()
                                if self.Parent.range != range_old:
                                    range_update = True
        return range_update



    def get_range(self):

        """ Method to get the range of a Row,
        Col, Unit or Cell """

        if 'Unit' in self.__str__():

            """ Returns a list of 3 lists, containing
            the range of each cell in the unit """

            self.range = [[col for col in row[self.col_start:self.col_end]] for row in self.Parent.range[self.row_start:self.row_end+1]]
            return self.range

        elif 'Row' in self.__str__():

            """ Returns a list of sets containing the
            range for each cell in the row """

            self.range = [col for col in self.Parent.range[self.row][:]]
            return self.range

        elif 'Col' in self.__str__():

            """ Returns a list of sets containing the
            range for each cell in the col """

            self.range = [row[self.col] for row in self.Parent.range]
            return self.range

        elif 'Cell' in self.__str__():

            """ Function to return a set of possible values
            which could be entered in this cell, based on row,
            column, unit contents """

            self.range = self.Parent.range[self.row][self.col]
            return self.range                       # Return the set of possible values which could go in the cell

#################################################################
# Define classes which represent each aspect of the sudoku grid #
#################################################################

class Board:

    """ This class defines attributes of the sudoku board,
    and methods for updating and acquiring board info """

    def __init__(self, grid):
        # Initialise the dictionary of (row,col) locations to values to be
        # removed from the range of the cell at this location
        self.range_remove = {}

        # Initialise list of lists of sets containing the range of each cell
        # on the Board at any time
        self.range = [[0 for x in range(0,9)] for y in range(0,9)]

        self.value = grid                                                                                                     # Initialise values for Board, based on text file
        self.Cells = [[Cell(Parent=self, row=row, col=col, grid=self.value) for col in range(0,9)] for row in range(0,9)]     # Create Cells objects. Feed object of class Board to the new object, so that it's parent is accessible.
        self.Rows = [Row(Parent=self, row=row, grid=self.value) for row in range(0,9)]                                        # Create Row objects. Feed object of class Board to the new object, so that it's parent is accessible.
        self.Units = [[Unit(Parent=self, i=row, j=col, grid=self.value) for col in range(0,3)] for row in range(0,3)]         # Create Unit objects. Feed object of class Board to the new object, so that it's parent is accessible.
        self.Cols = [Col(Parent=self, col=col, grid=self.value) for col in range(0,9)]                                        # Create Col objects. Feed object of class Board to the new object, so that it's parent is accessible.

                                                                                                                              # Initialise cell ranges based on the initial contents of their row, column and unit
        for row in xrange(0,9):
            for col in xrange(0,9):
                obj = self.get_obj(row=row,col=col)
                self.Cells[row][col].range = remaining(Row=obj[0], Col=obj[1], Unit=obj[2], Cell=obj[3])                      # Initialise the range of each Cell object by checking it's row, column and unit
                self.range[row][col] = self.Cells[row][col].range                                                             # The range of each cell is not only accessible through the Cell object, but through Board.range

    def full_list(self):                                                                    # Continue to try to solve the puzzle while there is a 0 in full_list

        """ Return all elements of the grid
        as a single list """

        full_list = [x for row in self.value for x in row]
        return full_list

    def update(self, row, col, val):                                                        # Method to update the values within the puzzle

        """ Updates a single cell of the board
        with a certain value. This entails calling update
        functions for Cell, Row, Col and Unit objects"""

        (u_row,u_col) = get_unit_row_column(act_row=row, act_col=col)                       # Get unit row and unit column (each between 0 and 2)
        (rel_row, rel_col) = (row - 3*u_row, col - 3*u_col)                                 # Get the relative row and column of the cell within the unit (each between 0 and 2)
        """ Update values first """
        self.value[row][col] = val                                                          # Update Board.value
        self.Rows[row].update(col=col, val=val)                                             # Update Board.Rows
        self.Cols[col].update(row=row, val=val)                                             # Update Board.Cols
        self.Units[u_row][u_col].update(row=rel_row, col=rel_col, val=val)                  # Update Board.Units
        self.Cells[row][col].update(val=val)                                                # Update Board.Cells
        """ Now update ranges """
        self.range_remove_last_possibility(row=row,col=col,val=val)
        self.get_cell_ranges()

    def get_obj(self, row, col):                                                            # Used to get the Row, Col, Unit, Cell objects for a row and column

        """ Function to return a tuple of the (Row,
        Column, Unit, Cell) corresponding to this (row,col) """

        (u_row,u_col) = get_unit_row_column(act_row=row, act_col=col)
        return (self.Rows[row],self.Cols[col],self.Units[u_row][u_col],self.Cells[row][col])

    def get_cell_ranges(self):                                                                    # Called directly after updating a value on the Board

        """ Function to return a list of sets of possible values for
        each cell in the grid """

        # Get Board.range by calling the get_range() method for each Cell object
        self.update_cell_range()
        for row_col in self.range_remove.keys():
            self.range[row_col[0]][row_col[1]] = \
            self.range[row_col[0]][row_col[1]].difference(self.range_remove[row_col])

        self.update_cell_range()

        return self.range

    def remove_from_range(self, rows, cols, val):                                                 # Update the dictionary of tuples to sets, with the values to be removed from the range of cells

        """ Function to update list of values to be removed from
        cell ranges, based on the findings of x-wing """

        for i, r in enumerate(rows):
            c = cols[i]
            if (r,c) in self.range_remove.keys():
                self.range_remove[(r,c)].add(val)
            else:
                self.range_remove[(r,c)] = set([val])

    def update_cell_range(self):
        self.range = [[self.Cells[row][col].get_range() for \
                       col in range(0,9)] for row in range(0,9)]

    def range_remove_last_possibility(self,row,col,val):
        rows, cols = [], []
        for i in xrange(0,9):
            if i != row:
                rows.append(i)
                cols.append(col)
            if i != col:
                rows.append(row)
                cols.append(i)

        (base_row, base_col) = get_base(row=row, col=col)

        for value in self.range[row][col]:
            self.remove_from_range([row],[col],value)

        for r in xrange(base_row,base_row + 3):
            for c in xrange(base_col, base_col + 3):
                if (r,c) != (row,col):
                    rows.append(r)
                    cols.append(c)
                    self.remove_from_range(rows,cols,val)

    def is_valid(self):

        """ Function will return True if the sudoku grid is
        still valid (i.e. rules of the puzzle have not been
        broken) """

        is_valid = True                                         # Assume grid is valid, but lower flag if it is found to be invalid.

        for val in xrange(1,10):
            for (Row,Col) in zip(self.Rows,self.Cols):

                if Row.value.count(val) > 1 or sum(Row.value) > 45 or \
                    Col.value.count(val) > 1 or sum(Col.value) > 45:
                    is_valid = False
                    break                                       # Break row/col loop

            if not is_valid:
                break                                           # Break Value loop if is_valid became false in row,col iteration

            for u_row in xrange(0,3):
                for u_col in xrange(0,3):
                    val_list = [x for r in self.Units[u_row][u_col].value for x in r]
                    if val_list.count(val) > 1 or sum(val_list) > 45:
                        is_valid = False
                        break                                   # Break col loop
                if not is_valid:
                    break                                       # Break row loop
            if not is_valid:
                break                                           # Break Value loop if is_valid became false in unit iteration
        return is_valid





    def is_complete(self):

        """ Function will return True if the sudoku grid's units, rows
        and columns all sum to 45, there are no zeros, and 1, 2, 3, 4, 5,
        6, 7, 8, 9 all occur in each Row, Cell, Unit """

        for row in xrange(0,9):
            for col in xrange(0,9):
                (u_row, u_col) = get_unit_row_column(row, col)
                val_list = [x for r in self.Units[u_row][u_col].value for x in r]
                vals = set(xrange(0,10))
                if (sum(self.Rows[row].value) != 45 or sum(self.Cols[col].value) != 45 or \
                 sum(val_list) != 45 or 0 in self.full_list() or len(set(self.Rows[row].value).difference(vals)) > 0 or \
                 len(set(self.Cols[col].value).difference(vals)) > 0 or len(set(val_list).difference(vals)) > 0):
                    break                                       # Break col loop if condition is met
            else:
                continue                                        # If col loop ended naturally, continue to loop, or end naturally
            break                                               # If we broke from col loop, break from row loop
        else:
            return True                                         # If row loop ended naturally, is_complete = True
        return False                                            # If row loop was broken, is_complete = False




#################################################################
#################################################################

class Unit(CommonAttributesMethods):

    """ This class defines attributes of a unit on the board,
    and methods for updating and acquiring unit info """

    def __init__(self, Parent, i, j, grid):                     # i is the row of the unit (1,2 or 3), j if the column of the unit (1,2 or 3)

        # Start and end rows, columns of the unit
        self.unit_row, self.unit_col = i, j
        self.row_start, self.col_start = 3*i, 3*j
        self.row_end, self.col_end = 3*i + 2, 3*j + 3

        # Extract the unit data as a list of lists
        self.value = [grid[self.row_start][self.col_start:self.col_end], \
                       grid[self.row_start+1][self.col_start:self.col_end], \
                       grid[self.row_end][self.col_start:self.col_end]]
        self.range =[]
        self.Parent = Parent

        CommonAttributesMethods.__init__(self)

    def __str__(self):

        """ Return the name of the object
        when called as a string """

        return "Unit {},{}".format(self.unit_row,self.unit_col)

    def update(self, row, col, val):

        """ Change an element of the unit
        to a certain value """

        self.value[row][col] = val

    def full_list(self):

        """ Get the full set of values present
        in a unit """

        full_list = {num for row in self.value for num in row}
        return full_list

    def rel_find(self, val):

        """ Find the first occurance of a
        certain value in the unit. Note,
        the output row and column are
        relative to the start of the unit"""

        for i, row in enumerate(self.value):
            for j, col in enumerate(row):
                if col == val:
                    row_star, col_star = i, j
                    break                           # Break inner loop, without going to else, if col = val
            else:                                   # If val was not found during inner loop, continue in code
                continue
            break                                   # If we broke from inner loop, break from outer loop
        else:                                       # If outer loop concluded without finding val, return None
            return None
        return (row_star, col_star)                 # If we broke from loops, return rel_row and rel_col in a tuple

#################################################################
#################################################################

class Row(CommonAttributesMethods):

    """ This class defines attributes of a row on the board,
    and methods for updating and acquiring row info """

    def __init__(self, Parent, row, grid):
        self.value = grid[row]                       # Simply extract the row from the grid. This is a single list
        self.row = row
        self.range = []
        self.Parent = Parent
        CommonAttributesMethods.__init__(self)

    def __str__(self):

        """ Return the name of the object
        when called as a string """

        return "Row {}".format(self.row)

    def update(self, col, val):

        """ Change an element of the row
        to a certain value """

        self.value[col] = val                        # Update the element with the value "val"

    def abs_find(self, val):

        """ Find the first occurance of a
        certain value in the row. Note,
        the output column value is absolute """

        for i,col in enumerate(self.value):
            if col == val:
                break
        else:                                       # Note, else clause is on for. This specifies what is returned when val is not found.
            return None
        return i

#################################################################
#################################################################

class Col(CommonAttributesMethods):

    """ This class defines attributes of a column on the board,
    and methods for updating and acquiring column info """

    def __init__(self, Parent, col, grid):
        self.value, self.Cells, self.range = [], [], []
        self.col = col
        for row in xrange(0,9):
            self.value.append(grid[row][col])        # Column is a list
        self.Parent = Parent

        CommonAttributesMethods.__init__(self)

    def __str__(self):

        """ Return the name of the object
        when called as a string """

        return "Column {}".format(self.col)

    def get_cells(self):

        """ Get the list of cells in the
        column """

        self.Cells = [self.Parent.Cells[x][self.col] for x in xrange(0,9)]

    def update(self, row, val):

        """ Change an element of the column
        to a certain value """

        self.value[row] =val                         # Update the element with the value "val"

    def abs_find(self, val):

        """ Find the first occurance of a
        certain value in the column. Note,
        the output row value is absolute """

        for i,row in enumerate(self.value):
            if row == val:
                break
        else:                                        # Note, else clause is on for. This specifies what is returned when val is not found.
            return None
        return i

#################################################################
#################################################################

class Cell(CommonAttributesMethods):

    """ This class defines attributes of a cell on the board,
    and methods for updating and acquiring cell info """

    def __init__(self, Parent, row, col, grid):
        self.value = grid[row][col]
        self.row, self.col = row, col
        self.Parent = Parent

    def __str__(self):

        """ Return the name of the object
        when called as a string """

        return "Cell {},{}".format(self.row,self.col)

    def update(self, val):

        """ Function to update the value of a cell
        with a particular value """

        self.value = val

#################################################################
#################################################################
