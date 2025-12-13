import re
from datetime import datetime
from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    """Log file syntax highlighter"""
    
    def __init__(self, text_widget):
        super().__init__(text_widget)
        
        # Log specific colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("timestamp", self.syntax_colors.get("comment", "#6A9955"))
        self.syntax_colors.setdefault("log_level_debug", self.syntax_colors.get("function", "#569CD6"))
        self.syntax_colors.setdefault("log_level_info", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("log_level_warning", self.syntax_colors.get("variable", "#DCDCAA"))
        self.syntax_colors.setdefault("log_level_error", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("log_level_critical", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("logger_name", self.syntax_colors.get("variable", "#9CDCFE"))
        self.syntax_colors.setdefault("file_path", self.syntax_colors.get("number", "#B5CEA8"))
        self.syntax_colors.setdefault("line_number", self.syntax_colors.get("number", "#B5CEA8"))
        self.syntax_colors.setdefault("ip_address", self.syntax_colors.get("function", "#4FC1FF"))
        self.syntax_colors.setdefault("url", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("exception", self.syntax_colors.get("string", "#CE9178"))
        self.syntax_colors.setdefault("stack_trace", self.syntax_colors.get("operator", "#D4D4D4"))
        self.syntax_colors.setdefault("numeric_value", self.syntax_colors.get("number", "#B5CEA8"))
        self.syntax_colors.setdefault("json_data", self.syntax_colors.get("variable", "#DCDCAA"))
        self.syntax_colors.setdefault("sql_query", self.syntax_colors.get("class", "#4EC9B0"))
        
        self.setup_tags()
        
        # Log patterns
        self.timestamp_patterns = [
            re.compile(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?'),  # ISO format
            re.compile(r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?'),  # MM/DD/YYYY format
            re.compile(r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?'),  # YYYY/MM/DD format
            re.compile(r'\[\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2}\]'),  # [DD-MM-YYYY HH:MM:SS]
        ]
        
        self.log_level_patterns = {
            'debug': re.compile(r'\b(DEBUG|debug|Debug)\b'),
            'info': re.compile(r'\b(INFO|info|Info|INFORMATION|information|Information)\b'),
            'warning': re.compile(r'\b(WARNING|warning|Warning|WARN|warn|Warn)\b'),
            'error': re.compile(r'\b(ERROR|error|Error|ERR|err|Err)\b'),
            'critical': re.compile(r'\b(CRITICAL|critical|Critical|FATAL|fatal|Fatal)\b'),
        }
        
        self.logger_name_pattern = re.compile(r'\b\w+(\.\w+)*\b')
        self.file_path_pattern = re.compile(r'\b(?:/[\w.-]+)+\b|\b(?:[A-Za-z]:)?[\\/][\w.-]+(?:[\\/][\w.-]+)*\b')
        self.line_number_pattern = re.compile(r'\bline\s+\d+\b|\b\d+\s*:\s*\d+\b', re.IGNORECASE)
        self.ip_address_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        self.url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+')
        self.exception_pattern = re.compile(r'\b(?:Exception|Error|Warning|Traceback|Stacktrace)\b', re.IGNORECASE)
        self.stack_trace_pattern = re.compile(r'^\s+File\s+".*?",\s+line\s+\d+', re.MULTILINE)
        self.numeric_pattern = re.compile(r'\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b')
        self.json_pattern = re.compile(r'\{[^{}]*\}|\[[^\[\]]*\]')
        self.sql_pattern = re.compile(r'\b(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b.*?;', re.IGNORECASE | re.DOTALL)
        
    def highlight(self):
        """Perform log file syntax highlighting"""
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
            
            # Process log elements
            self._highlight_timestamps(text)
            self._highlight_log_levels(text)
            self._highlight_logger_names(text)
            self._highlight_file_paths(text)
            self._highlight_line_numbers(text)
            self._highlight_ip_addresses(text)
            self._highlight_urls(text)
            self._highlight_exceptions(text)
            self._highlight_stack_traces(text)
            self._highlight_numeric_values(text)
            self._highlight_json_data(text)
            self._highlight_sql_queries(text)
            
            # Flush any remaining batched tag operations
            self._flush_all_tag_batches()
            
            # Restore cursor position and selection
            self.text_widget.mark_set("insert", current_insert)
            self.text_widget.yview_moveto(current_view[0])
            if current_selection:
                self.text_widget.tag_add("sel", *current_selection)
                
        except Exception as e:
            print(f"Log highlight failed: {str(e)}")
            # Fallback to basic highlighting
            self._basic_highlight(text)
    
    def _highlight_timestamps(self, text: str):
        """Highlight timestamps in log files"""
        for pattern in self.timestamp_patterns:
            for match in pattern.finditer(text):
                start_pos = match.start()
                end_pos = match.end()
                
                start_line = text.count('\n', 0, start_pos) + 1
                start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
                
                end_line = text.count('\n', 0, end_pos) + 1
                end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
                
                start = f"{start_line}.{start_col}"
                end = f"{end_line}.{end_col}"
                
                self._add_tag("timestamp", start, end)
    
    def _highlight_log_levels(self, text: str):
        """Highlight log levels"""
        for level, pattern in self.log_level_patterns.items():
            for match in pattern.finditer(text):
                start_pos = match.start()
                end_pos = match.end()
                
                start_line = text.count('\n', 0, start_pos) + 1
                start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
                
                end_line = text.count('\n', 0, end_pos) + 1
                end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
                
                start = f"{start_line}.{start_col}"
                end = f"{end_line}.{end_col}"
                
                self._add_tag(f"log_level_{level}", start, end)
    
    def _highlight_logger_names(self, text: str):
        """Highlight logger names"""
        for match in self.logger_name_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            # Check if this looks like a logger name (contains dots)
            if '.' in match.group():
                self._add_tag("logger_name", start, end)
    
    def _highlight_file_paths(self, text: str):
        """Highlight file paths"""
        for match in self.file_path_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("file_path", start, end)
    
    def _highlight_line_numbers(self, text: str):
        """Highlight line numbers"""
        for match in self.line_number_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("line_number", start, end)
    
    def _highlight_ip_addresses(self, text: str):
        """Highlight IP addresses"""
        for match in self.ip_address_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("ip_address", start, end)
    
    def _highlight_urls(self, text: str):
        """Highlight URLs"""
        for match in self.url_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("url", start, end)
    
    def _highlight_exceptions(self, text: str):
        """Highlight exceptions"""
        for match in self.exception_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("exception", start, end)
    
    def _highlight_stack_traces(self, text: str):
        """Highlight stack traces"""
        for match in self.stack_trace_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("stack_trace", start, end)
    
    def _highlight_numeric_values(self, text: str):
        """Highlight numeric values"""
        for match in self.numeric_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("numeric_value", start, end)
    
    def _highlight_json_data(self, text: str):
        """Highlight JSON data"""
        for match in self.json_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("json_data", start, end)
    
    def _highlight_sql_queries(self, text: str):
        """Highlight SQL queries"""
        for match in self.sql_pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            
            start_line = text.count('\n', 0, start_pos) + 1
            start_col = start_pos - text.rfind('\n', 0, start_pos) - 1
            
            end_line = text.count('\n', 0, end_pos) + 1
            end_col = end_pos - text.rfind('\n', 0, end_pos) - 1
            
            start = f"{start_line}.{start_col}"
            end = f"{end_line}.{end_col}"
            
            self._add_tag("sql_query", start, end)