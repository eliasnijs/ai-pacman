from pacman_gymenv_v1 import *

# from stable_baselines3.common.env_checker import check_env
# pacman_env = PacmanEnvironment_v1()
# check_env(pacman_env)

from stable_baselines3 import PPO

"""
PARAMETERS

Environment
- observation space:
	v1:	pacman: pacman.x, pacman.y, pacman.dx, pacman.dy
		ghosts: delta_ghost.x, delta_ghost.dy, ghost.dx, ghost.dy
		other:	pellet positions
- reward function:
	v1:	difference between current score previous score
		-10.0 if we lost

Policy Parameters
- Proximal Policy Optimization (PPO):
	Hyperparameters:
	- learning rate
	- number of steps
	- batch size
	- number of epochs
	- gamma
	- gae lambda
	- clip range
	- normalize advantage
		-
	- ent coefficients
		- entropy coefficient for the loss calculation
	- vf coefficients
		- value function coefficient for the loss calculation
	- max grad norm
		- the maximum value for gradient clipping
		- gradient clipping rescales the gradient as soon as it gets too
		  large.
		- default = 0.5

  https://stable-baselines3.readthedocs.io/en/master/modules/ppo.htm

"""

# Optuna

pacman_env = PacmanEnvironment_v1(pacmanmap="pacman/maps/lv3.txt")
model = PPO(
	"MlpPolicy",
    	pacman_env,
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


"""
Learn
"""

model.learn(total_timesteps=4096*32*4, progress_bar=True)

FPS=6
def show(stdscr):
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
            wait_t = 10e9/FPS - (time.perf_counter_ns() - start_t)
            if (wait_t > 0):
                time.sleep(wait_t/10e9)

        # stdscr.addstr(0,0,"press q to stop or any other key to continue...")
        # key = stdscr.getch()

# NOTE(Elias): start the program
if __name__ == "__main__":
    curses.wrapper(show)
