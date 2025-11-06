import os
import time
import random
import sys

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    import termios, tty, select
    WINDOWS = False

WIDTH, HEIGHT = 10, 20

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

def rotate(shape):
    return [list(r) for r in zip(*shape[::-1])]

def empty_board():
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

def draw(board, shape, offset, score):
    print("\033[H", end="")

    temp = [row[:] for row in board]
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c:
                if 0 <= offset[1] + y < HEIGHT and 0 <= offset[0] + x < WIDTH:
                    temp[offset[1] + y][offset[0] + x] = c
    print("+" + "--" * WIDTH + "+")
    for row in temp:
        print("|" + "".join("[]" if x else "  " for x in row) + "|")
    print("+" + "--" * WIDTH + "+")
    print(f"Score: {score}")
    print("Controls: A=links, D=rechts, W=drehen, S=fallen, Q=quit")

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c:
                if (x + off_x < 0 or x + off_x >= WIDTH or
                    y + off_y >= HEIGHT or
                    board[y + off_y][x + off_x]):
                    return True
    return False

def merge(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c:
                board[y + off_y][x + off_x] = c

def clear_lines(board):
    cleared = [row for row in board if any(v == 0 for v in row)]
    lines = HEIGHT - len(cleared)
    while len(cleared) < HEIGHT:
        cleared.insert(0, [0] * WIDTH)
    return cleared, lines

def get_input(timeout=0):
    if WINDOWS:
        if msvcrt.kbhit():
            ch = msvcrt.getwch().lower()
            return ch
        return ""
    else:
        dr, _, _ = select.select([sys.stdin], [], [], timeout)
        if dr:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1).lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        return ""

def tetris():
    board = empty_board()
    score = 0
    speed = 1.0
    shape = random.choice(list(SHAPES.values()))
    offset = [WIDTH // 2 - len(shape[0]) // 2, 0]
    last_fall_time = time.time()

    if not WINDOWS:
        print("\033[2J")
        print("\033[?25l", end="")
    else:
        os.system('cls')

    try:
        while True:
            draw(board, shape, offset, score)
            move = get_input(0)

            if move == "q":
                print("Spiel beendet!")
                break
            elif move == "a":
                new_off = [offset[0] - 1, offset[1]]
                if not check_collision(board, shape, new_off):
                    offset = new_off
            elif move == "d":
                new_off = [offset[0] + 1, offset[1]]
                if not check_collision(board, shape, new_off):
                    offset = new_off
            elif move == "w":
                new_shape = rotate(shape)
                if not check_collision(board, new_shape, offset):
                    shape = new_shape
            elif move == "s":
                offset[1] += 1
                if check_collision(board, shape, offset):
                    offset[1] -= 1

            if time.time() - last_fall_time > speed:
                offset[1] += 1
                last_fall_time = time.time()
                if check_collision(board, shape, offset):
                    offset[1] -= 1
                    merge(board, shape, offset)
                    board, lines = clear_lines(board)
                    score += lines * 100
                    if lines:
                        speed = max(0.3, speed - 0.1)
                    shape = random.choice(list(SHAPES.values()))
                    offset = [WIDTH // 2 - len(shape[0]) // 2, 0]
                    if check_collision(board, shape, offset):
                        draw(board, shape, offset, score)
                        print("GAME OVER! Endpunktzahl:", score)
                        break

            time.sleep(0.05)
    finally:
        if not WINDOWS:
            print("\033[?25h", end="")

if __name__ == "__main__":
    tetris()
