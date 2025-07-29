class UIPage:
    """
    Represents a UI page consisting of multiple UI elements.

    The UIPage class serves as a container for a group of UI elements that together form a page or screen
    within the user interface. It provides methods to show or hide all elements collectively, enabling easy
    management of the page's visibility state.

    Attributes:
        elements (list): A list of UI elements that belong to this page.
    """

    def __init__(self, elements):
        """
        Initialize the UIPage with a list of UI elements.

        Args:
            elements (list): The UI elements to include in this page.
        """
        self.elements = elements

    def show(self):
        """
        Show all elements on the page.

        This method iterates through all the elements contained in the page and calls their individual
        'show' method to make them visible. Grouping show/hide operations simplifies managing the entire
        page's visibility as a single unit.
        """
        for element in self.elements:
            element.show()

    def hide(self):
        """
        Hide all elements on the page.

        This method iterates through all the elements contained in the page and calls their individual
        'hide' method to make them invisible. Grouping show/hide operations simplifies managing the entire
        page's visibility as a single unit.
        """
        for element in self.elements:
            element.hide()
