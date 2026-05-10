import math
from ray import Vec


class Player:
    def __init__(self, pos=(0, 0), angle=0):
        self.pos = Vec(pos)

        self.angle = math.radians(angle)

        self.move_speed = 3
        self.turn_speed = math.radians(2)

    @property
    def direction(self):
        return Vec((math.cos(self.angle), math.sin(self.angle))).normalized()

    def rotate_left(self):
        self.angle += self.turn_speed

    def rotate_right(self):
        self.angle -= self.turn_speed

    def move_forward(self):
        self.pos = self.pos + (self.direction * self.move_speed)

    def move_backward(self):
        self.pos = self.pos - (self.direction * self.move_speed)
