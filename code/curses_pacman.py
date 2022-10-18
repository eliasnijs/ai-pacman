import curses
import time

from base import *
from pacman_h import *
from pacman import *

FPS = 6

# ==============================================================
# NOTE(Elias): Keyboard

def kb_getqueue(w) -> list[int]:
    keys = [] 
    key_next = w.getch()
    while (key_next != -1):
        keys.append(key_next)
        key_next = w.getch()
    return keys

def kb_key(button:Button, newstate:bool):
    button.wasdown = button.isdown
    button.isdown = newstate 

def handleinput(game:Game, keys:list[int]) -> None:
    kb_key(game.controller.up, ord('w') in keys)
    kb_key(game.controller.right, ord('d') in keys)
    kb_key(game.controller.down, ord('s') in keys)
    kb_key(game.controller.left, ord('a') in keys)

# =======================================================
# NOTE(Elias): Main

def pacman(stdscr) -> None:

    # NOTE(Elias): initialisation
    
    stdscr.nodelay(True) # NOTE(Elias): configure curses keyboard input
    
    tiles, pacman, ghosts = loadmap("maps/map.txt")
    controller = Controller(Button(False, False), Button(False, False), Button(False, False), Button(False, False))
    game:Game = Game(True, controller, 0, 0, 0, len(tiles[0]), len(tiles), tiles, pacman, ghosts)


    # NOTE(Elias): running 
    while game.running:
        start_t = time.perf_counter_ns()

        keys = kb_getqueue(stdscr)
        if ord('q') in keys:
            break
        handleinput(game, keys)

        game_update(game)
        game_render(stdscr, game)
        
        end_t = time.perf_counter_ns()
        wait_t = (1/FPS)*10e9 - (end_t - start_t)
        if (wait_t > 0):
            # NOTE(Elias): Is sleep the correct way of doing this?
            # There might be a problem with interrupt signals?
            time.sleep(wait_t / 10e9)

curses.wrapper(pacman)