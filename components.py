import pygame
import pygame_gui
from config import SIDEBAR_WIDTH, PADDING, MARGIN, WINDOW_WIDTH, LABEL_INPUT_GAP

# Mapping of element type strings to their corresponding pygame_gui classes
ELEMENT_CLASSES = {
    'button': pygame_gui.elements.UIButton,
    'label': pygame_gui.elements.UILabel,
    'text_input': pygame_gui.elements.UITextEntryLine,
    'slider': pygame_gui.elements.UIHorizontalSlider,
    'selection_list': pygame_gui.elements.UISelectionList,
    'text_box': pygame_gui.elements.UITextBox,
    'dropdown': pygame_gui.elements.UIDropDownMenu,
}

# Metadata for each element type, such as default heights
ELEMENT_META = {
    'button': {'default_height': 40},
    'label': {'default_height': 30},
    'text_input': {'default_height': 30},
    'slider': {'default_height': 30},
    'selection_list': {'default_height': 150},
    'dropdown': {'default_height': 30},
}

def create_element_class(element_type, manager, width=None, height=None, **kwargs):
    cls = ELEMENT_CLASSES.get(element_type)
    if cls is None:
        # Unknown element type; cannot create element
        return None

    # Set default width if not provided
    if width is None:
        width = SIDEBAR_WIDTH - 2 * MARGIN
    # Set default height based on element type metadata
    if height is None:
        height = ELEMENT_META.get(element_type, {}).get('default_height', 30)

    # Base keyword arguments for element creation, including position and manager
    element_kwargs = {
        'relative_rect': pygame.Rect((0, 0), (width, height)),
        'manager': manager,
    }

    # Add type-specific properties to element creation kwargs
    if element_type == 'button' or element_type == 'label':
        # Provide default text if not specified
        element_kwargs['text'] = kwargs.get('text', 'Button' if element_type == 'button' else 'Label')
    if element_type == 'slider':
        # Slider requires start value and value range (min_val, max_val)
        element_kwargs['start_value'] = kwargs.get('start_value', 50)
        element_kwargs['value_range'] = (kwargs.get('min_val', 0), kwargs.get('max_val', 100))
    if element_type == 'selection_list':
        element_kwargs['item_list'] = kwargs.get('item_list', [])
    if element_type == 'text_box':
        # Use html_text instead of text
        element_kwargs['html_text'] = kwargs.get('text', '')  # fallback to 'text' key if html_text missing
    if element_type == 'dropdown':
        options = kwargs.get('options', [])
        if not options:
            return None  # Skip creating if no options provided
        default_option = options[0]
        element_kwargs['options_list'] = options
        element_kwargs['starting_option'] = default_option


    # Instantiate the UI element
    element = cls(**element_kwargs)

    # Apply common properties such as element name and visibility
    apply_common_properties(element, kwargs)
    return element

def apply_common_properties(element, props):
    name = props.get('name')
    if name:
        element.element_name = name  # Assign a custom name to the element for lookup
    visible = props.get('visible', True)
    if not visible:
        element.hide()  # Hide element if visibility is set to False

def _create_element(edef, manager):
    """
    Helper function to create a UI element from its definition dictionary

    Parameters:
        edef (dict): Element definition containing 'type' and other properties.
        manager (pygame_gui.UIManager): The UI manager to assign to the element.

    Returns:
        pygame_gui element instance or None if type is unknown.
    """
    etype = edef.get('type')
    kwargs = edef.copy()
    kwargs.pop('type', None)

    if etype == 'dropdown':
        options = edef.get('options')
        options_source_key = edef.get('options_source')
        if options_source_key and not options:
            # Import here to avoid circular imports
            from data_sources import get_options
            kwargs['options'] = get_options(options_source_key)

        if not kwargs.get('options'):
            return None  # Skip creating dropdown if no options available

    element = create_element_class(etype, manager, **kwargs)

    if 'label' in edef:
        label_text = edef['label']
        label_kwargs = {
            'type': 'label',
            'text': label_text,
            'name': edef['name'] + "_label"
        }
        label_element = create_element_class('label', manager, **label_kwargs)
        apply_common_properties(label_element, label_kwargs)
        return [label_element, element]
    else:
        return [element]
    
def _layout_vertical(manager, element_defs, start_x, start_y):
    """
    Layout elements stacked vertically from top to bottom.

    Parameters:
        manager (pygame_gui.UIManager): The UI manager.
        element_defs (list): List of element definition dicts.
        start_x (int): Starting x-coordinate for layout.
        start_y (int): Starting y-coordinate for layout.
        padding (int): Space between elements.
        margin (int): Margin from the starting x-coordinate.
        width (int): Width to assign to each element.

    Returns:
        list: List of created and positioned UI elements.
    """
    elements = []
    current_y = start_y
    for edef in element_defs:
        els = _create_element(edef, manager)
        if not els:
            continue
        for el in els:
            el.set_relative_position((start_x + MARGIN, current_y))
            elements.append(el)
            current_y += el.rect.height + PADDING
    return elements

