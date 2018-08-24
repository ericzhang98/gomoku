# State/action independent mcts

import numpy as np
from math import sqrt, log

THINK_TIME = 2000
SELF_PLAY = False

"""
PureMCTS --
main mcts class
- root: Node - init with root state
- uct_search: action - best action from mcts
"""
class AlphaZeroMCTS:
    def __init__(self, root_state):
        self.root = Node(root_state, 999999999)

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
                value = 1 if node_to_eval.state.curr_player == node_to_eval.state.winning_player else -1
            else:
                winning_player = self.rollout(node_to_eval)
                value = 0.1 if node_to_eval.state.curr_player == winning_player else -0.1

            self.backup(node_to_eval, value)

            # print child stats
            if counter % 100 == 0:
                actions, probs = self.action_probs(self.root)
                action_probs = dict(zip(actions, probs))
                children = self.root.action_children.values()
                best = max(children, key= lambda c: c.visits)
                print("best ac so far: {}, Visits: {} Qval: {}".format(best.state.prev_move, best.visits, -best.q_val()))

        actions, probs = self.action_probs(self.root)
        action_probs = dict(zip(actions, probs))

        # print child stats
        children = self.root.action_children.values()
        children = sorted(children, key= lambda c: c.visits, reverse=True)
        for child in children:
            print("Action: {}, Visits: {} Qval: {}".format(child.state.prev_move, child.visits, -child.q_val()))

        if SELF_PLAY:
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
        child_node = Node(next_state, self.value_policy(next_state))
        child_node.parent = node
        node.action_children[rand_untried_action] = child_node
        return child_node

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

    def value_policy(self, node):
        return 0

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
- full_expanded() -> bool
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
        c = 2
        # return float(self.losses)/self.visits + c*sqrt(2*log(self.parent.visits)/self.visits)
        return self.q_val() + c*self.prior*sqrt(self.parent.visits)/(1+self.visits)

    def q_val(self):
        return float(self.value)/self.visits
