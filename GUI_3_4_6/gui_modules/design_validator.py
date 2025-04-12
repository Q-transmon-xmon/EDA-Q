# design_validator.py
import logging
from typing import Any, Dict, List, Optional, Callable
from PyQt5.QtCore import QObject


class DesignValidator(QObject):
    """Global design validator (singleton pattern) that supports dynamic registration of component validation rules."""

    _instance = None
    _registry = {}  # Component registry {component name: {check_func, error_template}}

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            # Initialize default component validation rules
            cls._registry = {
                'topology': {
                    'check_func': lambda d: not d.topology.positions,
                    'error_template': '{component} configuration is not initialized'
                },
                'gds': {
                    'check_func': lambda d: all(not v.options for v in d.gds.options.values()),
                    'error_template': '{component} configuration is not initialized'
                },
                'chip': {  # Modified check logic
                    'check_func': lambda d: not d.options().gds.chips,
                    'error_template': '{component} configuration is not initialized'
                }
            }
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True

    @classmethod
    def register_component(cls,
                           component: str,
                           check_func: Callable[[Any], bool],
                           error_template: Optional[str] = None):
        """
        Register or update component validation rules.
        Args:
            component: Component name
            check_func: Validation function (design: Any) -> bool
            error_template: Error message template, supports {component} placeholder
        """
        cls._registry[component] = {
            'check_func': check_func,
            'error_template': error_template or '{component} configuration is invalid'
        }

    def is_component_empty(self, design: Any, component: str) -> bool:
        """
        Check if a component is empty.
        Args:
            design: Design object
            component: Registered component name

        Raises:
            ValueError: Unregistered component type
        """
        if component not in self._registry:
            raise ValueError(f"Unregistered component type: {component}")
        return self._registry[component]['check_func'](design)

    def validate_components(self,
                            design: Any,
                            components: List[str],
                            stop_on_error: bool = False) -> Dict[str, str]:
        """
        Validate multiple components.
        Args:
            design: Design object
            components: List of components to check
            stop_on_error: Stop checking on the first error

        Returns:
            Error dictionary {component name: error description}
        """
        errors = {}
        for comp in components:
            try:
                if self.is_component_empty(design, comp):
                    template = self._registry[comp]['error_template']
                    errors[comp] = template.format(component=comp.capitalize())
                    if stop_on_error:
                        return errors
            except KeyError:
                error_msg = f"Unregistered component type: {comp}"
                errors[comp] = error_msg
                logging.warning(error_msg)
            except Exception as e:
                error_msg = f"{comp.capitalize()} validation failed: {str(e)}"
                errors[comp] = error_msg
                logging.exception(f"Component validation failed [{comp}]")  # Log full stack trace
                if stop_on_error:
                    return errors
        return errors


# Global singleton instance
design_validator = DesignValidator()