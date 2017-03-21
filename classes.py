from functions import remaining, get_unit_row_column
from itertools import combinations, chain

import csv
# Load the initial grid from a text file

with open('incomplete.txt') as f:                                                           # Open the incomplete sudoku puzzle
    reader = csv.reader(f, delimiter = ' ')                                                 # Read file
    grid = [list(map(int,num)) for num in reader]                                           # Import data as a list of lists of integers


#################################################################

# Define classes which represent each aspect of the sudoku grid #

#################################################################

class Board:

    def __init__(self, grid = grid):
        # Initialise the dictionary of (row,col) locations to values to be
        # removed from the range of the cell at this location
        self.range_remove = {}

        # Initialise list of lists of sets containing the range of each cell
        # on the Board at any time
        self.range = [[0 for x in range(0,9)] for y in range(0,9)]

        self.value = grid                                                                   # Initialise values for Board, based on text file
        self.Cells = [[Cell(row, col) for col in range(0,9)] for row in range(0,9)]         # Create Cells objects
        self.Rows = [Row(col) for col in range(0,9)]                                        # Create Row objects
        self.Units = [[Unit(row, col) for col in range(0,3)] for row in range(0,3)]         # Create Unit objects
        self.Cols = [Col(row) for row in range(0,9)]                                        # Create Col objects

        # Initialise cell ranges based on the initial contents of their row, column and unit
        for row in range(0,9):
            for col in range(0,9):
                obj = self.get_obj(row,col)
                self.Cells[row][col].range = remaining(obj[0], obj[1], obj[2], obj[3])      # Initialise the range of each Cell object by checking it's row, column and unit
                self.range[row][col] = self.Cells[row][col].range                           # The range of each cell is not only accessible through the Cell object, but through Board.range



    def full_list(self):                                                                    # Continue to try to solve the puzzle while there is a 0 in full_list

        """ Return all elements of the grid
        as a single list """

        full_list = []
        for row in self.value:
            full_list.extend(row)
        return full_list

    def update(self, row, col, val):                                                        # Method to update the values within the puzzle

        """ Updates a single cell of the board
        with a certain value. This entails calling update
        functions for Cell, Row, Col and Unit objects"""

        (u_row,u_col) = get_unit_row_column(row,col)                                        # Get unit row and unit column (each between 0 and 2)
        (rel_row, rel_col) = (row - 3*u_row, col - 3*u_col)                                 # Get the relative row and column of the cell within the unit (each between 0 and 2)
        """ Update values first """
        self.value[row][col] = val                                                          # Update Board.value
        self.Rows[row].update(col, val)                                                     # Update Board.Rows
        self.Cols[col].update(row, val)                                                     # Update Board.Cols
        self.Units[u_row][u_col].update(rel_row, rel_col, val)                              # Update Board.Units
        self.Cells[row][col].update(val)                                                    # Update Board.Cells
        """ Now update ranges """
        self.range_remove_last_possibility(row,col,val)
        self.get_cell_ranges()

    def get_obj(self, row, col):                                                            # Used to get the Row, Col, Unit, Cell objects for a row and column

        """ Function to return a tuple of the (Row,
        Column, Unit, Cell) corresponding to this (row,col) """

        (u_row,u_col) = get_unit_row_column(row, col)
        return (self.Rows[row],self.Cols[col],self.Units[u_row][u_col],self.Cells[row][col])

    def get_cell_ranges(self):                                                              # Called directly after updating a value on the Board

        """ Function to return a list of sets of possible values for
        each cell in the grid """

        # Get Board.range by calling the get_range() method for each Cell object
        self.update_cell_range()
        for row_col in self.range_remove.keys():
            self.range[row_col[0]][row_col[1]] = \
    self.range[row_col[0]][row_col[1]].difference(self.range_remove[row_col])

        self.update_cell_range()

        return self.range

    def remove_from_range(self, rows, cols, val):                                           # Update the dictionary of tuples to sets, with the values to be removed from the range of cells

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
        if row == 4 and col ==8 and val == 7:
            pass
        
        rows =[]
        cols = []
        for i in range(0,9):
            if i != row:
               rows.append(i)
               cols.append(col)
        for j in range(0,9):
            if j != col:
                rows.append(row)
                cols.append(j)
        base_row = row - row % 3
        base_col = col - col % 3
        

        for value in Grid.range[row][col]:
            Grid.remove_from_range([row],[col],value)
        
    
        for r in range(base_row,base_row + 3):
            for c in range(base_col, base_col + 3):
                if (r,c) != (row,col):
                    rows.append(r)
                    cols.append(c)
                    Grid.remove_from_range(rows,cols,val)



