from flask import Flask, render_template, request, send_file
import os
import markdown
import pdfkit
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('editor.html')

@app.route('/convert', methods=['POST'])
def convert():
    content = ""
    filename = request.form.get('filename', 'document')
    file = request.files.get('md_file')
    output_type = request.form['output_type']

    if file and file.filename.endswith('.md'):
        content = file.read().decode('utf-8')
        filename = os.path.splitext(secure_filename(file.filename))[0]
    else:
        content = request.form.get('markdown', '')

    html_body = markdown.markdown(content, extensions=['fenced_code', 'codehilite'])

    if output_type == 'html':
        return html_body

    if output_type == 'pdf':
        css_style = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, sans-serif;
                color: #000;
                background: #fff;
                padding: 40px;
                font-size: 12pt;
                line-height: 1.6;
            }
            h1, h2, h3, h4 {
                color: #0066cc;
            }
            pre {
                background-color: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            code {
                background-color: #eee;
                padding: 2px 4px;
                border-radius: 4px;
            }
        </style>
        """

        full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{filename}</title>
    {css_style}
</head>
<body>
{html_body}
</body>
</html>
"""
        config = pdfkit.configuration(wkhtmltopdf=os.path.abspath("exe/wkhtmltopdf.exe"))
        # Générer dans un objet mémoire
        pdf_data = pdfkit.from_string(full_html, False, configuration=config)
        return send_file(
            io.BytesIO(pdf_data),
            as_attachment=True,
            download_name=f"{filename}.pdf",
            mimetype='application/pdf'
        )

if __name__ == '__main__':
    app.run(debug=True)
