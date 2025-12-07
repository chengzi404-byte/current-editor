import re
from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    """Markdown syntax highlighter"""
    
    def __init__(self, text_widget):
        super().__init__(text_widget)
        
        # Markdown specific colors
        self.syntax_colors.update({
            "heading": "#569CD6",
            "bold": "#DCDCAA",
            "italic": "#DCDCAA",
            "code_block": "#CE9178",
            "inline_code": "#CE9178",
            "link": "#4EC9B0",
            "image": "#4EC9B0",
            "blockquote": "#6A9955",
            "list": "#B5CEA8",
            "horizontal_rule": "#D4D4D4",
            "table": "#9CDCFE",
            "strikethrough": "#C586C0",
        })
        
        self.setup_tags()
        
        # Markdown patterns
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.*)$', re.MULTILINE)
        self.bold_pattern = re.compile(r'(\*\*|__)(.*?)\1')
        self.italic_pattern = re.compile(r'(\*|_)(.*?)\1')
        self.code_block_pattern = re.compile(r'```[\s\S]*?```|~~~[\s\S]*?~~~')
        self.inline_code_pattern = re.compile(r'`[^`]+`')
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
        self.blockquote_pattern = re.compile(r'^>\s+(.*)$', re.MULTILINE)
        self.list_pattern = re.compile(r'^[\s]*[-*+]\s+(.*)$', re.MULTILINE)
        self.numbered_list_pattern = re.compile(r'^[\s]*\d+\.\s+(.*)$', re.MULTILINE)
        self.horizontal_rule_pattern = re.compile(r'^[-*_]{3,}\s*$', re.MULTILINE)
        self.strikethrough_pattern = re.compile(r'~~(.*?)~~')
        self.table_pattern = re.compile(r'^\|.*\|$', re.MULTILINE)
        
    def highlight(self):
        """Perform Markdown syntax highlighting"""
        try:
            # Save current status
            current_insert = self.text_widget.index("insert")
            current_view = self.text_widget.yview()
            current_selection = None
            try:
                current_selection = (
                    self.text_widget.index("sel.first"),
                    self.text_widget.index("sel.last")
                )
            except:
                pass
                
            # Clear existing tags
            self._clear_tags()
            text = self.text_widget.get("1.0", "end-1c")
            
            # Initialize tag batch
            self._tag_batch = {}
            
            # Process Markdown elements
            self._highlight_headings(text)
            self._highlight_bold_and_italic(text)
            self._highlight_code_blocks(text)
            self._highlight_links_and_images(text)
            self._highlight_blockquotes(text)
            self._highlight_lists(text)
            self._highlight_horizontal_rules(text)
            self._highlight_strikethrough(text)
            self._highlight_tables(text)
            
            # Flush any remaining batched tag operations
            self._flush_all_tag_batches()
            
            # Restore cursor position and selection
            self.text_widget.mark_set("insert", current_insert)
            self.text_widget.yview_moveto(current_view[0])
            if current_selection:
                self.text_widget.tag_add("sel", *current_selection)
                
        except Exception as e:
            print(f"Markdown highlight failed: {str(e)}")
            # Fallback to basic highlighting
            self._basic_highlight(text)
    
    def _highlight_headings(self, text: str):
        """Highlight Markdown headings"""
        for match in self.heading_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            # Calculate line and column positions
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            # Highlight the entire heading
            self._add_tag("heading", start, end)
    
    def _highlight_bold_and_italic(self, text: str):
        """Highlight bold and italic text"""
        # Bold text
        for match in self.bold_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("bold", start, end)
        
        # Italic text
        for match in self.italic_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("italic", start, end)
    
    def _highlight_code_blocks(self, text: str):
        """Highlight code blocks and inline code"""
        # Code blocks
        for match in self.code_block_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("code_block", start, end)
        
        # Inline code
        for match in self.inline_code_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("inline_code", start, end)
    
    def _highlight_links_and_images(self, text: str):
        """Highlight links and images"""
        # Links
        for match in self.link_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("link", start, end)
        
        # Images
        for match in self.image_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("image", start, end)
    
    def _highlight_blockquotes(self, text: str):
        """Highlight blockquotes"""
        for match in self.blockquote_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("blockquote", start, end)
    
    def _highlight_lists(self, text: str):
        """Highlight lists"""
        # Unordered lists
        for match in self.list_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("list", start, end)
        
        # Numbered lists
        for match in self.numbered_list_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("list", start, end)
    
    def _highlight_horizontal_rules(self, text: str):
        """Highlight horizontal rules"""
        for match in self.horizontal_rule_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("horizontal_rule", start, end)
    
    def _highlight_strikethrough(self, text: str):
        """Highlight strikethrough text"""
        for match in self.strikethrough_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("strikethrough", start, end)
    
    def _highlight_tables(self, text: str):
        """Highlight tables"""
        for match in self.table_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("table", start, end)