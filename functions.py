#################################################################
#################################################################

def remaining(Row, Col, Unit, Cell):

    """ Get the set of remaining possible values
    for a cell """
    if Cell.value == 0:
        all_vals = set(range(1,10))
        row_vals = set(Row.value)
        col_vals = set(Col.value)
        unit_vals = Unit.full_list()
        return all_vals.difference(row_vals | col_vals | unit_vals)     # | denotes union
    else:
        return set()

#################################################################
#################################################################

def get_unit_row_column(act_row, act_col):                          # Necessary - called by get_obj()

    """ Function returns the unit row and unit column
    for an input row number and column number """

    if act_row >= 0 and act_row <=2:
        unit_row = 0
    elif act_row >=3 and act_row <=5:
        unit_row = 1
    elif act_row >=6 and act_row <=8:
        unit_row = 2
    else:
        unit_row = None

    if act_col >= 0 and act_col <=2:
        unit_col = 0
    elif act_col >=3 and act_col <=5:
        unit_col = 1
    elif act_col >=6 and act_col <=8:
        unit_col= 2
    else:
        unit_col = None

    return (unit_row, unit_col)

#################################################################
#################################################################

def get_base(row, col):

    """ Return the base row and column
    of the unit for a given cell """

    base_row = row - row % 3
    base_col = col - col % 3

    return (base_row, base_col)                                     # Return base (row, column) tuple

#################################################################
#################################################################
