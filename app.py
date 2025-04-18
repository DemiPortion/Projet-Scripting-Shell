from flask import Flask, render_template, request, send_file
import os
import io
import pdfkit
import tempfile
from werkzeug.utils import secure_filename
from markdown_parser import markdown_to_html, markdown_to_slides

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('editor.html')

@app.route('/convert', methods=['POST'])
def convert():
    filename = request.form.get('filename', 'document')
    file = request.files.get('md_file')
    output_type = request.form['output_type']

    if file and file.filename.endswith('.md'):
        content = file.read().decode('utf-8')
        filename = os.path.splitext(secure_filename(file.filename))[0]
    else:
        content = request.form.get('markdown', '')

    # Slides HTML (affichage)
    if output_type == 'slides':
        return markdown_to_slides(content)

    # Slides PDF (style sombre type présentation)
    if output_type == 'slides-pdf':
        html_slides = markdown_to_slides(content)
        html_slides = html_slides.replace(
            "<body>", "<body style='background-color: #111; color: white;'>"
        )
        config = pdfkit.configuration(wkhtmltopdf=os.path.abspath("exe/wkhtmltopdf.exe"))
        options = {
            'page-size': 'A4',
            'margin-top': '0',
            'margin-bottom': '0',
            'margin-left': '0',
            'margin-right': '0',
            'encoding': "UTF-8",
            'print-media-type': '',
            'no-outline': None,
            'viewport-size': '1280x720'
        }
        pdf_data = pdfkit.from_string(html_slides, False, configuration=config, options=options)
        return send_file(
            io.BytesIO(pdf_data),
            as_attachment=True,
            download_name=f"{filename}_slides.pdf",
            mimetype='application/pdf'
        )

    # HTML simple
    if output_type == 'html':
        return markdown_to_html(content)

    # PDF classique (avec saut de page sur <h1>)
    if output_type == 'pdf':
        html_body = markdown_to_html(content)

        # Ajouter un saut de page avant chaque <h1> sauf le premier
        html_body = html_body.replace("<h1>", "<h1 style='page-break-before: always;'>", 1)
        html_body = html_body.replace("<h1>", "<h1 style='page-break-before: always;'>")

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
        pdf_data = pdfkit.from_string(full_html, False, configuration=config)
        return send_file(
            io.BytesIO(pdf_data),
            as_attachment=True,
            download_name=f"{filename}.pdf",
            mimetype='application/pdf'
        )

if __name__ == '__main__':
    app.run(debug=True)
