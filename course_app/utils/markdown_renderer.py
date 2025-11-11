import markdown

def render_markdown(markdown_text):
    """Renders markdown text to HTML."""
    return markdown.markdown(markdown_text, extensions=['fenced_code', 'tables'])
