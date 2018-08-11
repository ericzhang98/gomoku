# State/action independent mcts

"""
Pure_MCTS --
main mcts class
- root: Node - init with root state
- uct_search: action - best action from mcts
"""
THINK_TIME = 5000
class Pure_MCTS:
    def __init__(self, root_state):
        self.root = Node(root_state)

    """
    main algo loop
    returns action - best action
    """
    def uct_search(self):
        counter = 0
        while counter < THINK_TIME:
            counter += 1
            node_to_sim = self.tree_policy(self.root)
            winning_player = self.default_policy(node_to_sim)
            self.backup(node_to_sim, winning_player)
            if counter % 100 == 0:
                action, child = self.wr_action_child(self.root)
                print("best ac so far:({}, {})".format(action[0], action[1]))

        children = self.root.action_children.values()
        children = sorted(children, key= lambda c: float(c.losses)/c.visits, reverse=True)
        for child in children:
            print("Action: {}, Wins: {}, Visits: {} WR: {}".format(child.state.prev_move, child.losses, child.visits, float(child.losses)/child.visits))

        action, child = self.wr_action_child(self.root)
        return action

    """
    explores using ucb and chooses node to simulate
    returns node - node to simulate
    """
    def tree_policy(self, node):
        while not node.terminal:
            # ucb val is technically inf
            if not node.fully_expanded():
                return self.expand(node)
            else:
                action, child = self.ucb_action_child(node)
                node = child
        return node

    """
    try an untried action and expand node (represents ucb returning inf)
    modifies: node.untried_actions, node.action_children
    returns node - the newly expanded child node of og node
    """
    def expand(self, node):
        # choose random action in node's untried action set and rm from set
        rand_untried_action = node.rand_untried_action(rm=True)
        # make child node with next state + add edges
        next_state = node.state.apply_action(rand_untried_action)
        child_node = Node(next_state)
        child_node.parent = node
        node.action_children[rand_untried_action] = child_node
        return child_node

    """
    ucb
    returns (action, node) - ucb optimal (action, child node) to explore
    """
    def ucb_action_child(self, node):
        from math import sqrt, log
        best_val = -1
        best_action_child = None
        c = 2
        for action, child in node.action_children.items():
            # child.losses = curr node's wins after taking the action, since children node's player is opponent
            ucb_val = float(child.losses)/child.visits + c*sqrt(2*log(node.visits)/child.visits)
            if ucb_val > best_val:
                best_val = ucb_val
                best_action_child = (action, child)
        return best_action_child

    """
    action child with highest win rate (to be returned from uct search)
    returns (action, node) - (action, child node) with highest win rate
    """
    def wr_action_child(self, node):
        from math import sqrt, log
        best_win_rate = -1
        best_action_child = None
        for action, child in node.action_children.items():
            # child.losses = curr node's wins after taking the action, since children node's player is opponent
            win_rate = float(child.losses)/child.visits
            if win_rate > best_win_rate:
                best_win_rate = win_rate
                best_action_child = (action, child)
        return best_action_child

    """
    random simulation until a player wins
    returns player - winning player
    """
    def default_policy(self, node):
        while not node.terminal:
            rand_action = node.rand_action()
            next_state = node.state.apply_action(rand_action)
            node = Node(next_state)
        return node.state.winning_player

    """
    updates visits and wins count according to winning_player and reward function
    returns nothing
    """
    def backup(self, node, winning_player):
        while node is not None:
            node.visits += 1
            reward = self.reward(node, winning_player)
            node.wins += reward
            node.losses += (1 if reward == 0 else 0)
            node = node.parent

    def reward(self, node, winning_player):
        return 1 if winning_player == node.state.curr_player else 0


"""
Node --
keeps track of state, actions, and stats info of the state
- state: state
- terminal: bool - directly corresponds to state.terminal
- parent: Node
- action_children: dict - maps: action -> child node
- all_actions: set - const set of actions
- untried_actions: set - set of untried actions
- full_expanded() -> bool
- rand_action() -> action
- rand_untried_action() -> action
"""
class Node:
    def __init__(self, state):
        self.state = state

        self.terminal = state.terminal
        self.parent = None
        self.action_children = {} # maps: actions -> nodes containing next state

        possible_actions = state.possible_actions()
        # if len(possible_actions) == 0:
        #     print "POSSIBLE ACTIONS IS 0"
            # raise RuntimeError
        self.all_actions = set(possible_actions)
        self.untried_actions = set(possible_actions)

        # stats
        self.visits = 0
        self.wins = 0
        self.losses = 0

    """
    returns bool - whether or not the node is fully expanded
    """
    def fully_expanded(self):
        return len(self.untried_actions) == 0

    """
    returns action - a random action from all_actions
    """
    def rand_action(self):
        import random
        index = random.randint(0, len(self.all_actions)-1)
        rand_action = list(self.all_actions)[index]
        return rand_action

    """
    rm: bool - whether or not to remove the random action from untried_actions
    returns action - a random action from untried_actions
    """
    def rand_untried_action(self, rm=False):
        import random
        index = random.randint(0, len(self.untried_actions) - 1)
        rand_untried_action = list(self.untried_actions)[index]
        if rm:
            self.untried_actions.remove(rand_untried_action)
        return rand_untried_action


"""
action: some hashable property used by apply_action to create a new next state

state:
- curr_player: player - player that is going to make a move on the current state
- terminal: bool - whether or not a player has won the game (must be correct on init)
- winning_player: player - (must be non null if terminal == true)

- possible_actions() -> set - non-empty set of possible actions (called by Node at init to init untried_actions)
- apply_action(action) -> state - next state (should not modify the state)
"""

class State:
    def __init__(self, curr_player, terminal, winning_player):
        self.curr_player = curr_player
        self.terminal = terminal
        self.winning_player = winning_player

    def possible_actions(self):
        raise NotImplementedError

    def apply_action(self, action):
        raise NotImplementedError

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
        import copy
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

def rc_to_ind(r, c):
    grid_len = GRID_LEN
    return grid_len*r + c

def ind_to_rc(ind):
    grid_len = GRID_LEN
    return ind // grid_len, ind % grid_len