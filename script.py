import markdown
import os
import hashlib
import shutil
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Création du dossier Markdown s'il n'existe pas
MARKDOWN_DIR = Path("Markdown")
if not MARKDOWN_DIR.exists():
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

# CSS (thème sombre intégré)
CSS_STYLE = """
<style>
    body {
        margin: 0;
        padding: 2rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #121212;
        color: #e0e0e0;
        line-height: 1.6;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    a {
        color: #90caf9;
    }
    pre {
        background: #1e1e1e;
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
    }
    code {
        background-color: #2c2c2c;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }
    img {
        max-width: 100%;
        height: auto;
    }
    blockquote {
        border-left: 4px solid #555;
        margin-left: 0;
        padding-left: 1rem;
        color: #aaa;
    }
    @media (max-width: 600px) {
        body { padding: 1rem; }
    }
</style>
"""

# Génère le HTML complet à partir du contenu Markdown
def generate_html(md_content: str) -> str:
    html_body = markdown.markdown(md_content, extensions=['fenced_code', 'codehilite'])
    html_template = f"""
<!DOCTYPE html>
<html lang=\"fr\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Document Markdown</title>
    {CSS_STYLE}
</head>
<body>
    {html_body}
</body>
</html>
"""
    return html_template

# Calcule le hash d'un contenu texte
def hash_content(content: str) -> str:
    return hashlib.md5(content.encode('utf-8')).hexdigest()

# Fonction de traitement d'un contenu Markdown
def process_md_content(md_content: str, filename: str):
    md_name = Path(filename).stem
    html_content = generate_html(md_content)
    html_hash = hash_content(html_content)

    subdir = MARKDOWN_DIR / md_name
    subdir.mkdir(exist_ok=True)

    html_file = subdir / f"{md_name}.html"
    md_file_path = subdir / f"{md_name}.md"

    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            existing_html = f.read()
        if html_hash == hash_content(existing_html):
            messagebox.showinfo("Info", f"✅ {filename} déjà à jour.")
            return

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    messagebox.showinfo("Succès", f"✔️ HTML généré pour {filename}.")

# Affiche le contenu d'un fichier ou ouvre le HTML si c'est un dossier
def open_from_list(event):
    selection = file_listbox.curselection()
    if selection:
        filename = file_listbox.get(selection[0])
        filepath = MARKDOWN_DIR / filename
        if filepath.is_dir():
            md_file = filepath / f"{filename}.md"
            html_file = filepath / f"{filename}.html"
            if md_file.exists():
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, content)
                filename_entry.delete(0, tk.END)
                filename_entry.insert(0, md_file.name)
            if html_file.exists():
                if messagebox.askyesno("Ouvrir HTML", f"Voulez-vous ouvrir {html_file.name} dans votre navigateur ?"):
                    webbrowser.open(html_file.resolve().as_uri())
        elif filepath.suffix == ".md":
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, content)
            filename_entry.delete(0, tk.END)
            filename_entry.insert(0, filename)

# Met à jour la liste des fichiers et dossiers Markdown
def update_file_list():
    file_listbox.delete(0, tk.END)
    for item in sorted(MARKDOWN_DIR.iterdir()):
        file_listbox.insert(tk.END, item.name)
    root.after(5000, update_file_list)  # Vérifie les fichiers et dossiers toutes les 5 secondes

# Interface graphique épurée et moderne
def open_file():
    filepath = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md")])
    if not filepath:
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, content)
    filename_entry.delete(0, tk.END)
    filename_entry.insert(0, os.path.basename(filepath))

def export_html():
    content = text_area.get("1.0", tk.END).strip()
    filename = filename_entry.get().strip()
    if not content or not filename:
        messagebox.showerror("Erreur", "Veuillez fournir un contenu Markdown et un nom de fichier.")
        return
    process_md_content(content, filename)
    update_file_list()

root = tk.Tk()
root.title("Markdown ➜ HTML")
root.geometry("1080x560")
root.configure(bg="#1c1c1c")

font_family = ("Segoe UI", 11)

filename_entry = tk.Entry(root, font=font_family, bg="#2c2c2c", fg="white", insertbackground="white", relief="flat")
filename_entry.place(x=220, y=20, width=500, height=30)
filename_entry.insert(0, "nom_du_fichier.md")

browse_btn = tk.Button(root, text="📂", command=open_file, font=font_family, bg="#3a3a3a", fg="white", relief="flat")
browse_btn.place(x=730, y=20, width=40, height=30)

generate_btn = tk.Button(root, text="🚀 Générer HTML", command=export_html, font=font_family, bg="#0066cc", fg="white", relief="flat")
generate_btn.place(x=780, y=20, width=160, height=30)

file_listbox = tk.Listbox(root, bg="#2c2c2c", fg="white", font=font_family, relief="flat")
file_listbox.place(x=20, y=20, width=180, height=520)
file_listbox.bind("<<ListboxSelect>>", open_from_list)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#1e1e1e", fg="white", insertbackground="white", font=("Consolas", 11), borderwidth=0)
text_area.place(x=220, y=70, width=820, height=470)

update_file_list()

root.mainloop()
