import pygame
import math
from dataclasses import dataclass, field
from coordinate_mapper import world_to_screen_centre


@dataclass(slots=True)
class Wall:
    cell: tuple
    color: tuple
    texture: str | None = None
    metadata: dict = field(default_factory=dict)

class Grid:
    def __init__(self):
        self.CELL_WIDTH = 50
        self.CELL_HEIGHT = 50

        self.highlights = set()
        self.walls = {}

    def world_to_cell(self, pos):
        return (
            math.floor(pos[0] / self.CELL_WIDTH),
            math.floor(pos[1] / self.CELL_HEIGHT),
        )

    def add_wall(self, wall):
        self.walls[wall.cell] = wall

    def remove_wall(self, cell):
        del self.walls[cell]

    def is_wall(self, cell):
        return cell in self.walls

    def get_wall_color(self, cell, color):
        return self.walls[cell].color

    def cell_to_world(self, cell):
        return (cell[0] * self.CELL_WIDTH, cell[1] * self.CELL_HEIGHT)

    def is_world_wall(self, pos):
        return self.is_wall(self.world_to_cell(pos))

    def cell_rect_to_screen(self, surface, cell, project):
        wx, wy = self.cell_to_world(cell)

        # top-left world position of cell
        top_left_world = (wx, wy + self.CELL_HEIGHT)

        sx, sy = project(surface, top_left_world)

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
        for wall in walls:
            self.walls[tuple(wall.cell)] = wall

    def highlight_cell(self, cell):
        self.highlights.add(cell)

    def draw_grid_lines(self, surface, bounds, project=world_to_screen_centre):
        start_x, end_x, start_y, end_y = bounds

        x = start_x
        while x <= end_x:
            start = project(surface, (x, start_y)) # what we want is the top corner no matter where
            end = project(surface, (x, end_y))

            pygame.draw.line(surface, "white", start, end)

            x += self.CELL_WIDTH

        # horizontal lines
        y = start_y
        while y <= end_y:
            start = project(surface, (start_x, y)) 
            end = project(surface, (end_x, y))

            pygame.draw.line(surface, "white", start, end)

            y += self.CELL_HEIGHT

    def draw_walls(self, surface, project=world_to_screen_centre):
        for cell in self.walls:
            rect = self.cell_rect_to_screen(surface, cell, project=project)
            pygame.draw.rect(surface, self.walls[cell].color, rect)

    def draw_highlights(self, surface, project):
        for cell in self.highlights:
            rect = self.cell_rect_to_screen(surface, cell, project)

            pygame.draw.rect(surface, "yellow", rect, width=2)

    def highlight_world(self, pos):
        self.highlight_cell(self.world_to_cell(pos))

    def clear_highlights(self):
        self.highlights.clear()

    def draw(self, surface, project=world_to_screen_centre):
        # self.draw_grid_lines(surface, project=project)

        self.draw_walls(surface, project=project)

        self.draw_highlights(surface, project=project)
