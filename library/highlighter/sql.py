from .base import BaseHighlighter

class CodeHighlighter(BaseHighlighter):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        # SQL keywords (common across most SQL dialects)
        self.keywords = {
            # Data manipulation
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES',
            'UPDATE', 'SET', 'DELETE', 'FROM',
            # Data definition
            'CREATE', 'TABLE', 'ALTER', 'DROP', 'TRUNCATE',
            'INDEX', 'VIEW', 'DATABASE', 'SCHEMA',
            # Joins
            'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'ON',
            'CROSS', 'NATURAL',
            # Clauses
            'GROUP', 'BY', 'HAVING', 'ORDER', 'LIMIT', 'OFFSET',
            'DISTINCT', 'UNION', 'ALL', 'EXCEPT', 'INTERSECT',
            # Conditions
            'AND', 'OR', 'NOT', 'IN', 'BETWEEN', 'LIKE', 'IS', 'NULL',
            'EXISTS', 'ANY', 'SOME', 'ALL',
            # Functions
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'COALESCE', 'NULLIF',
            'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
            # Constraints
            'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'UNIQUE',
            'CHECK', 'DEFAULT', 'NOT NULL',
            # Transactions
            'BEGIN', 'COMMIT', 'ROLLBACK', 'SAVEPOINT',
            # Data types
            'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT',
            'FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC',
            'CHAR', 'VARCHAR', 'TEXT', 'BLOB',
            'DATE', 'TIME', 'DATETIME', 'TIMESTAMP',
            'BOOLEAN', 'BOOL'
        }
        
        # SQL syntax colors - use theme colors
        # Set default values for language-specific colors if not present in theme
        self.syntax_colors.setdefault("table", self.syntax_colors.get("class", "#4EC9B0"))
        self.syntax_colors.setdefault("column", self.syntax_colors.get("variable", "#9CDCFE"))
        self.syntax_colors.setdefault("function", self.syntax_colors.get("function", "#DCDCAA"))
        self.syntax_colors.setdefault("join", self.syntax_colors.get("decorator", "#C586C0"))
        self.syntax_colors.setdefault("constraint", self.syntax_colors.get("decorator", "#FF8C00"))
        self.syntax_colors.setdefault("datatype", self.syntax_colors.get("type", "#4FC1FF"))
        
        self.setup_tags()