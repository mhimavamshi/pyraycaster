def screen_to_world(origin, point):
    return (point[0] - origin[0], origin[1] - point[1])


def world_to_screen(origin, point):
    return (origin[0] + point[0], origin[1] - point[1])


def world_to_screen_centre(surface, point):
    w, h = surface.get_size()
    return world_to_screen((w // 2, h // 2), point)
