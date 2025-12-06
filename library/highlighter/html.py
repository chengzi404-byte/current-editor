from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # HTML syntax colors
        self.syntax_colors.update({
            "tag": "#569CD6",
            "attribute": "#9CDCFE",
            "string": "#CE9178",
            "comment": "#6A9955",
            "doctype": "#569CD6",
            "entity": "#D4D4D4"
        })
        
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
