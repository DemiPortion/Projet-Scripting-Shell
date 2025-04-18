import re

def simple_markdown_to_html(md_text):
    # Titres h1 à h6
    for i in range(6, 0, -1):
        pattern = r'^' + ('#' * i) + r' (.*)'
        replacement = f'<h{i}>\\1</h{i}>'
        md_text = re.sub(pattern, replacement, md_text, flags=re.MULTILINE)

    # Préparation
    lines = md_text.split("\n")
    processed = []
    in_ul = False
    in_ol = False
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Bloc de code (début/fin)
        if stripped.startswith("```"):
            if in_code_block:
                processed.append("</code></pre>")
                in_code_block = False
            else:
                processed.append("<pre><code>")
                in_code_block = True
            continue

        if in_code_block:
            processed.append(stripped)
            continue

        # Liste à puces
        if re.match(r'^- ', stripped):
            if not in_ul:
                processed.append('<ul>')
                in_ul = True
            processed.append(f'<li>{stripped[2:].strip()}</li>')
            continue
        elif in_ul:
            processed.append('</ul>')
            in_ul = False

        # Liste ordonnée
        if re.match(r'^\d+\. ', stripped):
            if not in_ol:
                processed.append('<ol>')
                in_ol = True
            processed.append(re.sub(r'^\d+\.\s+', '<li>', stripped) + '</li>')
            continue
        elif in_ol:
            processed.append('</ol>')
            in_ol = False

        # Citation
        if stripped.startswith("> "):
            processed.append(f'<blockquote>{stripped[2:].strip()}</blockquote>')
            continue

        # Ligne horizontale
        if re.match(r'^(\*\*\*|---|___)$', stripped):
            processed.append('<hr>')
            continue

        # Code en ligne
        line = re.sub(r'`([^`]+)`', r'<code>\1</code>', stripped)

        # Gras, italique, barré
        line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        line = re.sub(r'__(.*?)__', r'<em>\1</em>', line)
        line = re.sub(r'~~(.*?)~~', r'<del>\1</del>', line)

        # Image et lien
        line = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', line)
        line = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', line)

        # Paragraphe (évite les balises vides)
        if line:
            processed.append(f'<p>{line}</p>')

    # Fermeture éventuelle
    if in_ul:
        processed.append('</ul>')
    if in_ol:
        processed.append('</ol>')
    if in_code_block:
        processed.append('</code></pre>')

    # Nettoyage des lignes vides en trop
    cleaned = []
    for i, line in enumerate(processed):
        if line == "" and (i == 0 or processed[i - 1] == ""):
            continue
        cleaned.append(line)

    return "\n".join(cleaned)
