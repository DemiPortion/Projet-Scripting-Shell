
import re

def markdown_to_html(text):
    def replace_code_blocks(text):
        return re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)

    def replace_inline_code(text):
        return re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    def replace_headers(text):
        for i in range(6, 0, -1):
            pattern = r'^(#{' + str(i) + r'})\s+(.+)$'
            repl = r'<h' + str(i) + r'>\2</h' + str(i) + r'>'
            text = re.sub(pattern, repl, text, flags=re.MULTILINE)
        return text

    def replace_bold_italic(text):
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
        return text

    def replace_links_images(text):
        text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', text)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        return text

    def replace_blockquotes(text):
        lines = text.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith(">"):
                new_lines.append("<blockquote>" + line[1:].strip() + "</blockquote>")
            else:
                new_lines.append(line)
        return "\n".join(new_lines)

    def replace_lists(text):
        lines = text.split("\n")
        html = []
        in_ul, in_ol = False, False
        for line in lines:
            if re.match(r'^\s*[-+*]\s+', line):
                if not in_ul:
                    html.append("<ul>")
                    in_ul = True
                html.append(f"<li>{line.strip()[2:].strip()}</li>")
            elif re.match(r'^\s*\d+\.\s+', line):
                if not in_ol:
                    html.append("<ol>")
                    in_ol = True
                html.append(re.sub(r'^\s*\d+\.\s+', '<li>', line.strip()) + "</li>")
            else:
                if in_ul:
                    html.append("</ul>")
                    in_ul = False
                if in_ol:
                    html.append("</ol>")
                    in_ol = False
                html.append(line)
        if in_ul:
            html.append("</ul>")
        if in_ol:
            html.append("</ol>")
        return "\n".join(html)

    def replace_tables(text):
        lines = text.split("\n")
        new_lines = []
        in_table = False
        for i, line in enumerate(lines):
            if "|" in line:
                if not in_table:
                    new_lines.append("<table>")
                    in_table = True
                cells = line.strip().split("|")[1:-1]
                tag = "th" if re.match(r"^\s*\|?\s*:?[-]+:?", line) else "td"
                new_lines.append("<tr>" + "".join([f"<{tag}>{cell.strip()}</{tag}>" for cell in cells]) + "</tr>")
            else:
                if in_table:
                    new_lines.append("</table>")
                    in_table = False
                new_lines.append(line)
        if in_table:
            new_lines.append("</table>")
        return "\n".join(new_lines)

    def replace_hr(text):
        return re.sub(r'^(\*{3,}|-{3,}|_{3,})$', r'<hr>', text, flags=re.MULTILINE)

    text = replace_code_blocks(text)
    text = replace_inline_code(text)
    text = replace_headers(text)
    text = replace_bold_italic(text)
    text = replace_links_images(text)
    text = replace_blockquotes(text)
    text = replace_lists(text)
    text = replace_tables(text)
    text = replace_hr(text)

    # Paragraphe final
    lines = text.split("\n")
    output = []
    for line in lines:
        if line.strip() and not re.match(r'^<(/?(h\d|ul|ol|li|pre|code|blockquote|table|tr|td|th|hr|img|a))', line.strip()):
            output.append(f"<p>{line.strip()}</p>")
        else:
            output.append(line)
    return "\n".join(output)
