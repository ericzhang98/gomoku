Gomoku with AlphaZero style MCTS

Looking into the MCTS techniques used by Deepmind in AlphaZero and some potentially cool constraint solving stuff to add in.

Run `python gomoku.py` to start up the game. Edit `GRID_LEN` in `constants.py` to change the game type between 6x6 and 8x8.

`pure_mcts.py` and `alphazero_mcts.py` are the main files providing game-independent monte carlo tree search (can be applied to any game implementing the State interface in `state.py`). Currently using the pretrained models and the network architecture from [https://github.com/junxiaosong/AlphaZero_Gomoku/blob/master/policy_value_net_numpy.py](https://github.com/junxiaosong/AlphaZero_Gomoku/blob/master/policy_value_net_numpy.py) as the alpha zero style value network since the details seem complicated. Will take a further look into the architecture to fully understand it and see if improvements can be made.
