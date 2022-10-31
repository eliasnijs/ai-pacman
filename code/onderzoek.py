import numpy as np

import gym
from gym import spaces

from pacman.pacman import *

class pacmanEnv(gym.Env):

    metadata = {'render.modes': ['ascii', 'basic']}

    TOP = 0
    LEFT = 1
    BOTTOM = 2
    RIGHT = 3

    def __init__(self, map="pacman/maps/map.txt", stdscr=None):
        super(pacmanEnv, self).__init__()
        self.stdscr = stdscr 
        self.game = new_game(map)
        self.action_space = spaces.Discrete(4)
        nm_ghosts = len(self.game.ghosts)
        #observation: power time, combo, score, pellet count, pacman x, pacman y, [ghost x y dx dy], [[tile]]
        low = np.array(
            [0,0,0,0,0,0] + [0,0,-10,-1]*len(self.game.ghosts) + [0]*len(self.game.tiles)*len(self.game.tiles[0]))
        high = np.array(
            [
                POWERTIMER, 3200, np.inf, 
                len(self.game.tiles)*len(self.game.tiles[0]), 
                len(self.game.tiles[0]), len(self.game.tiles)]+            
            [   len(self.game.tiles[0]), len(self.game.tiles),1,1]*len(self.game.ghosts)+
            [3]*len(self.game.tiles)*len(self.game.tiles[0])
            )
        shape = (len(low),)
        self.observation_space = spaces.Box(low,high,shape)

    def step(self, action):
        reward = self.game.score
        kb_key(self.game.controller.up, action == self.TOP)
        kb_key(self.game.controller.left, action == self.LEFT)
        kb_key(self.game.controller.down, action == self.BOTTOM)
        kb_key(self.game.controller.right, action == self.RIGHT)
        game_update(self.game)
        reward = self.game.score - reward
        return np.array([self.game.powertime]), reward, self.game.pelletcount == 0 
    
    def reset(self,map="pacman/maps/map.txt"):
        game = new_game(map)

    def render(self, mode='basic'):
        if mode == 'ascii':
            # will not work in notebooks :(
            if self.stdscr == None:
                raise ValueError
            game_render(self.stdscr, self.game) 
        elif mode == 'basic':
            print(f"game = [pacman: ({self.game.pacman.pos.x},{self.game.pacman.pos.y}), [", end="")
            for i,g in enumerate(self.game.ghosts):
                print(f"ghost {i}: ({g.body.pos.x},{g.body.pos.y}), ", end="")
            print("]")
        else:
            raise NotImplementedError()

 
    def close(self):
        pass