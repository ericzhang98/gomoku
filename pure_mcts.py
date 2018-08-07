# State/action independent mcts

"""
Pure_MCTS --
main mcts class
- root: Node - init with root state
- uct_search: action - best action from mcts
"""
class Pure_MCTS:
    def __init__(self, root_state):
        self.root = Node(root_state)

    """
    main algo loop
    returns action - best action
    """
    def uct_search(self):
        counter = 0
        while counter < 100:
            counter += 1
            print "counter:", counter
            node_to_sim = self.tree_policy(self.root)
            winning_player = self.default_policy(node_to_sim)
            self.backup(node_to_sim, winning_player)

        action, child = self.best_action_child(self.root)
        return action

    """
    explores using ucb and chooses node to simulate
    returns node - node to simulate
    """
    def tree_policy(self, node):
        while not node.terminal:
            # ucb inf
            if not node.fully_expanded():
                return self.expand(node)
            else:
                action, child = self.best_action_child(node)
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
    returns (action, node) - best (action, child node) to explore
    """
    def best_action_child(self, node):
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
        if len(possible_actions) == 0:
            print "POSSIBLE ACTIONS IS 0"
            raise RuntimeError
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


class GomokuState(State):

    def __init__(self, grid, curr_player, prev_move):
        self.grid = grid
        self.maxrc = len(grid)-1
        self.grid_size = 26
        self.grid_count = 19
        self.options = self.get_options() # must be called before check_win

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
        next_grid = copy.deepcopy(self.grid)
        if next_grid[r][c] == '.':
            next_grid[r][c] = self.curr_player
            next_player = 'w' if self.curr_player == 'b' else 'b'
            next_state = GomokuState(next_grid, next_player, action)
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
        for r in range(len(grid)):
            for c in range(len(grid)):
                if not grid[r][c] == '.':
                    current_pcs.append((r,c))
        #At the beginning of the game, curernt_pcs is empty
        if not current_pcs:
            return [(self.maxrc/2, self.maxrc/2)]
        #Reasonable moves should be close to where the current players are
        #Think about what these calculations are doing
        #min(list, key=lambda x: x[0]) picks the element with the min value on the first dimension
        min_r = max(0, min(current_pcs, key=lambda x: x[0])[0]-1)
        max_r = min(self.maxrc, max(current_pcs, key=lambda x: x[0])[0]+1)
        min_c = max(0, min(current_pcs, key=lambda x: x[1])[1]-1)
        max_c = min(self.maxrc, max(current_pcs, key=lambda x: x[1])[1]+1)
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
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            return (True, self.grid[r][c])
        return (False, None)

    def get_continuous_count(self, r, c, dr, dc):
        player = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == player:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result