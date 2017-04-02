#################################################################
#################################################################

def remaining(Row, Col, Unit, Cell):

    """ Get the set of remaining possible values
    for a cell """

    if Cell.value == 0:
        all_vals = set(xrange(1,10))
        return all_vals.difference(set(Row.value) | set(Col.value) \
         | Unit.full_list())                                        # Returns set of possible values for cell
    else:
        return set()

#################################################################
#################################################################

def get_unit_row_column(act_row, act_col):

    """ Function returns the unit row and unit column
    for an input row number and column number """

    get_unit = lambda x: (x - x % 3)/3

    return tuple(map(get_unit,(act_row,act_col)))                     # Return unit row and column index in tuple

#################################################################
#################################################################

def get_base(row, col):

    """ Return the base row and column
    of the unit for a given cell """

    norm = lambda x: x - x % 3

    return tuple(map(norm,(row,col)))                                  # Return base (row, column) tuple

#################################################################
#################################################################
