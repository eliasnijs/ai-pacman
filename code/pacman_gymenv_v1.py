from collections import deque
import numpy as np

import gym
from gym import spaces

from pacman.pacman import *

"""
Pacman Ai - The Environment - v1

This environment does not support eating ghosts. The challenge
here is to learn to eat pellets to increase and to not get killed
by the ghosts.

The observation space:
- pacman.x, pacman.y, pacman.dx, pacman.dy
- for ghost in all ghosts: delta_ghost.x, delta_ghost.y, ghost.dx, ghost.dy
- pellet positions
- previous actions (last 30)
"""

PACMAN_MOV_MEM_AMOUNT = 64

class PacmanEnvironment_v1(gym.Env):
    metadata = {'render.modes': ['human']}

    ACTION_UP    = 0
    ACTION_DOWN  = 0
    ACTION_LEFT  = 0
    ACTION_RIGHT = 0

    def get_observation(self):
        pacman_x = self.game.pacman.pos.x
        pacman_y = self.game.pacman.pos.y

        ghost_data = []
        for ghost in self.game.ghosts:
            ghost_data.append(pacman_x - ghost.body.pos.x)
            ghost_data.append(pacman_y - ghost.body.pos.y)
            ghost_data.append(ghost.body.dir.x)
            ghost_data.append(ghost.body.dir.y)

        pellet_data = []
        for i,row in enumerate(self.game.tiles):
            for j,cell in enumerate(row):
                if cell == '·':
                    pellet_data.append(i)
                    pellet_data.append(j)

        self.previous_actions = deque(maxlen=PACMAN_MOV_MEM_AMOUNT)
        for _ in range(PACMAN_MOV_MEM_AMOUNT):
            self.previous_actions.append(-1)

        obs = [pacman_x, pacman_y] + ghost_data + pellet_data + list(self.previous_actions)
        obs = np.array(obs)
        print(len(obs))
        print(obs.shape)
        return obs

    # (nessecary gym function)
    def __init__(self, screen=None, pacmanmap="pacman/maps/lv2.txt"):
        super(PacmanEnvironment_v1, self).__init__();

        self.screen = screen
        self.map = pacmanmap

        game = new_game(self.map)

        para_cnt_pacman  = 2
        para_cnt_ghosts  = len(game.ghosts)*4
        para_cnt_pellets = len(list(filter(lambda tile: tile == '·', np.array(game.tiles).flatten())))
        para_cnt_memory  = PACMAN_MOV_MEM_AMOUNT
        para_cnt_total   = para_cnt_pacman + para_cnt_ghosts + para_cnt_pellets + para_cnt_memory

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=-1024, high=1024,
                                            shape=(para_cnt_total,), dtype=np.float32)

    # (nessecary gym function)
    def step(self, action):
        self.previous_actions.append(action) # store action in observation space memory

        kb_key(self.game.controller.up,    action == self.ACTION_UP)
        kb_key(self.game.controller.left,  action == self.ACTION_LEFT)
        kb_key(self.game.controller.down,  action == self.ACTION_DOWN)
        kb_key(self.game.controller.right, action == self.ACTION_RIGHT)

        game_update(self.game)

        self.observation = self.get_observation();
        self.is_done = self.game.pelletcount == 0 or not self.game.running

        self.reward = self.game.score
        if self.is_done and self.game.pellet != 0:
            self.reward = -10

        self.info = {}
        return self.observation, self.reward, self.is_done, self.info

    # (nessecary gym function)
    def reset(self):
        self.game = new_game(self.map)
        self.observation = self.get_observation();
        return self.observation

    # (nessecary gym function)
    def render(self, mode='human'):
        if mode == 'human':
            assert(self.screen != None)
            game_render(self.screen, self.game)
        else:
            raise NotImplementedError()



