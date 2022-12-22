from collections import deque
import numpy as np
import random

import gym
from gym import spaces

from pacman.pacman import *

class PacmanEnvironment(gym.Env):
	metadata = {'render.modes': ['human']}

	ACTION_UP= 0
	ACTION_DOWN  = 1
	ACTION_LEFT  = 2
	ACTION_RIGHT = 3

	def set_random_start_pos(self):
		x = random.randint(0, self.game.w - 1)
		y = random.randint(0, self.game.h - 1)
		while (not (self.game.tiles[y][x] == TILES.EMPTY.value or
	      self.game.tiles[y][x] == TILES.PELLET.value)):
			x = random.randint(0, self.game.w - 1)
			y = random.randint(0, self.game.h - 1)
			self.game.pacman.pos.x = x
			self.game.pacman.pos.y = y

	# returns the observation space corresponding with the game of the
	# environment
	def get_observation(self):
		pacman_data = np.array([self.game.pacman.pos.x, self.game.pacman.pos.y])
		ghost_data = np.zeros(len(self.game.ghosts)*2)
		for i,ghost in enumerate(self.game.ghosts):
			ghost_data[i*2] = ghost.body.pos.x
			ghost_data[i*2 + 1] = ghost.body.pos.y
		map_data = np.array(self.game.tiles).flatten()
		return np.concatenate((pacman_data, ghost_data, map_data))


	# (nessecary gym function)
	def __init__(self, screen=None, pacmanmap="pacman/maps/lv1.txt"):
		super(PacmanEnvironment, self).__init__();
		self.screen = screen
		self.map = pacmanmap
		self.game = new_game(self.map)

		para_cnt_total = (2 + len(self.game.ghosts)*2
		    + self.game.h * self.game.w)

		self.action_space = spaces.Discrete(4)
		self.observation_space = spaces.Box(low=-256, high=256,
				      shape=(para_cnt_total,), dtype=np.float64)

	# (nessecary gym function)
	def step(self, action):
		kb_key(self.game.controller.up,	   action == self.ACTION_UP)
		kb_key(self.game.controller.left,  action == self.ACTION_LEFT)
		kb_key(self.game.controller.down,  action == self.ACTION_DOWN)
		kb_key(self.game.controller.right, action == self.ACTION_RIGHT)

		prev_score = self.game.score
		game_update(self.game)

		self.observation = self.get_observation()
		self.is_done = (not self.game.running or self.game.pelletcount == 0)

		self.reward = self.game.score - prev_score
		if self.is_done and self.game.pelletcount != 0:
			self.reward = -200.0
		elif self.is_done and self.game.pelletcount == 0:
			self.reward = 200.0

		self.info = {}
		return self.observation, self.reward, self.is_done, self.info

	# (nessecary gym function)
	def reset(self):
		self.game = new_game(self.map)
		#self.set_random_start_pos()
		self.observation = self.get_observation()
		return self.observation

	# (nessecary gym function)
	def render(self, mode='human'):
		if mode == 'human':
			assert(self.screen != None)
			game_render(self.screen, self.game)
		else:
			raise NotImplementedError()