#################################################################

class Unit:

    def __init__(self, i, j, grid = grid):                                                  # i is the row of the unit (1,2 or 3), j if the column of the unit (1,2 or 3)

        # Start and end rows, columns of the unit
        self.unit_row = i
        self.unit_col = j
        self.row_start = 3*i
        self.col_start = 3*j
        self.row_end = 3*i + 2
        self.col_end = 3*j + 3

        # Extract the unit data as a list of lists
        self.value = [grid[self.row_start][self.col_start:self.col_end], \
                       grid[self.row_start+1][self.col_start:self.col_end], \
                       grid[self.row_end][self.col_start:self.col_end]]
        self.range =[]
        self.unit_range = set()
        self.range_subsets =[]
        self.preemptive_dict = {}

    def __str__(self):
        
        """ Return the name of the object
        when called as a string """
        
        return "Unit {},{}".format(self.unit_row,self.unit_col)

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

    def rel_find(self, val):

        """ Find the first occurance of a
        certain value in the unit. Note,
        the output row and column are
        relative to the start of the unit"""

        row_star = None
        col_star = None
        for i, row in enumerate(self.value):
            for j, col in enumerate(row):
                if col == val and not row_star:
                    row_star = i
                    col_star = j
        return (row_star, col_star)

    def get_range(self):
        
        """ Returns a list of 3 lists, containing
        the range of each cell in the unit """
        
        self.range = [[col for col in row[self.col_start:self.col_end]] for row in Grid.range[self.row_start:self.row_end+1]]
        return self.range
        
    def get_unit_range(self):
        
        """ Returns the set of all remaining values
        to be filled in, in this unit """
        
        range_list = [item for sublist in self.range for item in sublist] # Convert list of lists to list
        self.unit_range = set().union(*range_list)
        return self.unit_range
        
    def get_unit_range_subsets(self):
        
        """ Returns the list of all subsets (as tuples) of 2 or
        more elements for the superset of unit_range """
        
        list_of_tuples = list(chain(*[combinations(list(self.unit_range), length) for length in range(2,10)]))
        #self.range_subsets = [set(elements) for elements in list_of_tuples]
        self.range_subsets = list_of_tuples
        return self.range_subsets
        
    def get_preemptive_cells(self):
        
        """ Return the dictionary of range subset tuples : Cells
        which contain the entire subset within its range """
        
        for row in range(self.row_start, self.row_end+1):
            for col in range(self.col_start, self.col_end):
                for subset in self.range_subsets:
                    if Grid.Cells[row][col].range <=set(subset) and len(Grid.Cells[row][col].range)>1:
                        #print "subset: {}, range: {}".format(subset, Grid.Cells[row][col].range)
                        if subset in self.preemptive_dict.keys():
                            self.preemptive_dict[subset].add(Grid.Cells[row][col])
                        else:
                            self.preemptive_dict[subset] = set([Grid.Cells[row][col]])
        return self.preemptive_dict
        
    def check_num_preemptive(self):
        range_update = False
        for key in self.preemptive_dict:
            if len(key) == len(self.preemptive_dict[key]):
                cells_in_unit = []
                for row in range(self.row_start, self.row_end+1):
                    for col in range(self.col_start, self.col_end):
                        cells_in_unit.append(Grid.Cells[row][col])
                                  
                for cell in cells_in_unit:
                    if cell not in self.preemptive_dict[key]:
                        rows =[]
                        cols =[]
                        for val in key:
                            if cell.value == 0:
                                rows.append(cell.row)
                                cols.append(cell.col)
                                Grid.remove_from_range(rows,cols,val)
                                print "Remove rows: {}".format(rows)
                                print "Remove cols: {}".format(cols)
                                print "Remove val: {}".format(val)
                                Grid.get_cell_ranges()
                                range_update = True
        return range_update



