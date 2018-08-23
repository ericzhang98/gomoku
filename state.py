"""
State interface:
- curr_player: player - player that is going to make a move on the current state
- terminal: bool - whether or not a player has won the game (must be correct on init)
- winning_player: player - (must be non null if terminal == true)

- possible_actions() -> set - non-empty set of possible actions (called by Node at init to init untried_actions)
- apply_action(action) -> state - next state (should not modify the state)

action: some hashable property used by apply_action to create a new next state
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