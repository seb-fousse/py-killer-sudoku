from typing import Iterable, Tuple, Optional, Union, Mapping
from copy import deepcopy
from killer_sudoku.cage import Cage

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

class UnsolvableError(Exception):
  pass

class KillerSudoku:

  def __init__(self, cages: Iterable[Cage], board: Optional[Iterable[Iterable[int]]] = [[0 for _ in range(0,9)] for _ in range(0,9)]):
    """
    Initializes a Killer Sudoku board

    :param Iterable[Cage] cages: Iterable for the cages for the Killer Sudoku board
    :param Iterable[Iterable[int]] board: 9x9 list for the initial state of the Killer Sudoku board, defaults to a 9x9 list of 0s
    
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
    
    # TODO: Check that board has values appropriately assigned
    
    self.board: Iterable[Iterable[int]] = deepcopy(board)
    self.cages: Iterable[Cage] = deepcopy(cages)
    self._rows: Iterable[Cage] = []
    self._columns: Iterable[Cage] = []
    self._subgrids: Iterable[Cage] = []

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
    
    self._neighbors_map = self._get_neighbors_map()


  def solve(self, raising: Optional[bool] = False) -> Union['KillerSudoku', None]:
    solution = _Solver(self).solve()
    if solution:
      return solution
    elif raising:
      return UnsolvableError("No solution found")
    else:
      return None

  def show(self) -> None:
    # Top line
    sep_line = "╔"
    for j in range(8):
      sep_line += "═══"
      sep_line += "═" if (0, j+1) in self._neighbors_map[(0,j)]['cage'] else "╦"
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
      (False, False, False, False) : " "
    }

    # First 8 rows
    for i in range(0,8):
      cell_line = "║"
      sep_line = "║" if (i+1, 0) in self._neighbors_map[(i,0)]['cage'] else "╠"
      for j in range(0,9):
        value = ' ' if self.board[i][j] == 0 else self.board[i][j]
        neighbors = self._neighbors_map[(i,j)]['cage']
        cell_line += f' {value} '
        sep_line += "   " if (i+1, j) in neighbors else "═══"
        cell_line += " " if (i, j+1) in neighbors else "║"
        if j == 8:
          sep_line += "║" if (i+1, j) in neighbors else "╣"
          break
        right_neighbors = self._neighbors_map[(i,j+1)]['cage']
        below_neighbors = self._neighbors_map[(i+1,j)]['cage']
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
      neighbors = self._neighbors_map[(8,j)]['cage']
      cell_line += f' {value} '
      cell_line += " " if (8, j+1) in neighbors else "║"
      sep_line += "═══"
      sep_line += "═" if (8, j+1) in self._neighbors_map[(8,j)]['cage'] else "╩"
    cell_line += f' {value} ║'
    sep_line += "═══╝"
    print(cell_line)
    print(sep_line)

  def _get_neighbors_map(self) -> Mapping[Tuple, Iterable]:
    neighbors_map = {}
    for i in range(9):
      for j in range(9):
        neighbors_map[(i,j)] = {}
    for row in self._rows:
      for cell in row.cells:
        neighbors_map[cell]['row'] = [c for c in row.cells if c != cell]
    for column in self._columns:
      for cell in column.cells:
        neighbors_map[cell]['column'] = [c for c in column.cells if c != cell]
    for subgrid in self._subgrids:
      for cell in subgrid.cells:
        neighbors_map[cell]['subgrid'] = [c for c in subgrid.cells if c != cell]
    for cage in self.cages:
      for cell in cage.cells:
        neighbors_map[cell]['cage'] = [c for c in cage.cells if c != cell]
    return neighbors_map

class _Solver:
  def __init__(self, ks: KillerSudoku):
    self.ks = ks
    # Initialize empty cells to have domain 1-9
    self.empty_cell_possibilities = dict()
    for i in range(9):
      for j in range(9):
        if self.ks.board[i][j] == 0:
          self.empty_cell_possibilities[(i,j)] = {1,2,3,4,5,6,7,8,9}
    
  def solve(self) -> Union[Iterable[Iterable[int]], None]:
    # Decide which possibility reduction strategies to use here
    # TODO: easy killer combo reduce
    # TODO: hard killer combo reduce
    # TODO: constraint reduce
    # TODO: single innies and outies reduce
    return #self._recursive_solve(self.board, self.empty_cell_possibilities)
    
  def _recursive_solve(self, board: Iterable[Iterable[int]], empty_cell_possibilities: Mapping[Tuple[int, int], Iterable]) -> Union[Iterable[Iterable[int]], None]:
    while len(empty_cell_possibilities) > 0:
      if self._impossible(board):
        return None
      self._fill_board(board, empty_cell_possibilities)
      # Apply strategies to reduce empty cell possibilities
      # TODO: Consider adding more strategies if you can
      # Maybe use a flag system to skip unnecessary strategies
      if self._constraint_reduce(board, empty_cell_possibilities):
        continue
      if self._last_remaining_reduce():
        continue
      if self._conjugate_pair_reduce(): # Naked & hidden pairs
        continue
      if self._conjugate_triple_reduce(): # Naked & hidden triples
        continue
      if self._pointing_pair_reduce():
        continue
      if self._hard_killer_combo_reduce():
        continue

      # Apply backtrack if strategies couldn't reduce empty cell possibilities
      

    return board

  def _fill_board(board: Iterable[Iterable[int]], empty_cell_possibilities: Mapping[Tuple[int, int],Iterable[int]]) -> None:
    set_cells = []
    for blank_cell, possibilities in empty_cell_possibilities:
      if len(possibilities) == 1:
        value_to_set = possibilities.pop()
        board[blank_cell[0]][blank_cell[1]] = value_to_set
        set_cells.append(blank_cell)
    for set_cell in set_cells:
      empty_cell_possibilities.pop(set_cell)

  def _impossible(self, board: Iterable[Iterable[int]], empty_cell_possibilities: Mapping[Tuple[int, int],Iterable[int]]) -> bool:
    return False
  
  def _constraint_reduce(self, board: Iterable[Iterable[int]], empty_cell_possibilities: Mapping[Tuple[int, int],Iterable[int]]) -> bool:
    """
    Enforce the killer suduko constraints on the given board. Reduce empty cell possibilities. 
    TODO - Think of more efficient way to do this reduce as it will be the most frequently run
    maybe? keep track of already filled cells in a separate list
    """
    for constraint_list in (self.ks.cages, self.ks._rows, self.ks._columns, self.ks._subgrids):
      for constraint in constraint_list:
        pass
    
    return False
  
  def _last_remaining_reduce(self, board: Iterable[Iterable[int]], empty_cell_possibilities: Mapping[Tuple[int, int],Iterable[int]]) -> bool:
    """
    If a particular value is only possible in one cell in a given row, col, or subgrid. Update the possibility to the last remaining value
    https://www.sudokuwiki.org/Getting_Started
    """
    return False

  def _conjugate_pair_reduce(self, board: Iterable[Iterable[int]], empty_cell_possibilities: Mapping[Tuple[int, int],Iterable[int]]) -> bool:
    """
    https://www.sudokuwiki.org/Naked_Candidates
    https://www.sudokuwiki.org/Hidden_Candidates
    """
    return False
  
  def _conjugate_triple_reduce(self, board: Iterable[Iterable[int]], empty_cell_possibilities: Mapping[Tuple[int, int],Iterable[int]]) -> bool:
    """
    https://www.sudokuwiki.org/Naked_Candidates
    https://www.sudokuwiki.org/Hidden_Candidates
    """
    return False
  
  def _pointing_pair_reduce(self, board: Iterable[Iterable[int]], empty_cell_possibilities: Mapping[Tuple[int, int],Iterable[int]]) -> bool:
    """
    https://www.sudokuwiki.org/Intersection_Removal
    """
    return False
  
  def _hard_killer_combo_reduce(self, board: Iterable[Iterable[int]], empty_cell_possibilities: Mapping[Tuple[int, int],Iterable[int]]) -> bool:
    """
    https://www.sudokuwiki.org/Killer_Combinations
    """
    return False