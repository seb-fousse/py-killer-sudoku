from typing import Iterable, Tuple, Optional, Dict, List
from copy import deepcopy
from killer_sudoku.sudoku_data import *

"""
KillerSudoku(board, cages, raising=False)
- board: 9x9 array with numbers for set cells and 0 for unset cells
- cages: list of 
- solve(): returns a solved killer sudoku
- show(): prints the killer sudoku
"""

"""
Constraints:
- 9 unique values for each 9 columns, 9 rows, 9 subgrids. Each of these add to 45
- Cells in cages sum to a particular value and are unique in value
"""

"""
Strategy:
- Combination of backtracking and strategies listed here: https://www.sudokuwiki.org/killersudoku.aspx
"""

class Unsolvable(Exception):
  pass

class Cage():
  def __init__(self, sum: int, cells: Iterable[Tuple[int, int]]):
    """
    Initializes a cage for a Killer Sudoku

    :param sum: The sum of the values for each cell in the cage
    :param cells: Iterable containing (i, j) coordinates for each cell in this cage

    :raises ValueError: If there are an invalid number of cells in the cage, if the cage has an invalid sum,
      if a given cell's coordinates are counted multiples times in the cage, or if a cell in the cage is out of 
      bounds for a 9x9 Sudoku grid.
    """

    # Validate inputs
    if len(cells) < 1 or len(cells) > 9:
      raise ValueError("Must have 1-9 cells in a cage")
    cage_sum_min, cage_sum_max = possible_cage_sum_min_max[len(cells)]
    if sum < cage_sum_min or sum > cage_sum_max:
      raise ValueError(f"A cage with {len(cells)} cells has a sum in the range [{cage_sum_min}, {cage_sum_max}]")
    if len(cells) > len(set(cells)):
      raise ValueError("List of cells provided must have unique values")
    for cell in cells:
      if cell[0] < 0 or cell[0] > 8 or cell[1] < 0 or cell[1] > 8:
        raise ValueError(f"Cell {cell} is out of bounds for a 9x9 puzzle. Coordinates must be in the range [0-8]")
    
    self.sum = sum
    self.cells = cells

  def __repr__(self):
    return f"<Cage: {{sum: {self.sum}, cells: {self.cells}}}>"

class CageBuilder():
  def __init__(self, cages_iterable: Optional[Iterable[Dict]] = None):
    """
    Initializes a CageBuilder. A CageBuilder transforms a json or iterable into a list of Cages.
    This is inteded to make setting up the cages for a Killer Sudoku more convenient.

    :param cages_iterable: An iterable where each element is a dict in the format {'sum': n, 'cells':[(i,j)...]}
    """

    self.cages = []
    for cage_dict in cages_iterable:
      self.cages.append(Cage(cage_dict['sum'], [tuple(cell) for cell in cage_dict['cells']]))
  
  def add(self, cage: Cage):
    """
    Adds a Cage to the list of Cages contained in the CageBuilder

    :param cage: Cage to be added to the CageBuilder
    """
    self.cages.add(cage)


