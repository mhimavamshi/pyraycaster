import math
import pygame

from ray import Ray, Vec
from player import Player
from grid import Grid


BACKGROUND = (10, 12, 20)

CEILING_COLOR = (90, 140, 255)
FLOOR_COLOR = (34, 44, 34)

WALL_COLOR_X = (180, 190, 255)
WALL_COLOR_Y = (120, 140, 220)
WALL_COLOR_CORNER = (255, 255, 255)

FOG_DISTANCE = 900


class Renderer:
    def __init__(
        self,
        surface,
        player,
        grid,
        num_rays=120,
        fov=math.radians(60),
        max_steps=100,
    ):
        self.surface = surface

        self.player = player
        self.grid = grid

        self.width, self.height = surface.get_size()

        self.num_rays = num_rays
        self.fov = fov

        self.max_steps = max_steps

        self.WALL_HEIGHT = 100

        self.column_width = math.ceil(self.width / self.num_rays)

        self.projection_plane_distance = (self.width / 2) / math.tan(self.fov / 2)

    def generate_rays(self):
        rays = []

        start_angle = self.player.angle - (self.fov / 2)

        angle_step = self.fov / self.num_rays

        for i in range(self.num_rays):
            angle = start_angle + (i * angle_step)

            direction = (
                math.cos(angle),
                math.sin(angle),
            )

            ray = Ray(
                dir_vec=direction,
                start_pos=self.player.pos.tup(),
            )

            rays.append((angle, ray))

        return rays

    def draw_background(self):

        pygame.draw.rect(
            self.surface,
            CEILING_COLOR,
            (
                0,
                0,
                self.width,
                self.height // 2,
            ),
        )

        pygame.draw.rect(
            self.surface,
            FLOOR_COLOR,
            (
                0,
                self.height // 2,
                self.width,
                self.height // 2,
            ),
        )

    def get_wall_color(self, side):
        if side == "x":
            return WALL_COLOR_X

        elif side == "y":
            return WALL_COLOR_Y

        return WALL_COLOR_CORNER

    def apply_distance_shading(
        self,
        color,
        distance,
    ):
        fog = min(distance / FOG_DISTANCE, 1)

        brightness = 1 - fog

        return (
            int(color[0] * brightness),
            int(color[1] * brightness),
            int(color[2] * brightness),
        )

    def render_column(
        self,
        column_index,
        ray_angle,
        cast_result,
    ):

        if not cast_result.is_wall:
            return

        corrected_distance = cast_result.distance * math.cos(
            ray_angle - self.player.angle
        )

        corrected_distance = max(
            corrected_distance,
            0.0001,
        )

        wall_height = (
            self.projection_plane_distance / corrected_distance
        ) * self.WALL_HEIGHT

        x = column_index * self.column_width

        y = self.height / 2 - wall_height / 2

        color = self.get_wall_color(cast_result.side)

        color = self.apply_distance_shading(
            color,
            corrected_distance,
        )

        pygame.draw.rect(
            self.surface,
            color,
            (
                x,
                y,
                self.column_width + 1,
                wall_height,
            ),
        )

    def render(self):
        self.draw_background()

        rays = self.generate_rays()

        for column_index, (ray_angle, ray) in enumerate(rays):
            results = ray.cast(
                self.grid,
                max_steps=self.max_steps,
            )

            if not results:
                continue

            final_result = results[-1]

            self.render_column(
                column_index,
                ray_angle,
                final_result,
            )


class RaycasterApp:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((900, 700))
        pygame.display.set_caption("DDA Raycaster")

        self.clock = pygame.time.Clock()

        self.grid = Grid()
        self.grid.set_walls(
            {
                (-8, -8),
                (-7, -8),
                (-6, -8),
                (-5, -8),
                (-4, -8),
                (-3, -8),
                (-2, -8),
                (-1, -8),
                (0, -8),
                (1, -8),
                (2, -8),
                (3, -8),
                (4, -8),
                (5, -8),
                (6, -8),
                (7, -8),
                (-8, 8),
                (-7, 8),
                (-6, 8),
                (-5, 8),
                (-4, 8),
                (-3, 8),
                (-2, 8),
                (-1, 8),
                (0, 8),
                (1, 8),
                (2, 8),
                (3, 8),
                (4, 8),
                (5, 8),
                (6, 8),
                (7, 8),
                (-8, -7),
                (-8, -6),
                (-8, -5),
                (-8, -4),
                (-8, -3),
                (-8, -2),
                (-8, -1),
                (-8, 0),
                (-8, 1),
                (-8, 2),
                (-8, 3),
                (-8, 4),
                (-8, 5),
                (-8, 6),
                (-8, 7),
                (7, -7),
                (7, -6),
                (7, -5),
                (7, -4),
                (7, -3),
                (7, -2),
                (7, -1),
                (7, 0),
                (7, 1),
                (7, 2),
                (7, 3),
                (7, 4),
                (7, 5),
                (7, 6),
                (7, 7),
                (0, 0),
                (1, 0),
                (2, 0),
                (2, 1),
                (2, 2),
                (-3, 2),
                (-2, 2),
                (-1, 2),
                (-4, -3),
                (-4, -2),
                (-4, -1),
                (4, -4),
                (5, -4),
                (6, -4),
                (3, 4),
                (3, 5),
                (3, 6),
            }
        )

        self.player = Player(
            pos=(0, 0),
            angle=0,
        )

        self.base_fov = math.radians(120)

        self.renderer = Renderer(
            self.screen, self.player, self.grid, num_rays=240, fov=self.base_fov
        )

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.base_fov -= math.radians(4)

                    elif event.y < 0:
                        self.base_fov += math.radians(4)

                    self.base_fov = max(
                        math.radians(30),
                        min(
                            math.radians(150),
                            self.base_fov,
                        ),
                    )

                    self.renderer.fov = self.base_fov

                    self.renderer.projection_plane_distance = (
                        self.renderer.width / 2
                    ) / math.tan(self.renderer.fov / 2)

            keys = pygame.key.get_pressed()

            if keys[pygame.K_a]:
                self.player.rotate_right()

            if keys[pygame.K_d]:
                self.player.rotate_left()

            if keys[pygame.K_w]:
                self.player.move_forward()

            if keys[pygame.K_s]:
                self.player.move_backward()

            right_dir = Vec(
                (
                    -self.player.direction.y,
                    self.player.direction.x,
                )
            ).normalized()

            if keys[pygame.K_q]:
                self.player.pos = self.player.pos - (right_dir * self.player.move_speed)

            if keys[pygame.K_e]:
                self.player.pos = self.player.pos + (right_dir * self.player.move_speed)

            self.screen.fill((8, 10, 18))

            self.renderer.render()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    app = RaycasterApp()
    app.run()
