from dataclasses import dataclass
from enum import Enum
from random import randint
import time

import curses as curses

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
class Button:
    wasdown:bool
    isdown:bool 

@dataclass
class Controller:
    up:Button
    right:Button
    down:Button
    left:Button

@dataclass
class Game:
    running:bool 
    controller:Controller
    score:int
    w:int
    h:int
    tiles:list[str]
    pacman:Body
    ghosts:list[Ghost]

FPS = 6
DIRS = [vec2(0,-1), vec2(1, 0), vec2(0,1), vec2(-1,0)]


# =======================================================
# NOTE(Elias): Base Functions

def clamp(lb, v, ub):
    return min(max(lb, v), ub)

# =======================================================
# NOTE(Elias): c Helper Functions

def set_color(win, fg, bg):
    if curses.has_colors():
        n = fg + 1
        curses.init_pair(n, fg, bg)
        win.attroff(curses.A_COLOR)
        win.attron(curses.color_pair(n))

def unset_color(win):
    if curses.has_colors():
        win.attrset(curses.color_pair(0))

# =======================================================
# NOTE(Elias): Helper Functions

Colors = [curses.COLOR_RED, curses.COLOR_CYAN, curses.COLOR_MAGENTA, curses.COLOR_GREEN]

def loadmap(path:str) -> tuple[list[list[str]], Body, list[Body]]:
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

def kb_down(button:Button):
    return button.isdown

def kb_downsingle(button:Button):
    return button.isdown and not button.wasdown 

def kb_upsingle(button:Button):
    return not button.isdown and button.wasdown

def handleinput(game:Game, keys:list[int]) -> None:
    kb_key(game.controller.up, ord('w') in keys)
    kb_key(game.controller.right, ord('d') in keys)
    kb_key(game.controller.down, ord('s') in keys)
    kb_key(game.controller.left, ord('a') in keys)

            
# =======================================================
# NOTE(Elias): Game
    
def game_update(game:Game) -> None:

    # NOTE(Elias): Handle controller input 
    if kb_down(game.controller.up):
        pn = game.pacman.pos + DIRS[0] 
        if game.tiles[pn.y][pn.x] == Tiles.EMPTY.value:
            game.pacman.dir = DIRS[0]
    elif kb_down(game.controller.right):
        pn = game.pacman.pos + DIRS[1] 
        if game.tiles[pn.y][pn.x] == Tiles.EMPTY.value:
            game.pacman.dir = DIRS[1]
    elif kb_down(game.controller.down):
        pn = game.pacman.pos + DIRS[2] 
        if game.tiles[pn.y][pn.x] == Tiles.EMPTY.value:
            game.pacman.dir = DIRS[2]
    elif kb_down(game.controller.left):
        pn = game.pacman.pos + DIRS[3] 
        if game.tiles[pn.y][pn.x] == Tiles.EMPTY.value:
            game.pacman.dir = DIRS[3]
    
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
    set_color(stdscr, curses.COLOR_BLUE, curses.COLOR_BLACK)
    for i, row in enumerate(game.tiles):
        stdscr.addstr(i, 0, ' '.join(row))
    
    set_color(stdscr, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    stdscr.addstr(game.pacman.pos.y, game.pacman.pos.x*2, 'Q')
    
    for ghost in game.ghosts:
        set_color(stdscr, ghost.color, curses.COLOR_BLACK)
        stdscr.addstr(ghost.body.pos.y, ghost.body.pos.x*2, 'M')
    
    unset_color(stdscr)
    stdscr.addstr(0, (game.w + 1)*2, f"Ai-Pacman")
    stdscr.addstr(3, (game.w + 1)*2, f"score: {game.score}")
    
    stdscr.refresh()

# =======================================================
# NOTE(Elias): Main

def pacman(stdscr) -> None:
    tiles,pacman,ghosts = loadmap("map.txt")

    controller = Controller(Button(False, False), Button(False, False), Button(False, False), Button(False, False))
    game:Game = Game(True, controller, 0, len(tiles[0]), len(tiles), tiles, pacman, ghosts)

    stdscr.nodelay(True)    

    while (game.running):
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
            time.sleep(wait_t/10e9) 

# =======================================================
# NOTE(Elias): start application #

curses.wrapper(pacman)
