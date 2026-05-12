# Export/Import Map data; map i/o
# Level Editor creates UI/UX to make maps
# extensible for future: textures and ceiling and floors and metadata

# freely moving camera, mouse controls to lay down walls, selecting a wall and editing its metadata in a surface
# is pygame a good idea? or should i use ui/ux
# origin is player's start point

# only 2D for now

import os
import pygame
import math
import json
from dataclasses import dataclass, asdict
from grid import Grid, Wall
from player import Player
from ray import Vec

pygame.font.init()
font = pygame.font.SysFont("Arial", 10)
player_text_surface = font.render("P", True, (255, 255, 255))

@dataclass(slots=True)
class ImportedData:
    grid: Grid
    player: Player | None = None

class MapStore:
    def __init__(self):
        self.walls = {}
        self.player_position = (1, 1)

    def add_wall(self, wall):
        self.walls[wall.cell] = wall

    def remove_wall(self, cell):
        del self.walls[cell]

    def print_all(self):
        print(self.walls, self.player_position)

    def place_player(self, world_position):
        self.player_position = world_position

    def get_player(self):
        return self.player_position

    def export(self, name):
        DIR = "./maps"
        filename = f"{DIR}/{name}.json"
        os.makedirs(DIR, exist_ok=True)
        data = {str(cell): asdict(wall) for cell, wall in self.walls.items()} | {"player": self.player_position}
        with open(filename, "w") as fl:
            json.dump(data, fl)
        print(f"EXPORTED MAP: {filename}")

    @staticmethod
    def file_exists(name):
        DIR = "./maps"
        filename = f"{DIR}/{name}.json"
        return os.path.exists(filename)

    @staticmethod
    def import_map(name, ImportedData):
        DIR = "./maps"
        filename = f"{DIR}/{name}.json"
        if not MapStore.file_exists(name):
            return 
        with open(filename) as fl:
            data = json.load(fl)
        if ImportedData.player: 
            ImportedData.player.pos = Vec(tuple(data["player"]))
        del data["player"]
        # remaining are wall metadata
        walls = [Wall(**wall) for _, wall in data.items()]
        ImportedData.grid.set_walls(walls)


