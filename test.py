import json
from killer_sudoku.killer_sudoku import KillerSudoku, CageBuilder

blank_board = [[0 for _ in range(0,9)] for _ in range(0,9)]

cages = None
with open('unsolved_puzzles/puzzle1.json', 'r') as f:
  cb = CageBuilder(json.load(f))
  cages = cb.cages

ks = KillerSudoku(cages=cages)

ks.show()