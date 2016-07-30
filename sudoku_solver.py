# -*- encoding: utf-8 -*-

from pprint import pprint
# TODO: pretty view
# None - empty cells
sudoku_example = [
    [None,    7,    6, None,    9,    5, None,    8, None],
    [   5,    2,    9, None, None,    8,    7,    3, None],
    [None, None, None,    7, None, None, None,    5,    9],
    [   7,    1,    4,    6,    3,    2, None,    9, None],
    [None, None, None, None, None, None, None, None, None],
    [None,    9, None,    5,    8,    1,    4,    2,    7],
    [   9,    8, None, None, None,    4, None, None, None],
    [None,    3,    7,    9, None, None,    8,    4,    5],
    [None,    6, None,    8,    2, None,    9,    1, None],
]

def print_sudoku(sudoku):
    if isinstance(sudoku, Sudoku):
        sudoku = sudoku.fields
    print('\n'.join(', '.join('-' if cell is None else str(cell) for cell in row) for row in sudoku))


#0 -> (0,0) (0,1) (0,2) (1,0) (1,1) (1,2)  (2, 0) (2, 1) (2, 2)
#1 -> (3,0) (3,1) (3,2) (4,0) (4,1) (4,2)  (5, 0) (5, 1) (5, 2)

def squads_cells(fields, squad):
    row = (squad // 3) * 3
    column = (squad % 3) * 3
    for r in fields[row: row + 3]:
        yield from r[column: column + 3]

            
# pprint([[get_squad_by_coords(i, j) for j in range(9)] for i in range(9)])
get_squad_by_coords = lambda i, j: i // 3 * 3 + j // 3

def get_possible_values(fields, i, j):
    if fields[i][j] is not None:
        return set()
    possible = set(range(1, 10))

    for _i in range(9):
        possible.discard(fields[_i][j])

    for _j in range(9):
        possible.discard(fields[i][_j])
        
    for cell in squads_cells(fields, get_squad_by_coords(i, j)):
        possible.discard(cell)

    return possible

def get_one(s):
    for e in s:
        return e

class WrongSudokuException(Exception):
    pass

class SudokuCellSetted(Exception):
    pass

class Sudoku:

    def __init__(self, fields):
        self.fields = fields
        self.rows = [{j for j, x in enumerate(row) if x is None} for row in fields]
        self.columns = [{i for i in range(9) if fields[i][j] is None} for j in range(9)]
        
        self.possible_values = [[get_possible_values(fields, i, j) for j in range(9)] for i in range(9)]
        self.squads = [set(filter(None, squads_cells(fields, i))) for i in range(9)]

    def can_set(self, x, y, value):
        return value in self.possible_values[x][y]
    
    def _set(self, x, y, value):
        self.fields[x][y] = value
        self.rows[x].discard(y)
        self.columns[y].discard(x)
        self.recalc_cell(x, y, value)
        
    def set(self, x, y, value):
        if not self.can_set(x, y, value):
            print(x, y, value, self.possible_values[x][y])
            raise WrongSudokuException("cannot set")
        if self.fields[x][y] is not None:
            raise SudokuCellSetted("cannot set cell:" + str([x,y]) + 'value:' + str(value))
        self._set(x, y, value)

    def trySetOne(self, x, y):
        possible_values = self.possible_values[x][y]
        if len(possible_values) != 1:
            return False
        value = possible_values.pop()
        self._set(x, y, value)
        return True

    def recalc_cell(self, x, y, value):
        """ Цель: найти ещё одну клетку куда можно поставить"""
        squad = get_squad_by_coords(x, y)
        self.squads[squad].discard(value)

        to_set = []
        for xs in self.columns[y]:
            s = self.possible_values[xs][y]
            s.discard(value)
            if len(s) == 1:
                to_set.append((xs, y, s.pop()))

        row_possibles = self.possible_values[x]
        for ys in self.rows[x]:
            s = row_possibles[ys]
            s.discard(value)
            if len(s) == 1:
                to_set.append((x, ys, s.pop()))

        for xs, ys, v in to_set:
            self._set(xs, ys, v)
        self.check_squad(squad)
    
    def check_squad(self, n):
        if len(self.squads[n]) != 1:
            return False
        value = get_one(self.squads[n])
        row = (squad // 3) * 3
        column = (squad % 3) * 3
        for i in range(3):
            r = self.fields[row + i]
            for j in range(3):
                if r[column + j] is None:
                    self.set(row + i, column + j, value)
                    return True
        return False

    def check(self):
        for i in range(9):
            for j in range(9):
                self.trySetOne(i, j)
            self.check_squad(i)
    

def main():
    sudoku = Sudoku(sudoku_example)
    print("ORIGIN:")
    print_sudoku(sudoku)
    
    sudoku.check()
    print("AFTER CHECK:")
    print_sudoku(sudoku)


if __name__ == '__main__':
    main()