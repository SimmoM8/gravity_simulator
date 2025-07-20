def add_object(manager, objects, ui_manager):
    import pygame
    from object import Object
    from utils import random_color

    name = ui_manager.get("name_input").get_text()
    mass = float(ui_manager.get("mass_input").get_text() or 1)
    radius = float(ui_manager.get("radius_input").get_text() or 5)
    x, y = 100, 100  # default position
    vx, vy = 0, 0  # default velocity

    obj = Object(name, mass, radius, (x, y), (vx, vy), color=random_color())
    objects.append(obj)
    ui_manager.get("object_list").set_item_list([o.name for o in objects])


def delete_object(objects, selected_object, ui_manager):
    if selected_object in objects:
        objects.remove(selected_object)
        ui_manager.get("object_list").set_item_list([o.name for o in objects])


def update_selected_object(selected_object, ui_manager):
    if not selected_object:
        return

    name = ui_manager.get("name_input").get_text()
    mass = float(ui_manager.get("mass_input").get_text() or selected_object.mass)
    radius = float(ui_manager.get("radius_input").get_text() or selected_object.radius)

    selected_object.name = name
    selected_object.mass = mass
    selected_object.radius = radius
    ui_manager.get("object_list").set_item_list([o.name for o in ui_manager.get("object_list").item_list])