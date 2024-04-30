from typing import Iterable, Mapping, Optional, Tuple, Union
from killer_sudoku.static_data import *

class Cage:
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

  def __len__(self) -> int:
    return len(self.cells)

  def __repr__(self) -> str:
    return f"<Cage: {{sum: {self.sum}, cells: {self.cells}}}>"

class CageBuilder:
  def __init__(self, cages: Optional[Union[str, Iterable[Union[Mapping, Iterable]]]] = None):

    # TODO: make this more comprehensive, add checking for correctly formatting etc

    self.cages = []
    if type(cages) is str:
      for line in cages.splitlines():
        if len(line) != 0:
          numbers = line.split()
          sum = int(numbers[0])
          cells = [(int(n[0]),int(n[1])) for n in numbers[1:]]
          self.cages.append(Cage(sum, cells))
    elif type(cages) == Iterable:
      for cage in cages:
        if type(cage) == dict:
          self.cages.append(Cage(cage['sum'], [tuple(cell) for cell in cage['cells']]))
        elif type(cage) == list:
          self.cages.append(Cage(cage[0], [tuple(cell) for cell in cage[1]]))

  def add(self, cage: Cage) -> None:
    """
    Adds a Cage to the list of Cages contained in the CageBuilder

    :param Cage cage: Cage to be added to the CageBuilder
    """
    self.cages.add(cage)