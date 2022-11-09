from pacman_gymenv_v1 import *
from stable_baselines3.common.env_checker import check_env


pacman_env = PacmanEnvironment_v1()
pacman_env.reset()

check_env(pacman_env, warn=True)




