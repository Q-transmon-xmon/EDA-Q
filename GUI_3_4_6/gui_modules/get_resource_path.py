import os

def get_resource_path(
        *path_parts: str,
        base_dir: str = "current",
        base_path: str = None,
        raise_on_missing: bool = True
) -> str:
    """
    Flexible path resolver with chainable directory navigation

    :param path_parts: Path components ("data", "config.yaml")
    :param base_dir: Initial base type ("current", "parent")
    :param base_path: Optional existing base path for chaining
    :param raise_on_missing: Raise error if path missing (default: True)
    :return: Verified absolute path
    """
    # Prefer the provided base_path (key for chaining)
    if base_path:
        base = base_path
    else:
        # Initial base path calculation
        script_path = os.path.abspath(__file__)
        if base_dir == "current":
            base = os.path.dirname(script_path)
        elif base_dir == "parent":
            base = os.path.dirname(os.path.dirname(script_path))
        else:
            raise ValueError(f"Unsupported base_dir: {base_dir}")

    # Build the full path
    full_path = os.path.join(base, *path_parts)
    full_path = os.path.normpath(full_path)

    # Path validation
    if raise_on_missing and not os.path.exists(full_path):
        raise FileNotFoundError(f"Path not found: {full_path}")

    return full_path