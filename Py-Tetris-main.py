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

def format_preview(shape, size=4):
    preview = [[0]*size for _ in range(size)]
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if y < size and x < size:
                preview[y][x] = c
    return ["".join("[]" if c else "  " for c in row) for row in preview]

def draw(board, shape, offset, score, next_shapes):
    print("\033[H", end="")

    temp = [row[:] for row in board]
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c:
                if 0 <= offset[1] + y < HEIGHT and 0 <= offset[0] + x < WIDTH:
                    temp[offset[1] + y][offset[0] + x] = c

    print("+" + "--" * WIDTH + "+    Next Shapes:")

    next_previews = [format_preview(ns) for ns in next_shapes]
    preview_height = len(next_previews[0])
    spacing = 2

    for y in range(HEIGHT):
        line = "|"
        for x in range(WIDTH):
            val = temp[y][x]
            line += "[]" if val else "· "
        line += "|"

        preview_line = ""
        total_preview_height = preview_height * len(next_previews) + spacing * (len(next_previews)-1)
        if y < total_preview_height:
            idx = y
            for i, preview in enumerate(next_previews):
                if idx < preview_height:
                    preview_line += "    " + preview[idx]
                    break
                idx -= preview_height + spacing
        line += preview_line
        print(line)

    print("+" + "--" * WIDTH + "+")
    print(f"Score: {score}")
    print("Controls: A=left, D=right, W=rotate, S=hard drop, Q=quit")

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

def hard_drop(board, shape, offset):
    while not check_collision(board, shape, [offset[0], offset[1] + 1]):
        offset[1] += 1
    return offset

def tetris():
    board = empty_board()
    score = 0
    speed = 1.0
    current_shape = random.choice(list(SHAPES.values()))
    next_shapes = [random.choice(list(SHAPES.values())) for _ in range(3)]
    offset = [WIDTH // 2 - len(current_shape[0]) // 2, 0]
    last_fall_time = time.time()

    if not WINDOWS:
        print("\033[2J")
        print("\033[?25l", end="")
    else:
        os.system('cls')

    try:
        while True:
            draw(board, current_shape, offset, score, next_shapes)
            move = get_input(0)

            if move == "q":
                print("Game ended!")
                break
            elif move == "a":
                new_off = [offset[0] - 1, offset[1]]
                if not check_collision(board, current_shape, new_off):
                    offset = new_off
            elif move == "d":
                new_off = [offset[0] + 1, offset[1]]
                if not check_collision(board, current_shape, new_off):
                    offset = new_off
            elif move == "w":
                new_shape = rotate(current_shape)
                if not check_collision(board, new_shape, offset):
                    current_shape = new_shape
            elif move == "s":
                offset = hard_drop(board, current_shape, offset)

            if time.time() - last_fall_time > speed:
                offset[1] += 1
                last_fall_time = time.time()
                if check_collision(board, current_shape, offset):
                    offset[1] -= 1
                    merge(board, current_shape, offset)
                    board, lines = clear_lines(board)
                    score += lines * 100
                    if lines:
                        speed = max(0.3, speed - 0.1)
                    current_shape = next_shapes.pop(0)
                    next_shapes.append(random.choice(list(SHAPES.values())))
                    offset = [WIDTH // 2 - len(current_shape[0]) // 2, 0]
                    if check_collision(board, current_shape, offset):
                        draw(board, current_shape, offset, score, next_shapes)
                        print("GAME OVER! Final Score:", score)
                        break

            time.sleep(0.05)
    finally:
        if not WINDOWS:
            print("\033[?25h", end="")

if __name__ == "__main__":
    tetris()
