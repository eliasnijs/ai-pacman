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
	- learning rate
	- number of steps
	- batch size
	- number of epochs
	- gamma
	- gae lambda
	- clip range
	- normalize advantage
	- vf coefficients
	- max grad norm
	- use sde
	- sde sample freq		sample a new noise matrix every n steps
					when  using gSDE
					(default = -1)

  https://stable-baselines3.readthedocs.io/en/master/modules/ppo.htm

"""

"""
Configure Policy

- At the moment we are using Proximal Policy Optimization... see the following
	paper

"""

pacman_env = PacmanEnvironment_v1(pacmanmap="pacman/maps/lv1.txt")
model = PPO(
    "MlpPolicy",
    pacman_env,
    learning_rate       = 0.0005,
    n_steps             = 2048,
    batch_size          = 2,
    n_epochs            = 4,
    gamma               = 0.995,
    gae_lambda          = 0.96,
    clip_range          = 0.2,
    normalize_advantage = True,
    ent_coef            = 0.05,
    vf_coef             = 0.5,
    max_grad_norm       = 0.5,
    use_sde             = False,
    sde_sample_freq     = -1,
    device              = 'auto',
    verbose             = 1,
    )


"""
Learn
"""
________________________________________________________________________________
model.learn(total_timesteps=4096*16, progress_bar=True)

"""
Show Result
"""
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

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Start Program
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# NOTE(Elias): start the program
if __name__ == "__main__":
    curses.wrapper(show)
