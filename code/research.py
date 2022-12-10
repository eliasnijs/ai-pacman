from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.env_checker import check_env

from pacman_gymenv_v1 import *

def show(stdscr, fps):
	pacman_env.screen = stdscr
	stdscr.addstr(0,0,"press q to stop or any other key to continue...")
	key = stdscr.getch()
	while(key != "q"):
		obs = pacman_env.reset()
		finished = False
		i = 0
		while i < 1000 and not finished:
			start_t = time.perf_counter_ns()
			action, _states = model.predict(obs)
			obs, rewards, finished, info = pacman_env.step(action)
			pacman_env.render(mode='human')
			wait_t = 10e9/fps - (time.perf_counter_ns() - start_t)
			if (wait_t > 0):
				time.sleep(wait_t/10e9)

if __name__ == "__main__":
	# Optuna
	n_cpu = 6
	pacman_env = PacmanEnvironment_v1(pacmanmap="pacman/maps/lv5.txt")
	# check_env(pacman_env)
	env = SubprocVecEnv([lambda: pacman_env for i in range(n_cpu)])
	model = PPO(
		"MlpPolicy",
		env,
		learning_rate       = 0.0003,
		n_steps             = 512,
		batch_size          = 128,
		n_epochs            = 32,
		gamma               = 0.99,
		gae_lambda          = 0.9,
		clip_range          = 0.4,
		normalize_advantage = True,
		ent_coef            = 0.0,	# default
		vf_coef             = 0.5,	# default
		max_grad_norm       = 0.5,	# default
		device              = 'auto',	# default
		verbose             = 1,
		seed		    = 0
	    )
	model.learn(total_timesteps=4096, progress_bar=True)
	curses.wrapper(show, 8)
