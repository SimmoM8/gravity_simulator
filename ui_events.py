import pygame
import pygame_gui
from ui_actions import *

def handle_event(event, ui, sim):
    manager = ui["manager"]
    selected_object = sim["selected_object"]

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            handle_mouse_click(event.pos, ui, sim)

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            sim["dragging_object"] = None

    elif event.type == pygame.MOUSEMOTION:
        if sim.get("dragging_object"):
            handle_mouse_drag(event.pos, ui, sim)

    elif event.type == pygame.USEREVENT:
        if event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            print("mode:", sim["ui_mode"])
            if sim["ui_mode"] == "edit":
                update_selected_object(ui, sim)

        elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            handle_button_press(event.ui_element, ui, sim)

        elif event.user_type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            handle_selection(event.text, ui, sim)

        elif event.user_type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION:
            deselect_object(ui, sim)

        elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            handle_slider_change(event.ui_element, ui, sim)


    manager.process_events(event)