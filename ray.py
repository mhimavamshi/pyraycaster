import pygame
import math
from dataclasses import dataclass
from coordinate_mapper import world_to_screen_centre


class Vec:
    def __init__(self, pos):
        self.x, self.y = pos

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self):
        mag = self.magnitude()

        if mag == 0:
            return Vec((0, 0))

        return Vec((self.x / mag, self.y / mag))

    def __mul__(self, val):
        if isinstance(val, (int, float)):
            return Vec((self.x * val, self.y * val))

    def __add__(self, val):
        if isinstance(val, Vec):
            return Vec((self.x + val.x, self.y + val.y))

    def __sub__(self, val):
        if isinstance(val, Vec):
            return Vec((self.x - val.x, self.y - val.y))

    def tup(self):
        return (self.x, self.y)


# class CastResult:
#     def __init__(self, hit, cell, distance, side, grid):
#         self.hit = hit
#         self.cell = cell
#         self.distance = distance
#         self.side = side

#         self.is_wall = grid.is_wall(cell)


@dataclass(slots=True)
class CastResult:
    hit: tuple
    cell: tuple
    distance: float
    side: str
    is_wall: bool


class Ray:
    def __init__(self, dir_vec, start_pos=(0, 0)):
        self.start_pos = Vec(start_pos)
        self.directional_vect = Vec(dir_vec).normalized()

    def endpoint(self, multiple):
        return self.start_pos + (self.directional_vect * multiple)

    def draw(self, surface, multiple=1):
        end_point = self.endpoint(multiple)
        screen_start, screen_end = (
            world_to_screen_centre(surface, self.start_pos.tup()),
            world_to_screen_centre(surface, end_point.tup()),
        )
        pygame.draw.line(surface, "orange", screen_start, screen_end)

    def intersection_point(self, value, axis="x"):
        sx, sy = self.start_pos.tup()
        dx, dy = self.directional_vect.tup()

        if axis == "x":
            if dx == 0:
                return None

            t = (value - sx) / dx

            if t < 0:
                return None

            y = sy + dy * t
            return (value, y)

        elif axis == "y":
            if dy == 0:
                return None

            t = (value - sy) / dy

            if t < 0:
                return None

            x = sx + dx * t
            return (x, value)

    def cast(self, grid, max_steps=100):
        dx, dy = self.directional_vect.tup()
        sx, sy = self.start_pos.tup()

        cell_x = math.floor(sx / grid.CELL_WIDTH)
        cell_y = math.floor(sy / grid.CELL_HEIGHT)

        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        if dx > 0:
            next_x_boundary = (cell_x + 1) * grid.CELL_WIDTH
        else:
            next_x_boundary = cell_x * grid.CELL_WIDTH

        if dy > 0:
            next_y_boundary = (cell_y + 1) * grid.CELL_HEIGHT
        else:
            next_y_boundary = cell_y * grid.CELL_HEIGHT

        t_x = (next_x_boundary - sx) / dx if dx != 0 else float("inf")
        t_y = (next_y_boundary - sy) / dy if dy != 0 else float("inf")

        delta_t_x = grid.CELL_WIDTH / abs(dx) if dx != 0 else float("inf")
        delta_t_y = grid.CELL_HEIGHT / abs(dy) if dy != 0 else float("inf")

        results = []

        N = 0  # for now
        while N < max_steps:
            if t_x < t_y:
                t = t_x
                t_x += delta_t_x

                cell_x += step_x

                side = "x"

            elif t_y < t_x:
                t = t_y
                t_y += delta_t_y

                cell_y += step_y

                side = "y"

            else:
                t = t_x

                t_x += delta_t_x
                t_y += delta_t_y

                cell_x += step_x
                cell_y += step_y

                side = "corner"

            cell = (cell_x, cell_y)
            is_wall = grid.is_wall(cell)

            results.append(
                CastResult(
                    hit=(sx + dx * t, sy + dy * t),
                    cell=cell,
                    distance=t,
                    side=side,
                    is_wall=is_wall,
                )
            )

            if is_wall:
                break

            N += 1

        return results
