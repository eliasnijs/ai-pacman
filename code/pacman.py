from dataclasses import dataclass
from enum import Enum
from random import randint
import time

import curses as c

# ======================================================= #
"""
NOTE(Elias):
Resources:
- pacman in c:
    https://github.com/MarquisdeGeek/pacman/tree/master/src
- nc examples: 
    https://github.com/zephyrproject-rtos/windows-curses/tree/master/examples
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

class Tiles(Enum):
    EMPTY:str = ' '
    WALL:str = '#'

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

FPS = 33
DIRS = [vec2(0,1), vec2(1, 0), vec2(0,-1), vec2(-1,0)]


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

#NOTE(BAVO
Colors = [c.COLOR_RED,c.COLOR_CYAN,c.COLOR_MAGENTA,c.COLOR_GREEN]

def loadmap(path:str) -> (list[list[str]],Body,list[Body]):
    tiles =  [ list(row) for row in open(path, "r").read().splitlines() ]
    ghosts = []
    pacman = None
    colorIndex = 0
    colorLen = len(Colors)

    for row,tileRow in enumerate(tiles):
        for col,tile in enumerate(tileRow):
            if tile == "P":
                if pacman is not None:
                    raise Exception("More than one pacman on the map")
                pacman = Body(vec2(col,row),vec2(1,0))
                tiles[row][col] = " "
            elif tile == "G":
                if colorIndex == colorLen:
                    raise Exception("Number of ghosts on the map exceeded the maximum: "+str(colorLen))
                ghosts.append(Ghost(Body(vec2(col,row),vec2(0,1)),Colors[colorIndex]))
                colorIndex+=1
                tiles[row][col] = " "
    if pacman is None:
        raise Exception("No pacman (symbol = 'P') found on the map")
    return tiles,pacman,ghosts

def rand_dir() -> vec2:
    return DIRS[randint(0, 3)]
            
# =======================================================
# NOTE(Elias): Game
    
def game_update(game:Game, input) -> None:
    # NOTE(Elias): Handle keyboard input 
    match input:
        case "W": game.pacman.dir = DIRS[0]
        case "D": game.pacman.dir = DIRS[1]
        case "D": game.pacman.dir = DIRS[2]
        case "D": game.pacman.dir = DIRS[3]
        case "Q": game.running = False

    # NOTE(Elias): Update pacman
    pn = game.pacman.pos + game.pacman.dir
    if game.tiles[pn.y][pn.x] == Tiles.EMPTY.value:
        game.pacman.pos = pn

    # NOTE(Elias): Update ghosts 
    for ghost in game.ghosts:
        
        if ghost.body.pos == game.pacman.pos:
            game.running = False

        # TODO(Elias): does not take into account a switch in direction
        # before encountering a wall
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
    stdscr.addstr(game.pacman.pos.y, game.pacman.pos.x*2, 'W')
    
    for ghost in game.ghosts:
        set_color(stdscr, ghost.color, c.COLOR_BLACK)
        stdscr.addstr(ghost.body.pos.y, ghost.body.pos.x*2, 'M')
    
    unset_color(stdscr)
    stdscr.addstr(0, (game.w + 1)*2, f"Ai-Pacman (c) Elias Nijs, Bavo Verstraeten")
    stdscr.addstr(3, (game.w + 1)*2, f"score: {game.score}")
    
    stdscr.refresh()

# =======================================================
# NOTE(Elias): Main

def pacman(stdscr) -> None:
    tiles,pacman,ghosts = loadmap("map.txt")

    game:Game = Game(True, 0, len(tiles[0]), len(tiles), tiles, pacman, ghosts)

    nspf = (1/FPS)*10e9

    while (game.running):
        start_t = time.perf_counter_ns()
        game_update(game, None)
        game_render(stdscr, game)
        end_t = time.perf_counter_ns()
        wait_t = nspf - (end_t - start_t)
        if (wait_t > 0):
            # NOTE(Elias): Is sleep the correct way of doing this?
            # There might be a problem with interrupt signals?
            time.sleep(wait_t/10e9) 
        stdscr.getkey()

    stdscr.refresh()
    stdscr.getkey()

def keyboard():
    pass


# ======================================================= #
# NOTE(Elias): start application #

c.wrapper(pacman)
