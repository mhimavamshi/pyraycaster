import pygame

pygame.font.init()
LABEL_FONT = pygame.font.SysFont("Arial", 20)
OFFSET = 10

COLOR = "white"

drawn_points = {}


def add_point(pos, label=None):
    if pos not in drawn_points:
        if not label:
            label = pos
        drawn_points[pos] = LABEL_FONT.render(str(label), True, COLOR)


def draw_points(surface):
    for pos, label_text in drawn_points.items():
        center = pos
        color, radius, width = COLOR, 4, 0
        pygame.draw.circle(surface, color, center, radius, width)

        label_pos = (pos[0] + OFFSET, pos[1] + OFFSET)
        surface.blit(label_text, label_pos)