class KillerSudoku():
  def __init__(self, cages: Iterable[Cage], board: Optional[Iterable[Iterable[int]]] = [[0 for _ in range(0,9)] for _ in range(0,9)]):
    """
    Initializes a Killer Sudoku board

    :param board: Iterable for the initial state of the Killer Sudoku board
    :param cages: Iterable for the cages for the Killer Sudoku board
    
    :raises ValueError: If the board size isn't 9x9, if cells are counted in multiple cages, or if cages don't include all 81 cells
    """
    
    # Check board size
    if len(board) != 9:
      raise ValueError("Board must be 9x9")
    for i in range(len(board)):
      if len(board[i]) != 9:
        raise ValueError("Board must be 9x9")
    
    # Check that cells are unique to a single cage, and that cages encompass all 81 cells
    unique_cells = set()
    for cage in cages:
      for cell in cage.cells:
        if cell in unique_cells:
          raise ValueError(f"Cell {cell} has been included in multiple cages. A cell can only exist in 1 cage")
        else:
          unique_cells.add(cell)
    if len(unique_cells) != 81:
      raise ValueError("Cages do not contain all 81 cells in the puzzle")
    
    self.board: Iterable[Iterable[int]] = deepcopy(board)
    self.cages: Iterable[Cage] = deepcopy(cages)
    self._rows: Iterable[Cage] = []
    self._columns: Iterable[Cage] = []
    self._subgrids: Iterable[Cage] = []

    self._cage_neighbors = self._get_cage_neighbors_map()

    # Add cages for rows
    for i in range(0,9):
      row = []
      for j in range(0,9):
        row.append((i,j))
      self._rows.append(Cage(45, row))

    # Add cages for columns
    for j in range(0,9):
      column = []
      for i in range(0,9):
        column.append((i,j))
      self._columns.append(Cage(45, column))

    # Add cages for subgrids
    subgrids = [[None for _ in range(9)] for _ in range(9)]
    for i in range(9):
        for j in range(9):
            subgrid_index = (i // 3) * 3 + (j // 3)
            subgrids[subgrid_index][i % 3 * 3 + j % 3] = (i, j)
    for subgrid in subgrids:
      self._subgrids.append(Cage(45, subgrid))

  def solve(self, raising: Optional[bool] = False) -> 'KillerSudoku':
    pass
  
  def show(self) -> None:
    # Top line
    sep_line = "╔"
    for j in range(8):
      sep_line += "═══"
      sep_line += "═" if (0, j+1) in self._cage_neighbors[(0,j)] else "╦"
    sep_line += "═══╗"
    print(sep_line)

    sep_chars = {
      # Up   Left  Down  Right
      (True, True, True, True) : "╬",
      (True, True, True, False) : "╣",
      (True, True, False, True) : "╩",
      (True, True, False, False) : "╝",
      (True, False, True, True) : "╠",
      (True, False, True, False) : "║",
      (True, False, False, True) : "╚",
      (True, False, False, False) : " ",
      (False, True, True, True) : "╦",
      (False, True, True, False) : "╗",
      (False, True, False, True) : "═",
      (False, True, False, False) : " ",
      (False, False, True, True) : "╔",
      (False, False, True, False) : " ",
      (False, False, False, True) : " ",
      (False, False, False, True) : " "
    }

    # First 8 rows
    for i in range(0,8):
      cell_line = "║"
      sep_line = "║" if (i+1, 0) in self._cage_neighbors[(i,0)] else "╠"
      for j in range(0,9):
        value = ' ' if self.board[i][j] == 0 else self.board[i][j]
        neighbors = self._cage_neighbors[(i,j)]
        cell_line += f' {value} '
        sep_line += "   " if (i+1, j) in neighbors else "═══"
        cell_line += " " if (i, j+1) in neighbors else "║"
        if j == 8:
          sep_line += "║" if (i+1, j) in neighbors else "╣"
          break
        right_neighbors = self._cage_neighbors[(i,j+1)]
        below_neighbors = self._cage_neighbors[(i+1,j)]
        sep_up = (i,j+1) not in neighbors
        sep_left = (i+1, j) not in neighbors
        sep_down = (i+1, j+1) not in below_neighbors
        sep_right = (i+1, j+1) not in right_neighbors
        sep_line += sep_chars[(sep_up,sep_left,sep_down,sep_right)]
      print(cell_line)
      print(sep_line)
    
    # Last row
    cell_line = "║"
    sep_line = "╚"
    for j in range(0,8):
      neighbors = self._cage_neighbors[(8,j)]
      cell_line += f' {value} '
      cell_line += " " if (8, j+1) in neighbors else "║"
      sep_line += "═══"
      sep_line += "═" if (8, j+1) in self._cage_neighbors[(8,j)] else "╩"
    cell_line += f' {value} ║'
    sep_line += "═══╝"
    print(cell_line)
    print(sep_line)

  def _get_cage_neighbors_map(self):
    cage_neighbors_map = {}
    for cage in self.cages:
      for cell in cage.cells:
        cage_neighbors_map[cell] = [c for c in cage.cells if c != cell]
    return cage_neighbors_map
