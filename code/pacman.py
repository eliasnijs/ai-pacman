import random
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
    x: int
    y: int

    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)


# ======================================================= #
# NOTE(Elias): Game Structs 

class Tiles(Enum):
    EMPTY: str = ' '
    WALL: str = '#'
    PELLET: str = '·'
    POWER: str = '0'


@dataclass
class Body:
    pos: vec2
    dir: vec2


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
    powertime: int
    combo: int
    score: int
    w: int
    h: int
    tiles: list[list[str]]
    pacman: Body
    ghosts: list[Ghost]


FPS = 5
POWERTIMER = 60
GHOSTRESPAWN = 30
DIRS = [vec2(0, 1), vec2(1, 0), vec2(0, -1), vec2(-1, 0)]


# ======================================================= #
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

def isEmpty(row: int, col: int, game: Game) -> bool:
    return game.tiles[row][col] in [Tiles.EMPTY.value, Tiles.PELLET.value, Tiles.POWER.value]


# NOTE(Bavo): colors of the ghosts, and thus also the maximum number of ghosts
Colors = [curses.COLOR_RED, curses.COLOR_CYAN, curses.COLOR_MAGENTA, curses.COLOR_GREEN]


def loadmap(path: str) -> (list[list[str]], Body, list[Body]):
    tiles = [list(row) for row in open(path, "r", encoding="utf-8").read().splitlines()]
    ghosts = []
    pacman = None
    colorIndex = 0
    colorLen = len(Colors)
    maxW = len(max(tiles, key=lambda x: len(x)))
    for row, tileRow in enumerate(tiles):
        for col, tile in enumerate(tileRow):
            if tile == "P":
                if pacman is not None:
                    raise Exception("More than one pacman on the map")
                pacman = Body(vec2(col, row), vec2(1, 0))
                tiles[row][col] = Tiles.PELLET.value
            elif tile == "G":
                if colorIndex == colorLen:
                    raise Exception("Number of ghosts on the map exceeded the maximum: " + str(colorLen))
                ghosts.append(Ghost(Body(vec2(col, row), vec2(0, 1)), vec2(col, row), False, 0, Colors[colorIndex]))
                colorIndex += 1
                tiles[row][col] = Tiles.PELLET.value

        if len(tileRow) < maxW:
            for _ in range(maxW - len(tileRow)):
                tileRow.append(" ")
    if pacman is None:
        raise Exception("No pacman (symbol = 'P') found on the map")
    return tiles, pacman, ghosts


def rand_dir() -> vec2:
    return DIRS[randint(0, 3)]


# =======================================================
# NOTE(Elias): Game

# NOTE(Bavo): call this at beginning and end of ghost movement. Returns if the ghost may still move
def handle_touch(game: Game, ghost: Ghost) -> bool:
    if ghost.body.pos == game.pacman.pos:
        if not ghost.killable:
            game.running = False
        else:
            ghost.body.pos = ghost.spawn
            ghost.body.dir = vec2(0, 1)
            ghost.deathtime = GHOSTRESPAWN
            ghost.killable = False
            game.score += game.combo
            game.combo *= 2
        return False
    return True


def game_update(game: Game, input) -> None:
    # NOTE(Elias): Update pacman

    if game.powertime > 0:
        game.powertime -= 1
    else:
        game.combo = 0

    pn = game.pacman.pos + game.pacman.dir
    if 0 <= pn.x < game.w and 0 <= pn.y < game.h and isEmpty(pn.y, pn.x, game):
        game.pacman.pos = pn
        if game.tiles[pn.y][pn.x] == Tiles.PELLET.value:
            game.tiles[pn.y][pn.x] = Tiles.EMPTY.value
            game.score += 10
        if game.tiles[pn.y][pn.x] == Tiles.POWER.value:
            game.tiles[pn.y][pn.x] = Tiles.EMPTY.value
            game.score += 50
            game.powertime = POWERTIMER
            game.combo = 200

    # NOTE(Elias): Update ghosts

    for ghost in game.ghosts:
        if ghost.deathtime > 0:
            ghost.deathtime -= 1
        else:
            if game.powertime == POWERTIMER:
                ghost.killable = True
            if game.powertime == 0:
                ghost.killable = False
            if handle_touch(game, ghost):
                open = []
                for dir in DIRS:
                    pn = ghost.body.pos + dir
                    if (0 <= pn.x < game.w and 0 <= pn.y < game.h and isEmpty(pn.y, pn.x, game)
                            and dir != vec2(- ghost.body.dir.x, - ghost.body.dir.y)):
                        open.append(dir)
                spots = len(open)
                if spots == 0:
                    ghost.body.dir = vec2(- ghost.body.dir.x, - ghost.body.dir.y)
                else:
                    ghost.body.dir = random.choice(open)

                pn = ghost.body.pos + ghost.body.dir
                if 0 <= pn.x < game.w and 0 <= pn.y < game.h and isEmpty(pn.y, pn.x, game):
                    ghost.body.pos = pn

                handle_touch(game, ghost)


def game_render(stdscr, game: Game) -> None:
    for i, row in enumerate(game.tiles):
        for j, tile in enumerate(row):
            set_color(stdscr, curses.COLOR_YELLOW if tile == Tiles.PELLET.value else
            curses.COLOR_WHITE if tile == Tiles.POWER.value else curses.COLOR_BLUE, curses.COLOR_BLACK)
            stdscr.addstr(i, 2 * j, tile + " ")

    set_color(stdscr, curses.COLOR_YELLOW if game.powertime == 0 else curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.addstr(game.pacman.pos.y, game.pacman.pos.x * 2, 'Q')

    for ghost in game.ghosts:
        set_color(stdscr, curses.COLOR_WHITE if ghost.killable else
        curses.COLOR_BLUE if ghost.deathtime > 0 else ghost.color, curses.COLOR_BLACK)
        stdscr.addstr(ghost.body.pos.y, ghost.body.pos.x * 2, 'M')

    unset_color(stdscr)
    stdscr.addstr(0, (game.w + 1) * 2, f"Ai-Pacman (c) Elias Nijs, Bavo Verstraeten")
    stdscr.addstr(3, (game.w + 1) * 2, f"score: {game.score}")

    stdscr.refresh()


# =======================================================
# NOTE(Elias): Main

def handlekeys(game: Game, key: int) -> None:
    if key == ord('w'):
        game.pacman.dir = DIRS[0]
    elif key == ord('d'):
        game.pacman.dir = DIRS[1]
    elif key == ord('s'):
        game.pacman.dir = DIRS[2]
    elif key == ord('a'):
        game.pacman.dir = DIRS[3]


def pacman(stdscr) -> None:
    tiles, pacman, ghosts = loadmap("map.txt")

    game: Game = Game(True, 0, 0, 0, len(tiles[0]), len(tiles), tiles, pacman, ghosts)

    nspf = (1 / FPS) * 10e9

    stdscr.nodelay(True)

    while game.running:
        start_t = time.perf_counter_ns()
        key = stdscr.getch()
        if key == ord('q'):
            break
        else:
            handlekeys(game, key)
        game_update(game, None)
        game_render(stdscr, game)
        end_t = time.perf_counter_ns()
        wait_t = nspf - (end_t - start_t)
        if (wait_t > 0):
            # NOTE(Elias): Is sleep the correct way of doing this?
            # There might be a problem with interrupt signals?
            time.sleep(wait_t / 10e9)

        # ======================================================= #


# NOTE(Elias): start application #

curses.wrapper(pacman)
