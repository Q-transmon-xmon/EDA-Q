from addict import Dict
import copy, gdspy
from base.base import Base
import toolbox

class GdsBase(Base):
    """
    Includes various methods for displaying layouts and generating libs, serving as the base class for all GDS objects.
    """
    def __init__(self):
        return

    def show_gds(self):
        """
        Display the GDS layout corresponding to the lib.

        Dependent on the lib, subclasses using this method must include a method for generating the lib.
        """
        self.draw_gds()
        gdspy.LayoutViewer(library=self.lib)
        return

    def save_svg(self, width: int = 500, path: str = None):
        """
        Save the GDS layout corresponding to the lib as an SVG image.

        Input:
            width: The width of the image, from the leftmost coordinate to the rightmost coordinate of all components.
            path: The path to save the SVG image.

        Output:
            None

        Dependent on the lib, subclasses using this method must include a method for generating the lib.
        """
        self.draw_gds()
        # Default path
        if path is None:
            path = "./svg/{}.svg".format(self.__class__.__name__)

        toolbox.delete_file_if_exists(path=path)  # Avoid displaying the previous generation result when saving SVG fails, causing confusion.

        toolbox.save_svg(self.cell, width=width, path=path)

        return

    def show_svg(self, width: int = 500, path: str = None):
        """
        Display the GDS layout corresponding to the lib as an SVG image.

        Dependent on the lib, subclasses using this method must include a method for generating the lib.
        """
        self.draw_gds()

        # Default path
        if path is None:
            path = "./svg/{}.svg".format(self.__class__.__name__)

        toolbox.delete_file_if_exists(path=path)  # Avoid displaying the previous generation result when saving SVG fails, causing confusion.

        # Save SVG image
        toolbox.save_svg(self.cell, width=width, path=path)

        # Display SVG image
        from IPython.display import SVG
        from IPython.display import display
        display(SVG(path))

        return

    def save_gds(self, path: str = "./gds.gds"):
        """
        Save the GDS layout to a GDS file.

        Input:
            path: The path to save the GDS file.

        Output:
            The path where the GDS file is saved.
        """
        self.draw_gds()
        toolbox.jg_and_create_path(path)
        self.lib.write_gds(outfile=path)
        return path