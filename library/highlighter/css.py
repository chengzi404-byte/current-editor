from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # CSS syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("selector", self.syntax_colors.get("class", "#D7BA7D"))
        self.syntax_colors.setdefault("property", self.syntax_colors.get("variable", "#9CDCFE"))
        self.syntax_colors.setdefault("value", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("unit", self.syntax_colors.get("number", "#B5CEA8"))
        self.syntax_colors.setdefault("color", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("number", self.syntax_colors.get("number", "#B5CEA8"))
        self.syntax_colors.setdefault("important", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("media", self.syntax_colors.get("decorator", "#C586C0"))
        
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
