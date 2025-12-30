def validate_settings(settings):
    """Validate settings"""
    required_fields = [
        "editor.file-encoding",
        "editor.lang",
        "editor.font",
        "editor.fontsize",
        "editor.file-path",
        "highlighter.syntax-highlighting"
    ]
    for field in required_fields:
        if field not in settings:
            return False
    return True