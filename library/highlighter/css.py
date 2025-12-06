from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # Css syntax colors
        self.syntax_colors.update({
            "selector": "#D7BA7D",
            "property": "#9CDCFE",
            "value": "#CE9178",
            "unit": "#B5CEA8",
            "color": "#CE9178",
            "number": "#B5CEA8",
            "important": "#569CD6",
            "media": "#C586C0"
        })
        
        # CSS property and value keywords
        self.properties = {
            "color", "background", "margin", "padding", "border", "font",
            "width", "height", "display", "position", "top", "left", "right",
            "bottom", "float", "clear", "text-align", "vertical-align"
        }
        
        self.values = {
            "none", "block", "inline", "flex", "grid", "absolute", "relative",
            "fixed", "static", "inherit", "initial", "auto", "hidden", "visible"
        }
        
        self.setup_tags() 
