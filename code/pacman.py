from dataclasses import dataclass
from enum import Enum
from random import randint
from time import sleep

import curses
from curses import wrapper


# ======================================================= #
"""
TODO(Elias):
- detect keystrokes with ncurses
- render with ncurses
- normal food stuff
- power pellets
- more advanced map loading (for example map positions)
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
class Actor:
    pos:vec2
    dir:vec2

@dataclass
class Game:
    running:bool
    score:int
    w:int
    h:int
    tiles:list[str]
    pacman:Actor
    ghosts:Actor

class Tiles(Enum):
    EMPTY:str = ' '
    WALL:str = '#'

# ======================================================= #
# NOTE(Elias): Base Functions

def clamp(lb, v, ub):
    return min(max(lb, v), ub)

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
        pn = ghost.pos + ghost.dir
        while game.tiles[pn.y][pn.x] != Tiles.EMPTY.value:
            ghost.dir = rand_dir()
            pn = ghost.pos + ghost.dir
        ghost.pos = pn 
        if ghost.pos == game.pacman.pos:
            game.running = False 

def game_render(stdscr, game:Game) -> None:
    for i, row in enumerate(game.tiles):
        stdscr.addstr(i, 0, ' '.join(row))
    stdscr.addstr(game.pacman.pos.y, game.pacman.pos.x*2, 'P')
    for ghost in game.ghosts:
        stdscr.addstr(ghost.pos.y, ghost.pos.x*2, 'G')
    stdscr.refresh()

# =======================================================
# NOTE(Elias): Main

def main(stdscr) -> None:

    tiles = loadmap("map.txt")
    pacman = Actor(vec2(1, 1), vec2(1, 0))
    ghosts = [
        Actor(vec2(1, 0), vec2(1, 0)),
        Actor(vec2(10, 0), vec2(-1, 0)),
        Actor(vec2(2, 10), vec2(1, 0)),
        Actor(vec2(3, 2), vec2(1, 0)),
        ]

    game:Game = Game(True, 0, len(tiles[0]), len(tiles), tiles, pacman, ghosts)




    while (game.running):
        game_update(game)
        game_render(stdscr, game)
        sleep(0.33)
    stdscr.getkey()


# ======================================================= #
# NOTE(Elias): start curses application #

print("Ai-Pacman (c) Bavo Verstraeten, Elias Nijs")
wrapper(main)
