from dataclasses import dataclass
from enum import Enum
from base import *


DIRS = [vec2(0,-1), vec2(1, 0), vec2(0,1), vec2(-1,0)]
POWERTIMER = 60
GHOSTRESPAWN = 30


class Tiles(Enum):
    EMPTY: str = ' '
    WALL: str = '#'
    PELLET: str = '·'
    POWER: str = '0'


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
class Body:
    pos: vec2
    dir: vec2

# ==============================================================
# NOTE(Elias): Game 

@dataclass
class Ghost:
    body: Body
    spawn: vec2
    killable: bool
    deathtime: int
    color: int

@dataclass
class Game:
    running: bool
    controller:Controller
    powertime: int
    combo: int
    score: int
    w: int
    h: int
    tiles: list[list[str]]
    pacman: Body
    ghosts: list[Ghost]