from pathlib import Path
from typing import Optional

def get_icon_path(*subpaths) -> Path:
    """
    Get the absolute path of a file under the GUI/icons directory.
    :param subpaths: Relative path parts from the icons directory (multiple arguments accepted)
    :example: get_icon_path("logo", "logo.png")
    :return: The concatenated Path object
    """
    try:
        # Get the absolute path of the current file (based on the module location)
        current_file = Path(__file__).resolve()
        # Locate the GUI directory (parent of testcode)
        gui_root = current_file.parent.parent
        # Concatenate the target path
        target_path = gui_root / "icons" / Path().joinpath(*subpaths)
        if not target_path.exists():
            raise FileNotFoundError(f"The specified path does not exist: {target_path}")
        return target_path
    except Exception as e:
        raise ValueError(f"Error occurred while getting the icon path: {e}") from e

def move_to_icons(file_path: Path) -> None:
    """
    Move the specified file to the icons directory.
    :param file_path: Path object of the file to be moved
    """
    try:
        # Check if the file exists
        if not file_path.exists():
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        target_path = get_icon_path(file_path.name)
        if not target_path.parent.exists():
            target_path.parent.mkdir(parents=True)

        file_path.rename(target_path)
        print(f"File {file_path} has been successfully moved to {target_path}")
    except Exception as e:
        raise ValueError(f"Error occurred while moving the file: {e}") from e

# Example usage
if __name__ == "__main__":
    # Get the path of logo.png under the icons directory
    try:
        logo_path = get_icon_path("logo", "logo.png")
        print("Logo path:", logo_path)
    except ValueError as e:
        print(e)

    # Example of moving a file (requires the actual file to exist)
    try:
        source_file = Path("example.txt")
        if source_file.exists():
            move_to_icons(source_file)
    except ValueError as e:
        print(e)