from state import State
import copy

GRID_LEN = 7
WIN_AMT = 4
DEBUG_BOARD = False
LIMIT_TO_WINNING_MOVE = False

class GomokuState(State):

    def __init__(self, grid, curr_player, prev_move, prev_prev_move, board=None):
        self.grid = grid
        self.grid_len = GRID_LEN
        self.win_amt = WIN_AMT
        self.options = self.get_options() # must be called before check_win

        if DEBUG_BOARD:
            self.board = board #for visual debugging
        else:
            self.board = None

        self.prev_move = prev_move
        self.prev_prev_move = prev_prev_move

        # check win for opponent
        terminal, winning_player = self.check_win(prev_move)

        if LIMIT_TO_WINNING_MOVE:
            # check guaranteed winning move for current player
            almost_win, win_option = self.get_win_info(prev_prev_move)
            if almost_win:
                self.options = [win_option]

        State.__init__(self, curr_player, terminal, winning_player)

    def possible_actions(self):
        return set(self.options)

    """
    returns GomokuState - new instance of next state after applying action
    """
    def apply_action(self, action):
        # TODO: optimize
        next_grid = copy.copy(self.grid)
        if next_grid[move_to_ind(action)] == '.':
            next_grid[move_to_ind(action)] = self.curr_player
            next_player = 'w' if self.curr_player == 'b' else 'b'
            next_state = GomokuState(next_grid, next_player, action, self.prev_move, self.board)
            if self.board:
                self.board.set_piece(action[0],action[1])
            return next_state
        else:
            print "Bad action"
            return None

    """
    returns list - list of reasonable actions
    """
    def get_options(self):
        grid = self.grid
        #collect all occupied spots
        current_pcs = []
        for r in range(self.grid_len):
            for c in range(self.grid_len):
                move = (r,c)
                if not grid[move_to_ind(move)] == '.':
                    current_pcs.append((r,c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [((self.grid_len-1)/2, (self.grid_len-1)/2)]
        #Reasonable moves should be close to where the current players are
        #Think about what these calculations are doing
        #min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(self.grid_len-1, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(self.grid_len-1, max(current_pcs, key=lambda x: x[1])[1]+1)
        #Options of reasonable next step moves
        options = []
        for i in range(min_r, max_r+1):
            for j in range(min_c, max_c+1):
                if not (i, j) in current_pcs:
                    options.append((i,j))
        return options

    def get_win_info(self, prev_prev_move):
        if prev_prev_move is None:
            return False, None
        r, c = prev_prev_move
        n_count, n_block = self.get_continuous_info(r, c, -1, 0)
        s_count, s_block = self.get_continuous_info(r, c, 1, 0)
        e_count, e_block = self.get_continuous_info(r, c, 0, 1)
        w_count, w_block = self.get_continuous_info(r, c, 0, -1)
        se_count, se_block = self.get_continuous_info(r, c, 1, 1)
        nw_count, nw_block = self.get_continuous_info(r, c, -1, -1)
        ne_count, ne_block = self.get_continuous_info(r, c, -1, 1)
        sw_count, sw_block = self.get_continuous_info(r, c, 1, -1)
        # change win options to one option if off by one and unblocked TODO: gut shot win
        almost_amt = self.win_amt-1

        groups = [(n_count, s_count, n_block, s_block), (e_count, w_count, e_block, w_block),
                  (se_count, nw_count, se_block, nw_block), (ne_count, sw_count, ne_block, sw_block)]

        for group in groups:
            count1, count2, block1, block2 = group
            if count1 + count2 + 1 == almost_amt:
                if block1:
                    return True, block1
                if block2:
                    return True, block2

        return False, None

    def get_continuous_info(self, r, c, dr, dc):
        move = (r, c)
        player = self.grid[move_to_ind(move)]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            new_move = (new_r, new_c)
            if 0 <= new_r < self.grid_len and 0 <= new_c < self.grid_len and self.grid[move_to_ind(new_move)] == player:
                result += 1
            elif 0 <= new_r < self.grid_len and 0 <= new_c < self.grid_len and self.grid[move_to_ind(new_move)] == '.':
                return result, (new_r,new_c)
            else:
                return result, None
            i += 1

    """
    checks for win via continuous count and filled board
    returns (bool, player) - (terminal, winning_player)
    """
    def check_win(self, move):
        if move is None:
            return False, None
        r, c = move
        if len(self.options) == 0:
            #In the unlikely event that no one wins before board is filled
            #Make white win since black moved first
            return (True, 'w')

        # check continuous counts TODO: optimize
        n_count = self.get_continuous_count(r, c, -1, 0)
        s_count = self.get_continuous_count(r, c, 1, 0)
        e_count = self.get_continuous_count(r, c, 0, 1)
        w_count = self.get_continuous_count(r, c, 0, -1)
        se_count = self.get_continuous_count(r, c, 1, 1)
        nw_count = self.get_continuous_count(r, c, -1, -1)
        ne_count = self.get_continuous_count(r, c, -1, 1)
        sw_count = self.get_continuous_count(r, c, 1, -1)
        if (n_count + s_count + 1 >= self.win_amt) or (e_count + w_count + 1 >= self.win_amt) or \
                (se_count + nw_count + 1 >= self.win_amt) or (ne_count + sw_count + 1 >= self.win_amt):
            return True, self.grid[move_to_ind(move)]
        return False, None

    def get_continuous_count(self, r, c, dr, dc):
        move = (r,c)
        player = self.grid[move_to_ind(move)]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            new_move = (new_r, new_c)
            if 0 <= new_r < self.grid_len and 0 <= new_c < self.grid_len and self.grid[move_to_ind(new_move)] == player:
                result += 1
            else:
                return result
            i += 1


# utils

def move_to_ind(move):
    grid_len = GRID_LEN
    r, c = move
    return grid_len*r + c

def ind_to_move(ind):
    grid_len = GRID_LEN
    return ind // grid_len, ind % grid_len
