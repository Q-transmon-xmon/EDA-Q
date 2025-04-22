# gds_processor.py
import importlib


class GDSProcessor:
    @staticmethod
    def parse_gds(path, components_type):
        """
        解析GDS文件并生成对应组件的核心方法
        :param path: GDS文件路径
        :param components_type: 用户指定的组件类型（如 "cpw_components"）
        """
        # 这里实现实际的GDS解析逻辑
        print(f"Reading GDS file from path: {path}")

        # 组件解析并自动生成组件文件（假设这些函数在工具箱中已实现）
        import toolbox
        toolbox.generate_python_class_from_gds(path, "")

        # 动态加载组件模块
        components_module = importlib.import_module(f"library.{components_type}")
        new_component_module_name = toolbox.get_filename(path)

        # 更新组件模块列表
        components_module.module_name_list.append(new_component_module_name)

        # 动态添加组件类
        new_component_class_name = toolbox.convert_to_camel_case(new_component_module_name)
        new_component_module = importlib.import_module(new_component_module_name)
        new_component_class = getattr(new_component_module, new_component_class_name)
        setattr(components_module, new_component_class_name, new_component_class)

        print(f"组件已成功添加到 {components_type} 类别，"
              f"新组件类名：{new_component_class_name}")
        return True