#################################################################

class Row:

    def __init__(self, row, grid = grid):
        self.value = grid[row]                       # Simply extract the row from the grid. This is a single list
        self.row = row
        
    def __str__(self):
        
        """ Return the name of the object
        when called as a string """
        
        return "Row {}".format(self.row)

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

    def get_num_blanks(self):

        """ Get the number of blank cells
        within the row """

        count = 0
        for element in self.value:
            if element == 0:
                count += 1
        return count

    def abs_find(self, val):

        """ Find the first occurance of a
        certain value in the row. Note,
        the output column value is absolute """

        i_star = None
        for i,col in enumerate(self.value):
            if col == val:
                i_star = i
                break
        return i_star


#################################################################

class Col:

    def __init__(self, col, grid = grid):
        self.value = []
        self.col = col
        for row in range(0,9):
            self.value.append(grid[row][col])        # Column is a list
        self.Cells = [0,0,0,0,0,0,0,0]

    def __str__(self):
        
        """ Return the name of the object
        when called as a string """
        
        return "Column {}".format(self.col)

    def get_cells(self):
        self.Cells = [Grid.Cells[x][self.col] for x in range(0,9)]

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

    def get_num_blanks(self):

        """ Get the number of blank cells
        within the column """

        count = 0
        for element in self.value:
            if element == 0:
                count += 1
        return count

    def abs_find(self, val):

        """ Find the first occurance of a
        certain value in the column. Note,
        the output row value is absolute """
        i_star = None
        for i,row in enumerate(self.value):
            if row == val:
                i_star = i
                break
        return i_star

#################################################################

class Cell:

    def __init__(self, row, col, grid = grid):
        self.value = grid[row][col]
        self.row = row                              # Each cell remembers which row it is in
        self.col = col                              # Each cell remembers which column it is in

    def __str__(self):
        
        """ Return the name of the object
        when called as a string """
        
        return "Cell {},{}".format(self.row,self.col)

    def filled(self):

        """ Function to flag if the cell has been
        filled (i.e. contains a non-zero value) """

        if self.value != 0:
            return True
        else:
            return False

    def update(self, val):

        """ Function to update the value of a cell
        with a particular value """

        self.value = val

    def get_range(self):

        """ Function to return a set of possible values
        which could be entered in this cell, based on row,
        column, unit contents """

        self.range = Grid.range[self.row][self.col]
        return self.range                       # Return the set of possible values which could go in the cell


    def get_empty_cells(self):

        """ Get the list of cells which are empty,
        within the column and row of the considered cell """

        (Row, Col, Unit) = Grid.get_obj(self.row, self.col)[0:3]        # Get (Row, Col, Unit) objects for the row and column number
        empty_cells = []                                                # Initialise empty cell list
        for j, c in enumerate(Row.value):
            if j == self.col:                                           # Skip the input cell
                pass
            elif c == 0:
                empty_cells.append(Grid.get_obj(self.row,j)[3])
            else:
                pass
        for i, r in enumerate(Col.value):
            if i == self.row:                                           # Skip the input cell
                pass
            elif r == 0:
                empty_cells.append(Grid.get_obj(i,self.col)[3])
            else:
                pass
        return empty_cells                                              # Return the list of Cell objects


#################################################################
#################################################################

#################################################################

# Create the Grid object based on defined classes #

#################################################################

Grid = Board()
#Grid.Units[2][2].get_range()
#for row in Grid.Units[2][2].range:
#    print "{}".format(row)


for col in range(0,9):
    Grid.Cols[col].get_cells()
Grid.get_cell_ranges()
