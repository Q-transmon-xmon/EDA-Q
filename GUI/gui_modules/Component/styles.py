def get_component_styles():
    """
    Returns a style dictionary for quantum component library UI elements.
    """
    return {
        "category_header": """  
            QPushButton {  
                text-align: left;  
                padding: 8px 12px;  /* Top/Bottom: 8px, Left/Right: 12px */
                font-weight: bold;  
                font-size: 15px;  
                background-color: #f0f0f0;  /* Light gray background */
                min-width: 320px;  /* Minimum width for headers */
            }  
        """,
        "component_button": """  
            QPushButton {  
                padding: 8px 4px;  /* More vertical, less horizontal padding */
                text-align: center;  
                border-radius: 4px;  /* Slightly rounded corners */
                min-width: 160px;  /* Wider buttons for long names */
                min-height: 40px;  /* Taller buttons for better click target */
                font-size: 15px;  /* Consistent readable font size */
                border: 1px solid #d0d0d0;  /* Light gray border */
                margin: 2px;  /* Small margin between buttons */
            }  
            QPushButton:hover {  
                background-color: #e0e0e0;  /* Light hover effect */
            }  
        """,
        "container_layout": {
            "margins": (12, 6, 12, 12),  # (left, top, right, bottom)
            "spacing": (12, 12)  # (horizontal, vertical) spacing
        }
    }