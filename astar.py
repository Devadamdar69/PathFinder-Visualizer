import pygame
import math
from queue import PriorityQueue

WIDTH = 500
PLOT = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* PATH FINDING")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
CYAN = (0, 225, 225)

class Point:
    def __init__(self, row, col, width, total_row):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.width = width
        self.total_row = total_row
        self.neighbors = []

    def get_pos(self):
        return self.row, self.col

    def is_open(self):
        return self.color == PURPLE

    def is_blocked(self):
        return self.color == RED

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == CYAN

    def reset(self):
        self.color = WHITE

    def make_open(self):
        self.color = PURPLE

    def make_closed(self):
        self.color = RED

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = CYAN

    def make_path(self):
        self.color = GREEN

    def draw(self, plot):
        pygame.draw.rect(plot, self.color, (self.x, self.y, self.width, self.width))

    def neighbor_update(self, grid):
        self.neighbors = []
        if self.row < self.total_row - 1 and not grid[self.row + 1][self.col].is_barrier():  # down
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # up
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_row - 1 and not grid[self.row][self.col + 1].is_barrier():  # right
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # left
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}

    g_score = {point: float('inf') for row in grid for point in row}
    g_score[start] = 0

    f_score = {point: float('inf') for row in grid for point in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            grid[i].append(Point(i, j, gap, rows))

    return grid


def grid_line(plot, row, width):
    gap = width // row
    for i in range(row):
        pygame.draw.line(plot, GREY, (0, i * gap), (width, i * gap))
        for j in range(row):
            pygame.draw.line(plot, GREY, (j * gap, 0), (j * gap, width))


def draw(plot, grid, rows, width):
    plot.fill(WHITE)

    for row in grid:
        for point in row:
            point.draw(plot)

    grid_line(plot, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap

    return row, col


def main(plot, width):
    ROWS = 20
    grid = make_grid(ROWS, width)
    start = None
    end = None

    run = True
    finding = False

    while run:
        draw(plot, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if finding:
                continue

            if pygame.mouse.get_pressed()[0]:  # left mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                point = grid[row][col]
                if not start and point != end:
                    start = point
                    start.make_start()
                elif not end and point != start:
                    end = point
                    end.make_end()
                elif point != start and point != end:
                    point.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # right mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                point = grid[row][col]
                point.reset()
                if point == start:
                    start = None
                elif point == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not finding:
                    for row in grid:
                        for point in row:
                            point.neighbor_update(grid)

                    algorithm(lambda: draw(plot, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(PLOT, WIDTH)

