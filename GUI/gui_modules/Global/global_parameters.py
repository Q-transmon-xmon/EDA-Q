# global_parameters.py
from typing import Optional, Dict, Tuple
from api.design import Design

# Global data structure definitions (corrected)
global_designs: Dict[str, Tuple[Design, Optional[str]]] = {}  # Format: {design_name: (Design instance, path)}
current_design_name: Optional[str] = None  # Name of the currently selected design

def test():
    print("test", current_design_name)