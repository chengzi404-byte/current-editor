from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # HTML syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("tag", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("attribute", self.syntax_colors.get("variable", "#9CDCFE"))
        self.syntax_colors.setdefault("string", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("comment", self.syntax_colors.get("comment", "#6A9955"))
        self.syntax_colors.setdefault("doctype", self.syntax_colors.get("keyword", "#569CD6"))
        self.syntax_colors.setdefault("entity", self.syntax_colors.get("operator", "#D4D4D4"))
        
        # HTML tags and attribute keywords
        self.tags = {
            "html", "head", "body", "div", "span", "p", "a", "img", "script",
            "style", "link", "meta", "title", "h1", "h2", "h3", "h4", "h5", "h6",
            "ul", "ol", "li", "table", "tr", "td", "th", "form", "input", "button"
        }
        
        self.attributes = {
            "class", "id", "style", "href", "src", "alt", "title", "width",
            "height", "type", "name", "value", "placeholder", "required"
        }
        
        self.setup_tags() 
