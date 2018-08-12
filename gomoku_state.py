from pure_mcts import State
import copy

GRID_LEN = 7
DEBUG_BOARD = False

class GomokuState(State):

    def __init__(self, grid, curr_player, prev_move, prev_prev_move, board=None):
        self.grid = grid
        self.grid_len = GRID_LEN
        self.win_amt = 4
        self.options = self.get_options() # must be called before check_win

        if DEBUG_BOARD:
            self.board = board #for visual debugging
        else:
            self.board = None

        self.prev_move = prev_move
        self.prev_prev_move = prev_prev_move

        if prev_move is None:
            (terminal, winning_player) = (False, None)
        else:
            (terminal, winning_player) = self.check_win(prev_move[0], prev_move[1])
        State.__init__(self, curr_player, terminal, winning_player)

    def possible_actions(self):
        return set(self.options)

    """
    returns GomokuState - new instance of next state after applying action
    """
    def apply_action(self, action):
        (r, c) = action
        # TODO: optimize
        next_grid = copy.copy(self.grid)
        if next_grid[rc_to_ind(r,c)] == '.':
            next_grid[rc_to_ind(r,c)] = self.curr_player
            next_player = 'w' if self.curr_player == 'b' else 'b'
            next_state = GomokuState(next_grid, next_player, action, self.prev_move, self.board)
            if self.board:
                self.board.set_piece(r,c)
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
                if not grid[rc_to_ind(r,c)] == '.':
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

    """
    checks for win via continuous count and filled board
    returns (bool, player) - (terminal, winning_player)
    """
    def check_win(self, r, c):
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
            return (True, self.grid[rc_to_ind(r,c)])
        return (False, None)

    def get_continuous_count(self, r, c, dr, dc):
        player = self.grid[rc_to_ind(r,c)]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_len and 0 <= new_c < self.grid_len and self.grid[rc_to_ind(new_r,new_c)] == player:
                result += 1
            else:
                break
            i += 1
        return result


# utils

def rc_to_ind(r, c):
    grid_len = GRID_LEN
    return grid_len*r + c

def ind_to_rc(ind):
    grid_len = GRID_LEN
    return ind // grid_len, ind % grid_len