def screen_to_world(origin, point):
    return (point[0] - origin[0], origin[1] - point[1])


def world_to_screen(origin, point):
    return (origin[0] + point[0], origin[1] - point[1])


def world_to_screen_centre(surface, point):
    w, h = surface.get_size()
    return world_to_screen((w // 2, h // 2), point)


def world_to_screen_cam(surface, camera_pos, world_pos):
    w, h = surface.get_size()

    rel_x = world_pos[0] - camera_pos[0]
    rel_y = world_pos[1] - camera_pos[1]

    return (
        w // 2 + rel_x,
        h // 2 - rel_y,
    )

def screen_to_world_cam(surface, camera_pos, screen_pos):
    w, h = surface.get_size()

    return (
        camera_pos[0] + (screen_pos[0] - w // 2),
        camera_pos[1] - (screen_pos[1] - h // 2),
    )
