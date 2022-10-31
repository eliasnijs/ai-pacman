#!/bin/python3

import random as r
import time
import curses

from pacman.base import *
from pacman.pacman_h import *


# ==============================================================
# NOTE(Elias): Drawing

def set_color(win, fg):
    if curses.has_colors():
        n = fg + 1
        curses.init_pair(n, fg, curses.COLOR_BLACK)
        win.attroff(curses.A_COLOR)
        win.attron(curses.color_pair(n))

def unset_color(win):
    if curses.has_colors():
        win.attrset(curses.color_pair(0))

# ==============================================================
# NOTE(Elias): Keyboard

# NOTE(Elias): Does not support escape sequences (e.g. return-key, up-key, ...)
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

# ==============================================================
# NOTE(Elias): Controllor

def new_button():
    return Button(False, False)

def new_controller():
    return Controller(new_button(), new_button(), new_button(), new_button())

def kb_down(button:Button):
    return button.isdown

def kb_downsingle(button:Button):
    return button.isdown and not button.wasdown

def kb_upsingle(button:Button):
    return not button.isdown and button.wasdown

# =======================================================
# NOTE(Elias): Helper Functions

def is_empty(game:Game, pos:vec2) -> bool:
    return game.tiles[pos.y][pos.x] != TILES.WALL.value

def on_field(game:Game, pos:vec2) -> bool:
    return in_between(0, pos.x, game.w) and in_between(0, pos.y, game.h)

# NOTE(Bavo): call this at beginning and end of ghost movement. Returns if the ghost may still move
def handle_touch(game:Game, ghost: Ghost) -> bool:
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

def rand_dir() -> vec2:
    return DIRS[r.randint(0, 3)]


# =======================================================
# NOTE(Elias): Game

# TODO(Elias): Do this in a better way... color already set on the map?

def loadmap(path: str) -> tuple[list[list[str]], PhysicsBody, list[Ghost], int]:
    tiles = [list(row) for row in open(path, "r", encoding="utf-8").read().splitlines()]
    ghosts = []
    pacman = None
    colorIndex = 0
    colorLen = len(GHOST_COLORS)
    maxW = len(max(tiles, key=lambda x: len(x)))
    pelletcount = 0

    for row, tileRow in enumerate(tiles):
        for col, tile in enumerate(tileRow):
            if tile == "P":
                if pacman is not None:
                    raise Exception("More than one pacman on the map")
                pacman = PhysicsBody(vec2(col, row), vec2(1, 0))
            elif tile == "G":
                if colorIndex == colorLen:
                    raise Exception("Number of ghosts on the map exceeded the maximum: " + str(colorLen))
                ghosts.append(Ghost(PhysicsBody(vec2(col, row), vec2(0, 1)), vec2(col, row), False, 0, GHOST_COLORS[colorIndex]))
                colorIndex += 1
                tiles[row][col] = TILES.PELLET.value
                pelletcount+=1
            elif tile == TILES.PELLET.value:
                pelletcount+=1

        if len(tileRow) < maxW:
            for _ in range(maxW - len(tileRow)):
                tileRow.append(" ")
    if pacman is None:
        raise Exception("No pacman (symbol = 'P') found on the map")
    return tiles, pacman, ghosts, pelletcount

def new_game(map_path:str) -> Game:
    tiles, pacman, ghosts ,pellets= loadmap(map_path)
    controller = new_controller()
    return Game(True, controller, 0, 0, 0, len(tiles[0]), len(tiles), tiles, pellets, pacman, ghosts)

