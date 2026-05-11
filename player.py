import math
from ray import Vec


class Player:
    def __init__(self, pos=(0, 0), angle=0):
        self.pos = Vec(pos)

        self.angle = math.radians(angle)

        self.move_speed = 3
        self.turn_speed = math.radians(2)

        self.radius = 12

    @property
    def direction(self):
        return Vec((math.cos(self.angle), math.sin(self.angle))).normalized()

    def rotate_left(self):
        self.angle += self.turn_speed

    def rotate_right(self):
        self.angle -= self.turn_speed

    def move_forward(self):
        self.pos = self.pos + (self.direction * self.move_speed)

    def move(self, movement, grid):

        next_pos = self.pos + movement

        test_points = [
            (next_pos.x + self.radius, next_pos.y),
            (next_pos.x - self.radius, next_pos.y),
            (next_pos.x, next_pos.y + self.radius),
            (next_pos.x, next_pos.y - self.radius),
        ]

        blocked = any(
            grid.is_world_wall(p)
            for p in test_points
        )

        if not blocked:
            self.pos = next_pos

    def move_backward(self):
        self.pos = self.pos - (self.direction * self.move_speed)
