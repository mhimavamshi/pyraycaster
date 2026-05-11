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

    def collides(self, pos, grid):

        test_points = [
            (pos.x + self.radius, pos.y),
            (pos.x - self.radius, pos.y),
            (pos.x, pos.y + self.radius),
            (pos.x, pos.y - self.radius),
        ]

        return any(
            grid.is_world_wall(p)
            for p in test_points
        )


    def move(self, movement, grid):

        next_x = Vec(
            (
                self.pos.x + movement.x,
                self.pos.y,
            )
        )

        if not self.collides(next_x, grid):
            self.pos = next_x

        next_y = Vec(
            (
                self.pos.x,
                self.pos.y + movement.y,
            )
        )

        if not self.collides(next_y, grid):
            self.pos = next_y

    def move_backward(self):
        self.pos = self.pos - (self.direction * self.move_speed)
