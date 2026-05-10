import pygame
import math
from coordinate_mapper import world_to_screen_centre


class Grid:
    def __init__(self):
        self.CELL_WIDTH = 50
        self.CELL_HEIGHT = 50

        self.highlights = set()
        self.walls = set()

    def world_to_cell(self, pos):
        return (
            math.floor(pos[0] / self.CELL_WIDTH),
            math.floor(pos[1] / self.CELL_HEIGHT),
        )

    def add_wall(self, cell):
        self.walls.add(cell)

    def remove_wall(self, cell):
        self.walls.discard(cell)

    def is_wall(self, cell):
        return cell in self.walls

    def cell_to_world(self, cell):
        """
        Returns bottom-left corner of cell in world space.
        """
        return (cell[0] * self.CELL_WIDTH, cell[1] * self.CELL_HEIGHT)

    def cell_rect_to_screen(self, surface, cell):
        """
        Converts a grid cell into a pygame.Rect in screen space.
        """

        wx, wy = self.cell_to_world(cell)

        # top-left world position of cell
        top_left_world = (wx, wy + self.CELL_HEIGHT)

        sx, sy = world_to_screen_centre(surface, top_left_world)

        return pygame.Rect(sx, sy, self.CELL_WIDTH, self.CELL_HEIGHT)

    def cell_corners_world(self, cell):
        x, y = self.cell_to_world(cell)

        return {
            "bottom_left": (x, y),
            "top_left": (x, y + self.CELL_HEIGHT),
            "top_right": (x + self.CELL_WIDTH, y + self.CELL_HEIGHT),
            "bottom_right": (x + self.CELL_WIDTH, y),
        }

    def set_walls(self, walls):
        self.walls = set(walls)

    def highlight_cell(self, cell):
        self.highlights.add(cell)

    def draw_grid_lines(self, surface):
        width, height = surface.get_size()

        # vertical lines
        x = -width // 2

        while x <= width // 2:
            start = world_to_screen_centre(surface, (x, -height))
            end = world_to_screen_centre(surface, (x, height))

            pygame.draw.line(surface, "white", start, end)

            x += self.CELL_WIDTH

        # horizontal lines
        y = -height // 2

        while y <= height // 2:
            start = world_to_screen_centre(surface, (-width, y))
            end = world_to_screen_centre(surface, (width, y))

            pygame.draw.line(surface, "white", start, end)

            y += self.CELL_HEIGHT

    def draw_walls(self, surface):
        for cell in self.walls:
            rect = self.cell_rect_to_screen(surface, cell)

            pygame.draw.rect(surface, "gray", rect)

    def draw_highlights(self, surface):
        for cell in self.highlights:
            rect = self.cell_rect_to_screen(surface, cell)

            pygame.draw.rect(surface, "yellow", rect, width=2)

    def highlight_world(self, pos):
        self.highlight_cell(self.world_to_cell(pos))

    def clear_highlights(self):
        self.highlights.clear()

    def draw(self, surface):
        # self.draw_grid_lines(surface)

        self.draw_walls(surface)

        self.draw_highlights(surface)
