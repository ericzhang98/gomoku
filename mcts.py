from math import sqrt, log
import random
import time

class State:
    def __init__(self, grid, piece):
        self.grid = grid
        self.maxrc = len(grid)-1
        self.grid_size = 26
        self.grid_count = 19
        self.game_over = False
        self.winner = None
        self.piece = piece
        self.options = None

    def get_options(self):
        if self.options != None:
            return self.options
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
        #Reasonable moves should be close to where the current pieces are
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
        if len(options) == 0:
            #In the unlikely event that no one wins before board is filled
            #Make white win since black moved first
            self.game_over = True
            self.winner = 'w'
        self.options = options
        return options

    # checks for win and modifies self.game_over and self.winner if it's a win
    def check_win(self, r, c):
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
            self.winner = self.grid[r][c]
            self.game_over = True

    def get_continuous_count(self, r, c, dr, dc):
        piece = self.grid[r][c]
        result = 0
        i = 1
        while True:
            new_r = r + dr * i
            new_c = c + dc * i
            if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
                if self.grid[new_r][new_c] == piece:
                    result += 1
                else:
                    break
            else:
                break
            i += 1
        return result


class Node:
    def __init__(self, state, visits, wins):
        self.state = state
        self.visits = visits
        self.wins = wins
        self.terminal = state.game_over
        self.children = []
        self.untried_actions = set(state.get_options())
        self.action = None
        self.parent = None

    def fully_expanded(self):
        return len(self.untried_actions) == 0

class MCTS:
    def __init__(self, grid, piece):
        self.grid = grid
        self.maxrc = len(grid)-1
        self.piece = piece 
        self.grid_size = 26
        self.grid_count = 19
        root_state = State(grid, piece)
        self.root_node = Node(root_state, 0, 0)
        self.options = self.root_node.state.get_options()
        print "--------------------------------------------"
        print self.piece
        print self.root_node.state.get_options()
        #self.best_move = self.rand_action(self.root_node.state) # init best_move with rand action
        #self.best_move = self.uct_search()
        #print self.best_move

    def uct_search(self):
        root_node = self.root_node
        start_time = time.time()
        counter = 0
        while counter < 300:
            counter += 1
            print counter
            best_so_far = self.best_child_best(root_node)
            if best_so_far != None:
                print "Best so far", best_so_far.action
            # find node to explore according to tree_policy
            node_explore = self.tree_policy(root_node)
            # generate reward from node to explore
            winner = self.default_policy(node_explore)
            print "Winner:", winner
            # backup with the reward generated from node explore
            self.backup(node_explore, winner)
            print "Child wins:", [x.wins for x in root_node.children]
            print "Child visits:", [x.visits for x in root_node.children]
            print "Child UCB:", [self.ucb_value(root_node, x) for x in root_node.children]
            print "Child explore:", [self.explore_value(root_node, x) for x in root_node.children]
            print "Child to move:", [root_node.children[i].action for i in range(len(root_node.children))]
        return self.best_child_best(root_node).action

    # explores and chooses best new node
    def tree_policy(self, node):
        # keep going until terminal node
        while not node.terminal:
            print "following curr node:", node.state.piece
            # if not fully expanded, expand
            if not node.fully_expanded():
                print "expanding.."
                return self.expand(node)
            # otherwise go down along best child
            else:
                print "selecting best child.."
                node = self.best_child(node)
        return node

    # try an untried action and expand node
    def expand(self, node):
        # choose random action out of self.untried_actions and update
        untried_list = list(node.untried_actions)
        action = untried_list[random.randint(0, len(untried_list)-1)]
        node.untried_actions.remove(action)

        # make next node with new state
        next_state = self.apply_action(action[0], action[1], node.state)
        next_node = Node(next_state, 0, 0)
        next_node.action = action

        # add to curr node's children and set next node's parent
        node.children.append(next_node)
        next_node.parent = node

        return next_node

    def best_child(self, node):
        # upper confidence bound formula
        best_val = -1
        best_node = None
        c = 2
        for child in node.children:
            ucb_val = float(child.wins)/child.visits + c*sqrt(2*log(node.visits)/child.visits)
            if ucb_val > best_val:
                best_val = ucb_val
                best_node = child
                # print ucb_val
        return best_node

    def best_child_best(self, node):
        # upper confidence bound formula
        best_val = -1
        best_node = None
        c = 0
        for child in node.children:
            ucb_val = float(child.wins)/child.visits + c*sqrt(2*log(node.visits)/child.visits)
            if ucb_val > best_val:
                best_val = ucb_val
                best_node = child
                # print ucb_val
        return best_node

    def ucb_value(self, node, child):
        c = 0
        return float(child.wins)/child.visits + c*sqrt(2*log(node.visits)/child.visits)

    def explore_value(self, node, child):
        c = 2
        return c*sqrt(2*log(node.visits)/child.visits)

    def default_policy(self, node):
        while not node.terminal:
            action = self.rand_action(node.state)
            next_state = self.apply_action(action[0], action[1], node.state)
            node = Node(next_state, 0, 0)
            #print "rand action", action
            #print "next state player:", next_state.piece
        return node.state.winner

    def backup(self, node, winner):
        while node != None:
            node.visits += 1
            node.wins += self.reward(node, winner) 
            node = node.parent

    def reward(self, node, winner):
        # piece is opponent's piece at each node
        #print "evaluating reward", 0 if winner == node.state.piece else 1, winner, node.state.piece
        print "curr node player:", node.state.piece, "reward:", 0 if winner == node.state.piece else 1
        return 0 if winner == node.state.piece else 1

    # apply action to state and return next state
    def apply_action(self, r, c, state):
        import copy
        state = State(copy.deepcopy(state.grid), state.piece)
        if state.grid[r][c] == '.':
            state.grid[r][c] = state.piece
            if state.piece == 'b':
                state.piece = 'w'
            else:
                state.piece = 'b'
            state.check_win(r, c)
            return state 
        else:
            return None

    # return random action from state
    def rand_action(self, state):
        options = state.get_options()
        m = random.randint(0,len(options)-1)
        return options[m]

    def make_move(self):
        return self.uct_search()
