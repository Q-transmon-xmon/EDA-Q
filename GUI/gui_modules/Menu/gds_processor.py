# gds_processor.py
import importlib


class GDSProcessor:
    @staticmethod
    def parse_gds(path, components_type):
        """
        The core method for generating files and corresponding components
        :param path: GDS File Path
        :param components_type: User specified component type (in compliance with "cpw_components")
        """
        # Implement the actual GDS analysis logic here
        print(f"Reading GDS file from path: {path}")

        # Component parsing and automatic generation of component files (Assuming these functions have been implemented in the toolbox)
        import toolbox
        toolbox.generate_python_class_from_gds(path, "")

        # Dynamically load component modules
        components_module = importlib.import_module(f"library.{components_type}")
        new_component_module_name = toolbox.get_filename(path)

        # Update component module list
        components_module.module_name_list.append(new_component_module_name)

        # Dynamically add component classes
        new_component_class_name = toolbox.convert_to_camel_case(new_component_module_name)
        new_component_module = importlib.import_module(new_component_module_name)
        new_component_class = getattr(new_component_module, new_component_class_name)
        setattr(components_module, new_component_class_name, new_component_class)

        print(f"Component has been successfully added to the {components_type} category, "
              f"New component class name: {new_component_class_name}")
        return True