def game_update(game:Game) -> None:

    # NOTE(Elias): Handle controller input
    if kb_down(game.controller.up):
        if is_empty(game, game.pacman.pos + DIRS[0]):
            game.pacman.dir = DIRS[0]
    elif kb_down(game.controller.right):
        if is_empty(game, game.pacman.pos + DIRS[1]):
            game.pacman.dir = DIRS[1]
    elif kb_down(game.controller.down):
        if is_empty(game, game.pacman.pos + DIRS[2]):
            game.pacman.dir = DIRS[2]
    elif kb_down(game.controller.left):
        if is_empty(game, game.pacman.pos + DIRS[3]):
            game.pacman.dir = DIRS[3]

    # NOTE(Elias): Update pacman

    if game.powertime > 0:
        game.powertime -= 1
    else:
        game.combo = 0

    pn = game.pacman.pos + game.pacman.dir
    if on_field(game, pn) and is_empty(game, pn):
        game.pacman.pos = pn
        if game.tiles[pn.y][pn.x] == TILES.PELLET.value:
            game.tiles[pn.y][pn.x] = TILES.EMPTY.value
            game.score += 10
            game.pelletcount-=1
        if game.tiles[pn.y][pn.x] == TILES.POWER.value:
            game.tiles[pn.y][pn.x] = TILES.EMPTY.value
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
                    if (0 <= pn.x < game.w and 0 <= pn.y < game.h and is_empty(game, pn)
                            and dir != vec2(- ghost.body.dir.x, - ghost.body.dir.y)):
                        open.append(dir)
                spots = len(open)
                if spots == 0:
                    ghost.body.dir = vec2(- ghost.body.dir.x, - ghost.body.dir.y)
                else:
                    ghost.body.dir = r.choice(open)

                pn = ghost.body.pos + ghost.body.dir
                if on_field(game, pn) and is_empty(game, pn):
                    ghost.body.pos = pn

                handle_touch(game, ghost)


def game_render(stdscr, game: Game) -> None:
    # NOTE(Elias): Render map
    for i, row in enumerate(game.tiles):
        for j, tile in enumerate(row):
            if tile == TILES.PELLET.value:
                set_color(stdscr, curses.COLOR_YELLOW)
            elif tile == TILES.POWER.value:
                set_color(stdscr, curses.COLOR_WHITE)
            elif tile == TILES.WALL.value:
                set_color(stdscr, curses.COLOR_BLUE)
            else:
                set_color(stdscr, curses.COLOR_BLACK)
            stdscr.addstr(i, 2 * j, tile + " ")

    # NOTE(Elias): Render pacman
    if game.powertime != 0:
        set_color(stdscr, curses.COLOR_WHITE)
    else:
        set_color(stdscr, curses.COLOR_YELLOW)
    stdscr.addstr(game.pacman.pos.y, game.pacman.pos.x * 2, 'P')

    # NOTE(Elias): Render ghosts
    for ghost in game.ghosts:
        if ghost.killable:
            set_color(stdscr, curses.COLOR_WHITE)
        elif ghost.deathtime > 0:
            set_color(stdscr, 18)
        else:
            set_color(stdscr, ghost.color)
        stdscr.addstr(ghost.body.pos.y, ghost.body.pos.x * 2, 'M')

    # NOTE(Elias): Render statistics
    unset_color(stdscr)
    stdscr.addstr(0, (game.w + 1)*2, f"Ai-Pacman")
    stdscr.addstr(3, (game.w + 1)*2, f"score: {game.score}")

    stdscr.refresh()

# =======================================================
# NOTE(Elias): Main

def pacman(stdscr) -> int:

    # NOTE(Elias): initialisation
    stdscr.nodelay(True) # NOTE(Elias): configure curses keyboard input
    game:Game = new_game("maps/map.txt")
    framecnt = 0

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

        fps = 10e9/(end_t - start_t)
        wait_t = 10e9/FPS - (end_t - start_t)

        if (wait_t > 0):
            # NOTE(Elias): Is sleep the correct way of doing this?
            # There might be a problem with interrupt signals?
            time.sleep(wait_t/10e9)

        stdscr.addstr(4, (game.w + 1)*2, f"fps: {fps:.2f}")
        framecnt += 1

    return framecnt

def pacman_no_ui() -> int:
    game:Game = new_game("maps/map.txt")
    framecnt = 0
    while game.running:
        start_t = time.perf_counter_ns()

        game_update(game)

        end_t = time.perf_counter_ns()
        fps = 10e9/(end_t - start_t)

        framecnt += 1
    return framecnt


# NOTE(Elias): start the program
if __name__ == "__main__":
    curses.wrapper(pacman)

