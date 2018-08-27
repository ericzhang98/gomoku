# State/action independent mcts

import numpy as np
from math import sqrt, log

from constants import *

"""
PureMCTS --
main mcts class
- root: Node - init with root state
- uct_search: action - best action from mcts
"""
class AlphaZeroMCTS:
    def __init__(self, root_state):
        self.root = Node(root_state, 999999999)
        # policy value function from pretrained model
        from gomoku_state import GRID_LEN
        from policy_value_net_numpy import PolicyValueNetNumpy
        if GRID_LEN == 6:
            model_file = 'best_policy_6_6_4.model'
        else:
            model_file = 'best_policy_8_8_5.model'
        import pickle
        policy_params = pickle.load(open(model_file, 'rb'))
        nn = PolicyValueNetNumpy(GRID_LEN, GRID_LEN, policy_params)
        self.policy_value_fn = nn.policy_value_fn

        # print "AlphaZeroMCTS init. Current state value:", self.value_policy(root_state)

    """
    main algo loop
    returns action - action sampled according to policy vector
    """
    def uct_search(self):

        counter = 0
        while counter < THINK_TIME:
            counter += 1

            # tree policy (choosing leaf node) is the same
            node_to_eval = self.tree_policy(self.root)

            # value policy returns score if game ended otherwise uses nn to evaluate
            if node_to_eval.terminal:
                # value should always be -1 since the the current player of a terminal node has just lost
                value = 1 if node_to_eval.state.curr_player == node_to_eval.state.winning_player else -1
            else:
                # value = 0.1 if node_to_eval.state.curr_player == self.rollout(node_to_eval) else -0.1
                value = self.value_policy(node_to_eval.state)

            self.backup(node_to_eval, value)

            PRINT_SEARCH_LEADER = False
            if PRINT_SEARCH_LEADER:
                if counter % 100 == 0:
                    print "Child leader while running search---"
                    actions, probs = self.action_probs(self.root)
                    action_probs = dict(zip(actions, probs))
                    children = self.root.action_children.values()
                    best = max(children, key= lambda c: c.visits)
                    print("best ac so far: {}, Visits: {} Qval: {} Prior: {}".format(best.state.prev_move, best.visits, -best.q_val(), -best.prior))

        PRINT_PRIORS = False
        if PRINT_PRIORS:
            print "Priors---"
            value, value_action_probs = self.value_policy(self.root.state, action_probs=True)
            for a in sorted(value_action_probs, key=value_action_probs.get, reverse=True):
                print("Action: {} Prior: {}".format(a, value_action_probs[a]))

        PRINT_CHILD_STATS = True
        if PRINT_CHILD_STATS:
            print "Child stats---"
            children = self.root.action_children.values()
            children = sorted(children, key= lambda c: c.visits, reverse=True)
            for child in children:
                print("Action: {}, Visits: {} Qval: {} Prior: {}".format(child.state.prev_move, child.visits, -child.q_val(), -child.prior))

        actions, probs = self.action_probs(self.root)
        if DIRICHLET_NOISE:
            dirichlet = np.random.dirichlet(0.3 * np.ones(len(probs)))
            idx = np.random.choice(len(actions), p=(0.75*probs + 0.25*dirichlet))
        else:
            idx = np.random.choice(len(actions), p=probs)

        action = actions[idx]
        return action

    """
    explores using ucb and chooses node to simulate
    returns node - node to simulate
    """
    def tree_policy(self, node):
        while not node.terminal:
            # ucb val is technically inf
            if not node.fully_expanded():
                self.expand_all(node)
                return node
            else:
                action, child = self.ucb_action_child(node)
                node = child
        return node

    """
    fully expand node with priors from value_policy
    modifies: node.untried_actions, node.action_children
    returns nothing
    """
    def expand_all(self, node):
        node.untried_actions = set()
        value, value_action_probs = self.value_policy(node.state, action_probs=True)
        for action in node.all_actions:
            # make child node with next state + add edges
            next_state = node.state.apply_action(action)
            child_node = Node(next_state, -value_action_probs[action])
            child_node.parent = node
            node.action_children[action] = child_node

    """
    ucb
    returns (action, node) - ucb optimal (action, child node) to explore
    """
    def ucb_action_child(self, node):
        best_action_child = max(node.action_children.items(), key= lambda (action, child): -child.ucb_val())
        return best_action_child

    """
    returns ([action], [float]) - policy vector for given node
    """
    def action_probs(self, node, temp=0):
        actions = list(node.state.possible_actions())
        visits = map(lambda action: node.action_children[action].visits, actions)

        if node.state.possible_actions() != set(node.action_children.keys()):
            print "err: possible actions don't match action_children"
            print node.state.possible_actions()
            print node.action_children.keys()

        if temp == 0:
            best = np.argmax(visits)
            probs = np.zeros(len(actions))
            probs[best] = 1
        else:
            def softmax(x):
                probs = np.exp(x - np.max(x))
                probs /= np.sum(probs)
                return probs
            probs = softmax(1.0/temp * np.log(np.array(visits) + 1e-10))

        return actions, probs

    """
    random simulation until a player wins
    returns player - winning player
    """
    def rollout(self, node):
        while not node.terminal:
            rand_action = node.rand_action()
            next_state = node.state.apply_action(rand_action)
            node = Node(next_state, 99999999999)
        return node.state.winning_player

    """
    value of the state (from the perspective of curr player) according to nn
    returns float - value
    or (float, action -> float) - (value, action probability vector)
    """
    def value_policy(self, state, action_probs=False):
        # return 0
        from gomoku_state import NNBoardState
        nn_board_state = NNBoardState(state)
        act_probs, value = self.policy_value_fn(nn_board_state)
        if action_probs:
            return value, dict(act_probs)
        return value

    """
    updates visits and wins count according to winning_player and reward function
    returns nothing
    """
    def backup(self, node, reward):
        while node is not None:
            node.visits += 1
            node.value += reward
            reward = -reward
            node = node.parent


"""
Node --
keeps track of state, actions, and stats info of the state
- state: state
- terminal: bool - directly corresponds to state.terminal
- parent: Node
- action_children: dict - maps: action -> child node
- all_actions: set - const set of actions
- untried_actions: set - set of untried actions
- fully_expanded() -> bool
- rand_action() -> action
- rand_untried_action() -> action
"""
class Node:
    def __init__(self, state, prior):
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
        self.value = 0

        self.prior = prior

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
        c = 5
        # return float(self.losses)/self.visits + c*sqrt(2*log(self.parent.visits)/self.visits)
        return self.q_val() + c*self.prior*sqrt(self.parent.visits)/(1+self.visits)

    def q_val(self):
        return float(self.value)/self.visits if self.visits > 0 else 0
