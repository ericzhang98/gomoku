# Game constants
GRID_LEN = 8
if GRID_LEN == 6:
    WIN_AMT = 4
else:
    WIN_AMT = 5
DEBUG_BOARD = False
LIMIT_TO_WINNING_MOVE = False
LIMIT_TO_CLOSE_MOVE = False

# MCTS constants
THINK_TIME = 400
DIRICHLET_NOISE = False

# Logging info constants
PRINT_CHILD_STATS = True
PRINT_PRIORS = False
PRINT_SEARCH_LEADER = False
