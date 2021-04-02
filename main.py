import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('A* Pathfinding Visualization')

RGB_COLOR_RED = (255, 0, 0)
RGB_COLOR_GREEN = (0, 255, 0)
RGB_COLOR_BLUE = (0, 0, 255)
RGB_COLOR_YELLOW = (255, 255, 0)
RGB_COLOR_WHITE = (255, 255, 255)
RGB_COLOR_BLACK = (0, 0, 0)
RGB_COLOR_PURPLE = (128, 0, 128)
RGB_COLOR_ORANGE = (255, 165, 0)
RGB_COLOR_GREY = (128, 128, 128)
RGB_COLOR_TURQUOISE = (64, 224, 208)


class Node:
    def __init__(self, row, column, width, total_rows):
        self.row = row
        self.column = column
        self.x = row * width
        self.y = column * width
        self.color = RGB_COLOR_WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_position(self):
        return self.row, self.column

    def is_closed(self):
        return self.color == RGB_COLOR_RED

    def is_open(self):
        return self.color == RGB_COLOR_GREEN

    def is_barrier(self):
        return self.color == RGB_COLOR_BLACK

    def is_start(self):
        return self.color == RGB_COLOR_ORANGE

    def is_end(self):
        return self.color == RGB_COLOR_PURPLE

    def reset(self):
        self.color = RGB_COLOR_WHITE

    def show_as_started(self):
        self.color = RGB_COLOR_ORANGE

    def show_as_closed(self):
        self.color = RGB_COLOR_RED

    def show_as_open(self):
        self.color = RGB_COLOR_GREEN

    def show_as_barrier(self):
        self.color = RGB_COLOR_BLACK

    def show_as_ended(self):
        self.color = RGB_COLOR_TURQUOISE

    def show_colored_path(self):
        self.color = RGB_COLOR_PURPLE

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    """
    It´s important to determine if a potential neighbour node is a barrier or not.
    Barriers can absolutely not be treated as neighbours
    """
    def update_neighbours(self, grid):
        self.neighbours = []

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.column].is_barrier(): #down
            self.neighbours.append(grid[self.row + 1][self.column])

        if self.row > 0 and not grid[self.row - 1][self.column].is_barrier(): #up
            self.neighbours.append(grid[self.row - 1][self.column])

        if self.column < self.total_rows - 1 and not grid[self.row][self.column + 1].is_barrier(): #right
            self.neighbours.append(grid[self.row][self.column + 1])

        if self.row > 0 and not grid[self.row][self.column - 1].is_barrier(): #left
            self.neighbours.append(grid[self.row][self.column - 1])

    """Means less than. Handles what happens when 2 Nodes are compared"""
    def __lt__(self, other):
        return False


"""
H stands for the guessing distance in the A* Algorithm. 
Method figures out distance between point1 and point2
Here we´re using manhattan distance.
"""
def get_guessed_distance_h(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(node_coming_from, current_node, draw):
    while current_node in node_coming_from:
        current_node = node_coming_from[current_node]
        current_node.show_colored_path()

        draw()

def run_astar_algorithm(draw, grid, starting_node, ending_node):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, starting_node))
    node_coming_from = {}

    g_score = {spot: float('inf') for row in grid for spot in row}
    g_score[starting_node] = 0

    f_score = {spot: float('inf') for row in grid for spot in row}
    f_score[starting_node] = get_guessed_distance_h(starting_node.get_position(), ending_node.get_position())

    open_set_hash = {starting_node}
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_node = open_set.get()[2]
        open_set_hash.remove(current_node)

        if current_node == ending_node:
            reconstruct_path(node_coming_from, ending_node, draw)
            ending_node.show_as_ended()
            return True

        for neighbour in current_node.neighbours:
            temp_g_score = g_score[current_node] + 1

            if temp_g_score < g_score[neighbour]:
                node_coming_from[neighbour] = current_node
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + get_guessed_distance_h(neighbour.get_position(), ending_node.get_position())

                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.show_as_open()

        draw()

        if current_node != starting_node:
            current_node.show_as_closed()

    return False



def create_grid(number_of_rows, width):
    grid = []
    gap = width // number_of_rows

    for row in range(number_of_rows):
        grid.append([])
        for column in range(number_of_rows):
            node = Node(row, column, gap, number_of_rows)
            grid[row].append(node)

    return grid

def draw_grid(window, rows, width):
    gap = width // rows

    # horizontal lines
    for x in range(rows):
        pygame.draw.line(window, RGB_COLOR_GREY, (0, x * gap), (width, x * gap))
        # vertical lines
        for y in range(rows):
            pygame.draw.line(window, RGB_COLOR_GREY, (y * gap, 0), (y * gap, width))

def draw(window, grid, rows, width):
    window.fill(RGB_COLOR_WHITE)

    for row in grid:
        for node in row:
            node.draw(window)

    draw_grid(window, rows, width)
    pygame.display.update()

def get_clicked_position(mouse_position, rows, width):
    gap = width // rows
    y, x = mouse_position
    row = y // gap
    column = x // gap

    return row, column

def main(window, width):
    TOTAL_NUMBER_OF_ROWS = 50
    grid = create_grid(TOTAL_NUMBER_OF_ROWS, width)

    starting_node = None
    ending_node = None
    run = True

    while run:
        draw(window, grid, TOTAL_NUMBER_OF_ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # left mouse click
                position = pygame.mouse.get_pos()
                row, column = get_clicked_position(position, TOTAL_NUMBER_OF_ROWS, width)
                node = grid[row][column]

                if not starting_node and node != ending_node:
                    starting_node = node
                    starting_node.show_as_started()
                elif not ending_node and node != starting_node:
                    ending_node = node
                    ending_node.show_as_ended()
                elif node != ending_node and node != starting_node:
                    node.show_as_barrier()

            elif pygame.mouse.get_pressed()[2]:  # right mouse click
                position = pygame.mouse.get_pos()
                row, column = get_clicked_position(position, TOTAL_NUMBER_OF_ROWS, width)
                node = grid[row][column]
                node.reset()

                if node == starting_node:
                    starting_node = None
                elif node == ending_node:
                    ending_node = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and starting_node and ending_node:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)

                    run_astar_algorithm(lambda: draw(window, grid, TOTAL_NUMBER_OF_ROWS, width), grid, starting_node, ending_node)

                if event.key == pygame.K_c:
                    starting_node = None
                    ending_node = None
                    grid = create_grid(TOTAL_NUMBER_OF_ROWS, width)

    pygame.quit()

main(WINDOW, WIDTH)
