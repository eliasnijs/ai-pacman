import numpy as np

import gym
from gym import spaces

from pacman.pacman import *
    
def strtile_to_inttile(char):
    if char == TILES.EMPTY.value:
        return 0 
    elif char == TILES.WALL.value:
        return 1 
    elif char == TILES.PELLET.value:
        return 2 
    elif char == TILES.POWER.value:
        return 3 
    else:
        raise ValueError(char)

def strtiles_to_inttiles(tiles):
    return [strtile_to_inttile(char) for char in np.array(tiles).flatten()]

def ghosts_to_ghostarr(ghosts):
    return np.array([ np.array([
        ghost.body.pos.x, ghost.body.pos.y, 
        ghost.body.dir.x, ghost.body.dir.y, 
        ghost.killable, ghost.deathtime
        ]) for ghost in ghosts ]).flatten().tolist()

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
        
        nr_ghosts = len(self.game.ghosts)

        # GROOT BAVO MOMENT XD
        # observation: power time, combo, score, pellet count, pacman x, pacman y, [ghost x y dx dy killable deathtime], [[tile]]
        self.low = np.array([0,0,0,0,0,0] + [0,0,-1,-1, False, 0]*len(self.game.ghosts) + [0]*len(self.game.tiles)*len(self.game.tiles[0]))
        self.high = np.array(
            [
                POWERTIMER, 3200, np.inf, 
                len(self.game.tiles)*len(self.game.tiles[0]), 
                len(self.game.tiles[0]), len(self.game.tiles)]+            
            [   len(self.game.tiles[0]), len(self.game.tiles),1,1,1,GHOSTRESPAWN]*len(self.game.ghosts)+
            [3]*len(self.game.tiles)*len(self.game.tiles[0])
            )
        shape = (len(self.low),)
        self.observation_space = spaces.Box(self.low, self.high, shape, dtype=np.float64)

    def step(self, action):
        reward = self.game.score
        kb_key(self.game.controller.up, action == self.TOP)
        kb_key(self.game.controller.left, action == self.LEFT)
        kb_key(self.game.controller.down, action == self.BOTTOM)
        kb_key(self.game.controller.right, action == self.RIGHT)
        game_update(self.game)
        reward = pow((self.game.score - reward),2)
        
        tilearr = strtiles_to_inttiles(self.game.tiles)
        statarr = [self.game.powertime, self.game.combo, self.game.score, self.game.pelletcount]
        ghostarr = ghosts_to_ghostarr(self.game.ghosts)
        gamearr = np.array(statarr + [self.game.pacman.pos.x, self.game.pacman.pos.y] + ghostarr + tilearr)
        if not self.game.running:
            reward = -1000.0

        return gamearr, reward, self.game.pelletcount == 0 or not self.game.running, {}


    def reset(self,map="pacman/maps/map.txt"):
        self.game = new_game(map)
        tilearr = strtiles_to_inttiles(self.game.tiles)
        statarr = [self.game.powertime, self.game.combo, self.game.score, self.game.pelletcount]
        ghostarr = ghosts_to_ghostarr(self.game.ghosts)
        gamearr = np.array(statarr + [self.game.pacman.pos.x, self.game.pacman.pos.y] + ghostarr + tilearr)
        
        return gamearr

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

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.utils import set_random_seed

env = pacmanEnv()
model = PPO("MlpPolicy", env, verbose=1, n_steps=4096)
model.learn(total_timesteps=1000)

def show(stdscr):
    env.stdscr = stdscr
    stdscr.addstr(0,0,"press q to stop or any other key to continue...")
    key = stdscr.getch()
    while(key != "q"):
        obs = env.reset()
        for _ in range(10000):
            action, _states = model.predict(obs)
            obs, rewards, dones, info = env.step(action)
            env.render(mode='ascii')
        stdscr.addstr(0,0,"press q to stop or any other key to continue...")
        key

# NOTE(Elias): start the program
if __name__ == "__main__":
    curses.wrapper(show)