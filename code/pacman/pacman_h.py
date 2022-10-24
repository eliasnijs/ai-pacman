from dataclasses import dataclass
from enum import Enum
from base import *
import curses

# ==============================================================
# NOTE(Elias): Keyboard

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

# ==============================================================
# NOTE(Elias): Physics

@dataclass
class PhysicsBody:
    pos: vec2
    dir: vec2

# ==============================================================
# NOTE(Elias): Game

@dataclass
class Ghost:
    body: PhysicsBody
    spawn: vec2
    killable: bool
    deathtime: int
    color: int

@dataclass
class Game:
    running:bool
    controller:Controller
    powertime:int
    combo:int
    score: int
    w:int
    h:int
    tiles:list[list[str]]
    pelletcount: int
    pacman:PhysicsBody
    ghosts:list[Ghost]

# ==============================================================
# NOTE(Elias): Constants

FPS          = 15
POWERTIMER   = 60
GHOSTRESPAWN = 30
DIRS         = [vec2(0,-1), vec2(1, 0), vec2(0,1), vec2(-1,0)]
# NOTE(Bavo): colors of the ghosts, and thus also the maximum number of ghosts
GHOST_COLORS = [curses.COLOR_RED, curses.COLOR_CYAN, curses.COLOR_MAGENTA, curses.COLOR_GREEN]

class TILES(Enum):
    EMPTY   :str = ' '
    WALL    :str = '#'
    PELLET  :str = '·'
    POWER   :str = '0'
