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

        self.minimap_enabled = True

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

    def get_wall_color(self, wall, side):
        if side == "x":
            return self.grid.get_wall_color(wall, WALL_COLOR_X)
            # return WALL_COLOR_X

        elif side == "y":
            return self.apply_y_shading(self.grid.get_wall_color(wall, WALL_COLOR_X))

        return WALL_COLOR_CORNER

    def apply_y_shading(self, color):
        shade = 0.7

        return (
            int(color[0] * shade),
            int(color[1] * shade),
            int(color[2] * shade),
        )

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

        color = self.get_wall_color(cast_result.cell, cast_result.side)

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

    def draw_walls(self):
        rays = self.generate_rays()

        cast_results = []

        for column_index, (ray_angle, ray) in enumerate(rays):
            results = ray.cast(
                self.grid,
                max_steps=self.max_steps,
            )

            if not results:
                continue

            final_result = results[-1]

            cast_results.append(
                {
                    "ray_angle": ray_angle,
                    "ray": ray,
                    "hit": final_result.hit,
                    "steps": results,
                }
            )

            self.render_column(
                column_index,
                ray_angle,
                final_result,
            )

        return cast_results

    def world_to_minimap(
        self,
        world_pos,
        player_pos,
        minimap_center,
        scale,
    ):

        rel_x = world_pos[0] - player_pos[0]
        rel_y = world_pos[1] - player_pos[1]

        return (
            minimap_center[0] + rel_x * scale,
            minimap_center[1] - rel_y * scale,
        )


    def draw_minimap(self, cast_results):

        minimap_size = 220
        minimap_padding = 20
        minimap_scale = 0.24

        minimap_surface = pygame.Surface(
            (minimap_size, minimap_size),
            pygame.SRCALPHA,
        )

        minimap_surface.fill((15, 18, 26, 235))

        minimap_center = (
            minimap_size // 2,
            minimap_size // 2,
        )

        player_pos = self.player.pos.tup()

        for wall in self.grid.walls:

            wx, wy = self.grid.cell_to_world(wall)

            mx, my = self.world_to_minimap(
                (wx, wy),
                player_pos,
                minimap_center,
                minimap_scale,
            )

            wall_size = self.grid.CELL_WIDTH * minimap_scale

            rect = pygame.Rect(
                mx,
                my - wall_size,
                wall_size,
                wall_size,
            )

            color = self.grid.get_wall_color(wall, (180, 180, 180))

            pygame.draw.rect(
                minimap_surface,
                color,
                rect,
            )

        every_nth_ray = 3

        for cast in cast_results[::every_nth_ray]:

            hit = cast["hit"]

            hit_minimap = self.world_to_minimap(
                hit,
                player_pos,
                minimap_center,
                minimap_scale,
            )

            pygame.draw.line(
                minimap_surface,
                (255, 255, 120),
                minimap_center,
                hit_minimap,
                1,
            )

        pygame.draw.circle(
            minimap_surface,
            (80, 255, 120),
            (
                int(minimap_center[0]),
                int(minimap_center[1]),
            ),
            5,
        )

        dir_length = 20

        direction_end = (
            minimap_center[0]
            + math.cos(self.player.angle) * dir_length,
            minimap_center[1]
            - math.sin(self.player.angle) * dir_length,
        )

        pygame.draw.line(
            minimap_surface,
            (80, 255, 120),
            minimap_center,
            direction_end,
            3,
        )

        pygame.draw.rect(
            minimap_surface,
            (255, 255, 255),
            minimap_surface.get_rect(),
            2,
        )

        self.surface.blit(
            minimap_surface,
            (
                minimap_padding,
                minimap_padding,
            ),
        )

    def toggle_minimap(self):
        self.minimap_enabled = not self.minimap_enabled

    def render(self):
        self.draw_background()  
        cast_results = self.draw_walls()
        if self.minimap_enabled:
            self.draw_minimap(cast_results)


        


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


        self.grid.set_wall_colors(
            [
                ((0, 0), (255, 80, 80)),
                ((1, 0), (255, 80, 80)),
                ((2, 0), (255, 80, 80)),
                ((2, 1), (255, 80, 80)),
                ((2, 2), (255, 80, 80)),
            ]
        )

        self.player = Player(
            pos=(0, 0),
            angle=0,
        )

        self.base_fov = math.radians(60)

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

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.renderer.toggle_minimap()

            keys = pygame.key.get_pressed()

            if keys[pygame.K_a]:
                self.player.rotate_left()

            if keys[pygame.K_d]:
                self.player.rotate_right()

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