def _layout_horizontal(manager, element_defs, start_x, start_y, parent_height):
    """
    Layout elements horizontally with support for left, center, and right alignment groups.

    Parameters:
        manager (pygame_gui.UIManager): The UI manager.
        element_defs (list): List of element definition dicts.
        start_x (int): Starting x-coordinate for layout.
        start_y (int): Starting y-coordinate for layout.
        padding (int): Space between elements.
        margin (int): Margin from the starting x-coordinate.
        width (int): Width to assign to each element.
        parent_height (int): Height of the parent rectangle for vertical centering.

    Returns:
        list: List of created and positioned UI elements in the order they were created.
    """
    # Partition element_defs into left, center, right groups
    left_defs = []
    center_defs = []
    right_defs = []
    for edef in element_defs:
        align = edef.get('align', 'left')
        if align == 'center':
            center_defs.append(edef)
        elif align == 'right':
            right_defs.append(edef)
        else:
            left_defs.append(edef)

    # Create all elements first, keeping their order and original definition
    left_elements = []
    center_elements = []
    right_elements = []
    element_map = {}  # edef id to element, for output order
    # Helper for creation and storing
    def create_group(defs, group_elements):
        for edef in defs:
            els = _create_element(edef, manager)
            if els:
                for el in els:
                    group_elements.append((edef, el))
                    element_map[id(edef)] = el
    create_group(left_defs, left_elements)
    create_group(center_defs, center_elements)
    create_group(right_defs, right_elements)

    # Compute total widths for each group (including padding)
    def group_width(group):
        if not group:
            return 0
        return sum(el.rect.width for _, el in group) + PADDING * (len(group) - 1)

    left_w = group_width(left_elements)
    center_w = group_width(center_elements)
    right_w = group_width(right_elements)

    # Place left group: left to right from (start_x + margin)
    prev_edef = None
    lx = start_x + MARGIN
    for _, el in left_elements:
        y = start_y + (parent_height - el.rect.height) // 2
        el.set_relative_position((lx, y))
        if prev_edef == _:
            lx += el.rect.width + LABEL_INPUT_GAP
        else:
            lx += el.rect.width + PADDING
        prev_edef = _

    # Place right group: right to left from (start_x + WINDOW_WIDTH - margin)
    prev_edef = None
    rx = start_x + WINDOW_WIDTH - MARGIN
    for _, el in reversed(right_elements):
        rx -= el.rect.width
        y = start_y + (parent_height - el.rect.height) // 2
        el.set_relative_position((rx, y))
        if prev_edef == _:
            rx -= LABEL_INPUT_GAP
        else:
            rx -= PADDING
        prev_edef = _

    # Place center group: centered in remaining space between left and right groups
    prev_edef = None
    left_edge = start_x + MARGIN + left_w
    right_edge = start_x + WINDOW_WIDTH - MARGIN - right_w
    center_space = max(0, right_edge - left_edge)
    cx = left_edge + (center_space - center_w) // 2 if center_w <= center_space else left_edge
    for _, el in center_elements:
        y = start_y + (parent_height - el.rect.height) // 2
        el.set_relative_position((cx, y))
        if prev_edef == _:
            cx += el.rect.width + LABEL_INPUT_GAP
        else:
            cx += el.rect.width + PADDING
        prev_edef = _

    # Return elements in the order they were created (original element_defs order)
    result = []
    for edef in element_defs:
        el = element_map.get(id(edef))
        if el is not None:
            result.append(el)
    return result

def auto_layout_elements(manager, element_defs, parent_rect, layout):
    """
    Dispatcher function to layout UI elements either vertically or horizontally.

    Parameters:
        manager (pygame_gui.UIManager): The UI manager.
        element_defs (list): List of element definition dicts.
        parent_rect (pygame.Rect): The parent rectangle to base layout positioning on.
        layout (str): Layout direction, either "vertical" or "horizontal".

    Returns:
        list: List of created and positioned UI elements.
    """
    start_x = parent_rect.x + PADDING
    start_y = parent_rect.y + PADDING

    if layout == "horizontal":
        return _layout_horizontal(manager, element_defs, start_x, start_y, parent_rect.height)
    else:
        return _layout_vertical(manager, element_defs, start_x, start_y)