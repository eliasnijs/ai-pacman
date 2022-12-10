import matplotlib.pyplot as plt
import curses
import time

from stable_baselines3 import PPO
from stable_baselines3 import A2C
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor

# -----------------------------------------------------------------------------
# Configuration

# General configuration
N_CPU			= 4
MAP			= "pacman/maps/lv4.txt"
FPS			= 8

# Optuna hyperparameter tuning configuration
TUNING_LEARNINGRATE_LB	= 1e-5
TUNING_LEARNINGRATE_UB	= 1e-2
TUNING_EPOCHS_LB	= 1
TUNING_EPOCHS_UB	= 32
TUNING_GAMMA_LB		= 0.8
TUNING_GAMMA_UB		= 0.99
TUNING_ENTCOEF_LB	= 1e-5
TUNING_ENTCOEF_UB	= 1e-1

TUNING_STEPS		= 64
TUNING_TIMESTEPS	= 4096*2

# Final training configuration
MODEL_POLICY		= "MlpPolicy"
MODEL_TIMESTEPS		= 4096*32

# -----------------------------------------------------------------------------
# The Program

import optuna

from pacman_gymenv_v1 import PacmanEnvironment_v1

def show(stdscr, model, pacmanenv):
	stdscr.addstr(0,0,"press q to stop or any other key to continue...")
	pacmanenv.screen = stdscr
	key = stdscr.getch()
	while(key != "q"):
		obs = pacmanenv.reset()
		finished = False
		while not finished:
			start_t = time.perf_counter_ns()
			action, _states = model.predict(obs)
			obs, rewards, finished, info = pacmanenv.step(action)
			pacmanenv.render(mode='human')
			wait_t = 10e9/FPS - (time.perf_counter_ns() - start_t)
			if (wait_t > 0):
				time.sleep(wait_t/10e9)

def objective_ppo(trial):
	verbose		= 0
	seed		= 0

	learning_rate	= trial.suggest_float('learning_rate', TUNING_LEARNINGRATE_LB, TUNING_LEARNINGRATE_LB)
	n_epochs	= trial.suggest_int('n_epochs', TUNING_EPOCHS_LB, TUNING_EPOCHS_UB)
	gamma		= trial.suggest_float('gamma', TUNING_GAMMA_LB, TUNING_GAMMA_UB)
	ent_coef	= trial.suggest_float('ent_coef', TUNING_ENTCOEF_LB, TUNING_ENTCOEF_UB)

	pacmanenv = PacmanEnvironment_v1(pacmanmap=MAP)
	env = SubprocVecEnv([lambda: Monitor(pacmanenv) for i in range(N_CPU)])

	model = PPO(MODEL_POLICY, env, learning_rate=learning_rate,
	     ent_coef=ent_coef, gamma=gamma, n_epochs=n_epochs,
	     verbose = verbose, seed = seed)
	model.learn(total_timesteps=TUNING_TIMESTEPS, progress_bar=True)

	reward_mean, _ = evaluate_policy(model, env)
	return reward_mean


if __name__ == "__main__":
	# Tuning of the hyperparameters using 'Optuna'
	study = optuna.create_study(direction="maximize")
	study.optimize(objective_ppo, n_trials=TUNING_STEPS)

	print("Best hyperparameters and mean reward:")
	print(study.best_params)
	print(study.best_value)

	# Use the parameters from optuna to train for a longer time and
	# visiualise the result
	pacmanenv = PacmanEnvironment_v1(pacmanmap=MAP)
	env = SubprocVecEnv([lambda: Monitor(pacmanenv) for i in range(N_CPU)])

	model = PPO(MODEL_POLICY, env, **study.best_params)
	model.learn(MODEL_TIMESTEPS, progress_bar=True)

	curses.wrapper(show, model, pacmanenv)
