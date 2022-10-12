from dataclasses import dataclass
from enum import Enum
from random import randint
import time

import curses as c

# ======================================================= #
"""
TODO(Elias):
- detect keystrokes with nc
- render with nc
- normal food stuff
- power pellets
- more advanced map loading (for example map positions)

NOTE(Elias):
Resources:
- pacman in c:
    https://github.com/MarquisdeGeek/pacman/tree/master/src
- nc examples: 
    https://github.com/zephyrproject-rtos/windows-c/tree/master/examples
- ghost mechanics:
    https://youtu.be/ataGotQ7ir8
"""

# ======================================================= #
# NOTE(Elias): Base Structs 

@dataclass
class vec2:
    x:int
    y:int
    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)

# ======================================================= #
# NOTE(Elias): Game Structs 

@dataclass
class Body:
    pos:vec2
    dir:vec2

@dataclass
class Ghost:
    body:Body
    color:int

@dataclass
class Game:
    running:bool
    score:int
    w:int
    h:int
    tiles:list[str]
    pacman:Body
    ghosts:list[Ghost]

class Tiles(Enum):
    EMPTY:str = ' '
    WALL:str = '#'

# ======================================================= #
# NOTE(Elias): Base Functions

def clamp(lb, v, ub):
    return min(max(lb, v), ub)

# =======================================================
# NOTE(Elias): c Helper Functions

def set_color(win, fg, bg):
    if c.has_colors():
        n = fg + 1
        c.init_pair(n, fg, bg)
        win.attroff(c.A_COLOR)
        win.attron(c.color_pair(n))

def unset_color(win):
    if c.has_colors():
        win.attrset(c.color_pair(0))

# =======================================================
# NOTE(Elias): Helper Functions

def loadmap(path:str) -> list[list[str]]:
    return [ list(row) for row in open(path, "r").read().splitlines() ]

def rand_dir() -> vec2:
    poss = [vec2(  0,  1), vec2(  1,  0), vec2(  0, -1), vec2( -1,  0)]
    return poss[randint(0, 3)]

# =======================================================
# NOTE(Elias): Game
    
def game_update(game:Game) -> None:
    pn = game.pacman.pos + game.pacman.dir
    if game.tiles[pn.y][pn.x] == Tiles.EMPTY.value:
        game.pacman.pos = pn

    for ghost in game.ghosts:
        pn = ghost.body.pos + ghost.body.dir
        while game.tiles[pn.y][pn.x] != Tiles.EMPTY.value:
            ghost.body.dir = rand_dir()
            pn = ghost.body.pos + ghost.body.dir
        ghost.body.pos = pn 
        if ghost.body.pos == game.pacman.pos:
            game.running = False 

def game_render(stdscr, game:Game) -> None:
    set_color(stdscr, c.COLOR_BLUE, c.COLOR_BLACK)
    for i, row in enumerate(game.tiles):
        stdscr.addstr(i, 0, ' '.join(row))
    
    set_color(stdscr, c.COLOR_YELLOW, c.COLOR_BLACK)
    stdscr.addstr(game.pacman.pos.y, game.pacman.pos.x*2, '>')
    
    for ghost in game.ghosts:
        set_color(stdscr, ghost.color, c.COLOR_BLACK)
        stdscr.addstr(ghost.body.pos.y, ghost.body.pos.x*2, 'M')
    
    unset_color(stdscr)
    stdscr.addstr(0, (game.w + 1)*2, f"STATS")
    stdscr.addstr(2, (game.w + 1)*2, f"score: {game.score}")
    
    stdscr.refresh()

# =======================================================
# NOTE(Elias): Main

FPS = 33

def main(stdscr) -> None:
    tiles = loadmap("map.txt")
    pacman = Body(vec2(1, 1), vec2(1, 0))
    ghosts = [
        Ghost(Body(vec2(1, 0), vec2(1, 0)), c.COLOR_RED),
        Ghost(Body(vec2(10, 0), vec2(-1, 0)), c.COLOR_CYAN),
        Ghost(Body(vec2(2, 10), vec2(1, 0)), c.COLOR_MAGENTA),
        Ghost(Body(vec2(3, 2), vec2(1, 0)), c.COLOR_GREEN),
        ]

    game:Game = Game(True, 0, len(tiles[0]), len(tiles), tiles, pacman, ghosts)

    nspf = (1/FPS)*10e9

    while (game.running):
        start_t = time.perf_counter_ns()
        game_update(game)
        game_render(stdscr, game)
        end_t = time.perf_counter_ns()
        wait_t = nspf - (end_t - start_t)
        if (wait_t > 0):
            # NOTE(Elias): Is sleep the correct way of doing this?
            # There might be a problem with interrupt signals?
            time.sleep(wait_t/10e9) 
        stdscr.getkey()

    stdscr.addstr(8, game.w*2 + 2, f"You got eaten! :(")
    stdscr.refresh()
    stdscr.getkey()


# ======================================================= #
# NOTE(Elias): start c application #

print("Ai-Pacman (c) Bavo Verstraeten, Elias Nijs")
c.wrapper(main)
