import matplotlib.pyplot as plt
import curses
import time

from stable_baselines3 import PPO
from stable_baselines3 import A2C
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor

import optuna

from pacman_gymenv_v1 import PacmanEnvironment_v1

# _____________________________________________________________________________
# Configuration

# General configuration
MAP			= "pacman/maps/lv2.txt"
FPS			= 8
N_CPU			= 8
POLICY			= "MlpPolicy"
POLICY_CONFIG		= {"layers": [64, 64]}

# Optuna hyperparameter tuning configuration for PPO
#			   lower-bound, upper-bound
TUNING_HORIZON		= [32,		5000		]
TUNING_MINIBATCH_RANGE	= [4,		4096		]
TUNING_EPOCHS		= [3,		30		]
TUNING_CLIP_RANGE	= [0.1,		0.3		]
TUNING_GAMMA		= [0.8,		0.9997		]
TUNING_GAE		= [0.9,		1.0		]
TUNING_VF		= [0.5,		1.0		]
TUNING_EF		= [0.0,		0.01		]
TUNING_LEARNINGRATE	= [5e-6,	0.003		]

TUNING_STEPS		= 64
TUNING_TIMESTEPS	= 4096*2

# Final training configuration
MODEL_TIMESTEPS		= 4096*32*8

# Environment configuration
PACMAN_ENV = PacmanEnvironment_v1(pacmanmap=MAP)

# _____________________________________________________________________________
# The Program

def show(stdscr, model):

	f = open("run_results.txt", "w")

	stdscr.addstr(0,0,"press q to stop or any other key to continue...")
	pacmanenv = PACMAN_ENV
	pacmanenv.screen = stdscr
	key = stdscr.getch()
	count = 0
	while key != "q" and count < 1000:
		obs = pacmanenv.reset()
		finished = False
		framecnt = 0
		while not finished:
			framecnt += 1
			start_t = time.perf_counter_ns()
			action, _states = model.predict(obs)
			obs, rewards, finished, info = pacmanenv.step(action)
			# pacmanenv.render(mode='human')
			# wait_t = 10e9/FPS - (time.perf_counter_ns() - start_t)
			# if (wait_t > 0):
			# 	time.sleep(wait_t/10e9)
		f.write(f"{pacmanenv.game.pelletcount==0}, {pacmanenv.game.score}, {framecnt}\n")
		count += 1
	f.close()


def objective_ppo(trial):
	verbose		= 0
	seed		= 0
	# n_steps	= trial.suggest_int(	'n_steps',		TUNING_HORIZON[0],		TUNING_HORIZON[1])
	# batch_size	= trial.suggest_int(	'batch_size',		TUNING_MINIBATCH_RANGE[0],	TUNING_MINIBATCH_RANGE[1])
	n_epochs	= trial.suggest_int(	'n_epochs',		TUNING_EPOCHS[0],		TUNING_EPOCHS[1])
	clip_range	= trial.suggest_float(	'clip_range',		TUNING_CLIP_RANGE[0],		TUNING_CLIP_RANGE[1]);
	gamma		= trial.suggest_float(	'gamma',		TUNING_GAMMA[0],		TUNING_GAMMA[1])
	# gae_labmda	= trial.suggest_float(	'gae_lambda',		TUNING_GAE[0],			TUNING_GAE[1])
	# vf_coef	= trial.suggest_float(	'vf_coef',		TUNING_VF[0],			TUNING_VF[1])
	ent_coef	= trial.suggest_float(	'ent_coef',		TUNING_EF[0],			TUNING_EF[1])
	learning_rate	= trial.suggest_float(	'learning_rate',	TUNING_LEARNINGRATE[0],		TUNING_LEARNINGRATE[1])

	env = SubprocVecEnv([lambda: Monitor(PACMAN_ENV) for i in range(N_CPU)])

	model = PPO(
		policy		= POLICY,
		env		= env,
		learning_rate	= learning_rate,
		# n_steps	= n_steps,
		# batch_size	= batch_size,
		n_epochs	= n_epochs,
		gamma		= gamma,
		# gae_lambda	= gae_labmda,
		clip_range	= clip_range,
		ent_coef	= ent_coef,
		# vf_coef	= vf_coef,
		verbose		= 0,
		seed		= 0,
		)
	model.learn(total_timesteps=TUNING_TIMESTEPS, progress_bar=True)

	reward_mean, _ = evaluate_policy(model, env)
	return reward_mean

if __name__ == "__main__":
	check_env(PACMAN_ENV)

	# Tuning of the hyperparameters using 'Optuna'
	study = optuna.create_study(direction="maximize")
	study.optimize(objective_ppo, n_trials=TUNING_STEPS,
		gc_after_trial=True)

	print("Best hyperparameters and mean reward:")
	print(study.best_params)
	print(study.best_value)

	f = open("optuna_results.txt", "w")
	f.write(str(study.best_params))
	f.close()

	# Use the parameters from optuna to train for a longer time and
	# visiualise the result
	env = SubprocVecEnv([lambda: Monitor(PACMAN_ENV) for i in range(N_CPU)])

	model = PPO(POLICY, env, **study.best_params)
	# model = PPO(POLICY, env, **study.best_params, policy_kwargs=POLICY_CONFIG)
	# model = PPO(
	# 	policy		= POLICY,
	# 	env		= env,
	# 	learning_rate	= 0.002622982854085486,
	# 	n_steps		= 3353,
	# 	batch_size	= 2709,
	# 	n_epochs	= 16,
	# 	gamma		= 0.9108135128614272,
	# 	gae_lambda	= 0.9560261925276281,
	# 	clip_range	= 0.2788429232908717,
	# 	ent_coef	= 0.0011322183051189843,
	# 	vf_coef		= 0.6358362206959556,
	# 	verbose		= 1,
	# 	seed		= 0,
	# 	)
	model.learn(MODEL_TIMESTEPS, progress_bar=True)
	reward_mean, _ = evaluate_policy(model, env)

	f = open("model_results.txt", "w")
	f.write(str(reward_mean))
	f.close()

	curses.wrapper(show, model)