class Camera:
    def __init__(self, pos=(0, 0)):
        self.pos = Vec(pos)

        self.move_speed = 5

    @property
    def x(self):
        return self.pos.x

    @property
    def y(self):
        return self.pos.y

    def move(self, delta: Vec):
        self.pos = self.pos + delta

    def world_to_screen(self, surface, world_pos):
        sx, sy = surface.get_size()
        cx, cy = self.pos.x, self.pos.y

        return (
            sx // 2 + (world_pos[0] - cx),
            sy // 2 - (world_pos[1] - cy),
        )

    def screen_to_world(self, surface, screen_pos):
        sx, sy = surface.get_size()
        cx, cy = self.pos.x, self.pos.y

        return (
            cx + (screen_pos[0] - sx // 2),
            cy - (screen_pos[1] - sy // 2),
        )


class LevelEditor:
    def __init__(self, map_name, import_file):
        pygame.init()
        self.WIDTH, self.HEIGHT = 700, 700
        DIMS = self.WIDTH, self.HEIGHT
        self.main_surface = pygame.display.set_mode(DIMS)
        pygame.display.set_caption("Level Editor")

        self.map_name = map_name

        self.grid = Grid()
        self.camera = Camera((0, 0))
        self.store = MapStore()

        data = ImportedData(self.grid)
        MapStore.import_map(import_file, data)

        self.show_gridlines = True

        self.mode = ["wall", "player"]
        self.curr_mode = 0

        self.brightness = 100
        self.hue = None

    def draw_background(self):
        BACKGROUND_COLOR = "black"
        self.main_surface.fill(BACKGROUND_COLOR)

    def draw_gridlines(self):
        left = self.camera.x - self.WIDTH // 2
        right = self.camera.x + self.WIDTH // 2
        bottom = self.camera.y - self.HEIGHT // 2
        top = self.camera.y + self.HEIGHT // 2

        start_x = math.floor(left / self.grid.CELL_WIDTH) * self.grid.CELL_WIDTH
        end_x = math.ceil(right / self.grid.CELL_WIDTH) * self.grid.CELL_WIDTH

        start_y = math.floor(bottom / self.grid.CELL_HEIGHT) * self.grid.CELL_HEIGHT
        end_y = math.ceil(top / self.grid.CELL_HEIGHT) * self.grid.CELL_HEIGHT

        self.grid.draw_grid_lines(
            self.main_surface,
            (start_x, end_x, start_y, end_y),
            project=self.camera.world_to_screen,
        )

    def highlight_hover(self):
        mouse_world = self.camera.screen_to_world(
            self.main_surface, pygame.mouse.get_pos()
        )
        self.hover_cell = self.grid.world_to_cell(mouse_world)
        self.grid.highlight_cell(self.hover_cell)

    def draw_origin_point(self):
        center = self.camera.world_to_screen(self.main_surface, (0, 0))
        pygame.draw.circle(self.main_surface, "orange", center, 6)

    def draw_player(self):
        x, y = self.camera.world_to_screen(self.main_surface, self.store.get_player())
        container = pygame.rect.Rect(
            x, y, 10, 10
        )
        player_text_rect = player_text_surface.get_rect(center=container.center)
        self.main_surface.blit(player_text_surface, player_text_rect)
        

    def run(self):
        running = True

        clock = pygame.time.Clock()

        FPS = 60

        while running:
            dt = clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    world_pos = self.camera.screen_to_world(
                        self.main_surface, event.pos
                    )

                    cell = self.grid.world_to_cell(world_pos)

                    if self.mode[self.curr_mode] == "wall":
                        wall = Wall(cell, (255, 255, 255))

                        # left click -> add wall
                        if event.button == 1:
                            self.grid.add_wall(wall)
                            self.store.add_wall(wall)

                        # right click -> remove wall
                        elif event.button == 3:
                            self.grid.remove_wall(cell)
                            self.store.remove_wall(cell)

                    if self.mode[self.curr_mode] == "player":
                        if event.button == 1:
                            print(
                                f"PLAYER POSITION: {self.store.get_player()} -> {world_pos}"
                            )
                            self.store.place_player(world_pos)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.show_gridlines = not self.show_gridlines

                    if event.key == pygame.K_m:
                        self.curr_mode = (self.curr_mode + 1) % len(self.mode)
                        print(f"CURRENT MODE: {self.mode[self.curr_mode]}")

                    if event.key == pygame.K_e:
                        self.store.export(self.map_name)
                    
                    if event.key == pygame.K_b:
                        self.brightness = (self.brightness + 10) % 100

            self.highlight_hover()

            keys = pygame.key.get_pressed()

            movement = Vec((0, 0))

            if keys[pygame.K_w]:
                movement = movement + Vec((0, 1))

            if keys[pygame.K_s]:
                movement = movement + Vec((0, -1))

            if keys[pygame.K_a]:
                movement = movement + Vec((-1, 0))

            if keys[pygame.K_d]:
                movement = movement + Vec((1, 0))

            if movement.magnitude() > 0:
                movement = movement.normalized() * self.camera.move_speed
                self.camera.move(movement)

            self.draw_background()

            if self.show_gridlines:
                self.draw_gridlines()

            self.grid.draw(self.main_surface, project=self.camera.world_to_screen)

            self.draw_origin_point()

            self.draw_player()

            pygame.display.flip()

            self.grid.clear_highlights()


if __name__ == "__main__":
    print("Press M to change modes.")
    print("Press E to export current map.")
    print("Use WASD to move.")
    print("Use Right and Left mouseclicks as per the mode.")
    map_name = input("Enter map name to save as: ")
    import_file = input("Import any map? [enter valid name/skip]: ")
    editor = LevelEditor(map_name, import_file)
    print(f"Available modes: {editor.mode}")
    editor.run()
