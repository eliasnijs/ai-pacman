from collections import deque
import numpy as np

import gym
from gym import spaces

from pacman.pacman import *

"""
Pacman Ai - The Environment - v1

This environment does not support eating ghosts. The challenge
here is to learn to eat pellets and to not get killed
by the ghosts.

The observation space:
- pacman.x, pacman.y, pacman.dx, pacman.dy
- for ghost in all ghosts: delta_ghost.x, delta_ghost.y, ghost.dx, ghost.dy
- pellet positions
"""

class PacmanEnvironment_v1(gym.Env):
    metadata = {'render.modes': ['human']}

    ACTION_UP    = 0
    ACTION_DOWN  = 1
    ACTION_LEFT  = 2
    ACTION_RIGHT = 3

    # returns the observation space corresponding with the game of the
    # environment
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
                    pellet_data.append(pacman_x - i)
                    pellet_data.append(pacman_y - j)

        while (len(pellet_data) < self.game.original_pelletcount*2):
            pellet_data.append(0)

        obs = [pacman_x, pacman_y] + ghost_data + pellet_data

        obs = np.array(obs)
        return obs

    # (nessecary gym function)
    def __init__(self, screen=None, pacmanmap="pacman/maps/lv1.txt"):
        super(PacmanEnvironment_v1, self).__init__();

        self.screen = screen
        self.map = pacmanmap

        game = new_game(self.map)
        para_cnt_pacman  = 2
        para_cnt_ghosts  = len(game.ghosts)*4
        para_cnt_pellets = game.original_pelletcount*2

        para_cnt_total   = para_cnt_pacman + para_cnt_ghosts + para_cnt_pellets

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=-1024, high=1024,
                                            shape=(para_cnt_total,),
					    dtype=np.float64)

    # (nessecary gym function)
    def step(self, action):
        kb_key(self.game.controller.up,    action == self.ACTION_UP)
        kb_key(self.game.controller.left,  action == self.ACTION_LEFT)
        kb_key(self.game.controller.down,  action == self.ACTION_DOWN)
        kb_key(self.game.controller.right, action == self.ACTION_RIGHT)

        prev_score = self.game.score
        game_update(self.game)

        self.observation = self.get_observation()
        self.is_done = not self.game.running or self.game.pelletcount == 0

        self.reward = self.game.score - prev_score
        if self.is_done and self.game.pelletcount != 0:
            self.reward = -10.0

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



