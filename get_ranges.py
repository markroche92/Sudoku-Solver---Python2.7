""" This file contains functions to
get the set of values in the range of the
cells within the row/col of an input cell,
excluding the range of the input cell """

#################################################################
#################################################################

def get_row_range_wo(Cell, row, col, col_step = 0):

    """ Return the set of values in the
    range of all cells in a row, except for
    the cells corresponding to col and col + 2"""

    list_sets = [x.range for i,x in enumerate(Cell.Parent.Cells[row][:]) \
                 if (i!=col and i!=col+col_step)]

    full_set = set().union(*list_sets)
    return full_set

#################################################################
#################################################################

def get_col_range_wo(Cell, row, col, row_step = 0):

    """ Return the set of values in the
    range of all cells in a col, except for
    the cells corresponding to row and row + 2"""

    list_sets = [x.get_range() for i,x in enumerate(Cell.Parent.Cols[col].Cells) \
                 if (i!=row and i!=row+row_step)]

    full_set = set().union(*list_sets)
    return full_set

#################################################################
#################################################################
