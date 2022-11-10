from pacman_gymenv_v1 import *

# from stable_baselines3.common.env_checker import check_env
# pacman_env = PacmanEnvironment_v1()
# check_env(pacman_env)

from stable_baselines3 import PPO

pacman_env = PacmanEnvironment_v1()
model = PPO("MlpPolicy", pacman_env, verbose=1)
model.learn(total_timesteps=4096*16*16, progress_bar=True)

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
