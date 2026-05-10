import pygame
import math

from coordinate_mapper import screen_to_world, world_to_screen_centre
from grid import Grid
from player import Player
from ray import Ray

pygame.init()

DIMS = (900, 700)
FPS = 60

BACKGROUND = "black"

RAY_LENGTH = 2000
MAX_STEPS = 100

NUM_RAYS = 60
FOV = math.radians(60)

PLAYER_COLOR = "cyan"
HIT_COLOR = "red"

screen = pygame.display.set_mode(DIMS)
clock = pygame.time.Clock()


def draw_player(surface, player):
    screen_pos = world_to_screen_centre(surface, player.pos.tup())

    pygame.draw.circle(surface, PLAYER_COLOR, screen_pos, 8)

    facing = player.pos + (player.direction * 25)

    pygame.draw.line(
        surface,
        PLAYER_COLOR,
        screen_pos,
        world_to_screen_centre(surface, facing.tup()),
        2
    )


def generate_rays(player):
    rays = []

    start_angle = player.angle - (FOV / 2)
    angle_step = FOV / NUM_RAYS

    for i in range(NUM_RAYS):
        angle = start_angle + (i * angle_step)

        direction = (
            math.cos(angle),
            math.sin(angle)
        )

        ray = Ray(
            dir_vec=direction,
            start_pos=player.pos.tup()
        )

        rays.append(ray)

    return rays


def draw_ray_hits(surface, results):
    for result in results:
        hit_pos = world_to_screen_centre(surface, result.hit)

        pygame.draw.circle(surface, HIT_COLOR, hit_pos, 3)

        if result.is_wall:
            pygame.draw.circle(surface, "yellow", hit_pos, 5)


def main():
    grid = Grid()

    grid.set_walls({
        (3, 0),
        (3, 1),
        (3, 2),
        (3, 3),

        (0, 4),
        (1, 4),
        (2, 4),

        (-2, -2),
        (-2, -1),
        (-2, 0),

        (5, -3),
        (6, -3),
        (7, -3),
    })

    player = Player(
        pos=(0, 0),
        angle=0
    )

    running = True

    while running:
        # dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                world_pos = screen_to_world(
                    (DIMS[0] // 2, DIMS[1] // 2),
                    event.pos
                )

                cell = grid.world_to_cell(world_pos)

                if event.button == 1:
                    grid.add_wall(cell)

                elif event.button == 3:
                    grid.remove_wall(cell)


        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            player.rotate_left()

        if keys[pygame.K_d]:
            player.rotate_right()

        if keys[pygame.K_w]:
            player.move_forward()

        if keys[pygame.K_s]:
            player.move_backward()


        rays = generate_rays(player)

        screen.fill(BACKGROUND)

        grid.draw(screen)

        draw_player(screen, player)

        for ray in rays:

            results = ray.cast(
                grid,
                max_steps=MAX_STEPS
            )

            if results:
                final_hit = results[-1].hit
            else:
                final_hit = ray.endpoint(RAY_LENGTH).tup()

            pygame.draw.line(
                screen,
                "orange",
                world_to_screen_centre(screen, player.pos.tup()),
                world_to_screen_centre(screen, final_hit),
                1
            )

            draw_ray_hits(screen, results)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()