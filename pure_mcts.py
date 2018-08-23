# State/action independent mcts

import numpy as np
from math import sqrt, log

THINK_TIME = 2000

seed = np.random.randint(999999)
print "Seed:", seed
np.random.seed(seed)

"""
PureMCTS --
main mcts class
- root: Node - init with root state
- uct_search: action - best action from mcts
"""
class PureMCTS:
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

            # print child stats
            if counter % 100 == 0:
                action, child = self.wr_action_child(self.root)
                print("best ac so far:({}, {})".format(action[0], action[1]))

        # print child stats
        children = self.root.action_children.values()
        children = sorted(children, key= lambda c: c.q_val(), reverse=True)
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
        best_action_child = max(node.action_children.items(), key= lambda (action, child): child.ucb_val())
        return best_action_child

    """
    action child with highest win rate (to be returned from uct search)
    returns (action, node) - (action, child node) with highest win rate
    """
    def wr_action_child(self, node):
        best_action_child = max(node.action_children.items(), key= lambda (action, child): child.q_val())
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
        index = np.random.randint(len(self.all_actions))
        rand_action = list(self.all_actions)[index]
        return rand_action

    """
    rm: bool - whether or not to remove the random action from untried_actions
    returns action - a random action from untried_actions
    """
    def rand_untried_action(self, rm=False):
        index = np.random.randint(len(self.untried_actions))
        rand_untried_action = list(self.untried_actions)[index]
        if rm:
            self.untried_actions.remove(rand_untried_action)
        return rand_untried_action

    def ucb_val(self):
        c = 2
        return float(self.losses)/self.visits + c*sqrt(2*log(self.parent.visits)/self.visits)

    def q_val(self):
        return float(self.losses)/self.visits
