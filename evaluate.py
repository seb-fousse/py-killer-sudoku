#from killer_sudoku import KillerSudoku
from killer_sudoku.killer_sudoku import KillerSudoku
from killer_sudoku.cage import CageBuilder
import time

times_to_solve = []
solutions = []

for n in range(1,10):
  cages = None
  with open(f"puzzles/puzzle{n:05}.txt", 'r') as f:
    cb = CageBuilder(f.read())
    cages = cb.cages
  ks = KillerSudoku(cages=cages)

  start_time = time.time()
  solution = ks.solve()
  time_to_solve = time.time() - start_time

  times_to_solve.append(time_to_solve)
  solutions.append(solution)

total_time_to_solve = 0
num_solved_puzzles = 0
for i, solution in enumerate(solutions):
  if solution is not None:
    total_time_to_solve += times_to_solve[i]
    num_solved_puzzles += 1

if num_solved_puzzles == 0:
  print("No puzzles solved")
else:
  print(f"Average time to solve puzzle: {total_time_to_solve / num_solved_puzzles}")
    
