import tkinter as tk
from tkinter import ttk, filedialog
import markdown
from fpdf import FPDF
import os
import re
import tempfile
import webbrowser

# --- Core Logic ---
class MarkdownPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

def _sanitize(text):
    # Replace common unicode with latin-1 safe equivalents
    replacements = {'\u2014': '--', '\u2013': '-', '\u2018': "'", '\u2019': "'",
                    '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u2022': '-'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Drop any remaining non-latin1 characters
    return text.encode('latin-1', errors='replace').decode('latin-1')

def convert_md_to_pdf(md_text, output_path):
    pdf = MarkdownPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    for line in md_text.split('\n'):
        stripped = _sanitize(line.strip())

        # Headings
        if stripped.startswith('### '):
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(68, 68, 68)
            pdf.cell(0, 10, stripped[4:], new_x='LMARGIN', new_y='NEXT')
            pdf.ln(2)
        elif stripped.startswith('## '):
            pdf.set_font('Helvetica', 'B', 16)
            pdf.set_text_color(51, 51, 51)
            pdf.cell(0, 10, stripped[3:], new_x='LMARGIN', new_y='NEXT')
            pdf.set_draw_color(220, 220, 220)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
        elif stripped.startswith('# '):
            pdf.set_font('Helvetica', 'B', 20)
            pdf.set_text_color(0, 90, 158)
            pdf.cell(0, 12, stripped[2:], new_x='LMARGIN', new_y='NEXT')
            pdf.set_draw_color(0, 90, 158)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)
        # Horizontal rule
        elif stripped in ('---', '***', '___'):
            pdf.set_draw_color(220, 220, 220)
            pdf.line(10, pdf.get_y() + 3, 200, pdf.get_y() + 3)
            pdf.ln(8)
        # Bullet points
        elif stripped.startswith('- ') or stripped.startswith('* '):
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(51, 51, 51)
            text = stripped[2:]
            # Handle bold in list items
            text = _render_inline(pdf, text, bullet=True)
        # Code block markers
        elif stripped.startswith('```'):
            continue
        # Empty line
        elif not stripped:
            pdf.ln(4)
        # Regular text
        else:
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(51, 51, 51)
            _render_inline(pdf, stripped)

    pdf.output(output_path)

def _render_inline(pdf, text, bullet=False):
    # Simple bold/italic/code inline rendering
    prefix = '  -  ' if bullet else ''
    # Strip markdown bold/italic for clean PDF
    clean = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    clean = re.sub(r'\*(.+?)\*', r'\1', clean)
    clean = re.sub(r'`(.+?)`', r'\1', clean)
    clean = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean)
    clean = _sanitize(clean)

    if '**' in text:
        # Has bold segments
        parts = re.split(r'(\*\*.+?\*\*)', text)
        x_start = pdf.get_x()
        if bullet:
            pdf.set_font('Helvetica', '', 11)
            pdf.write(6, prefix)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                pdf.set_font('Helvetica', 'B', 11)
                pdf.write(6, part[2:-2])
            else:
                pdf.set_font('Helvetica', '', 11)
                pdf.write(6, part)
        pdf.ln(7)
    else:
        pdf.set_font('Helvetica', '', 11)
        pdf.multi_cell(0, 6, prefix + clean)
        pdf.ln(1)
    return clean

def preview_md(md_text):
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'codehilite', 'toc'])
    tmp = os.path.join(tempfile.gettempdir(), "md2pdf_preview.html")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(f"<html><head><meta charset='utf-8'><style>body{{font-family:'Segoe UI',sans-serif;max-width:800px;margin:40px auto;padding:0 20px;line-height:1.6;color:#333}}h1{{color:#005A9E;border-bottom:2px solid #005A9E;padding-bottom:8px}}h2{{border-bottom:1px solid #ddd;padding-bottom:6px}}code{{background:#f4f4f4;padding:2px 6px;border-radius:3px;font-family:Consolas,monospace}}pre{{background:#f4f4f4;padding:12px;border-radius:5px}}blockquote{{border-left:4px solid #005A9E;padding:8px 16px;color:#555;background:#f9f9f9}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px 12px}}th{{background:#f4f4f4}}a{{color:#005A9E}}</style></head><body>{html}</body></html>")
    webbrowser.open(f"file:///{tmp}")

# --- Graphical User Interface ---
class MD2PDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MD to PDF")
        self.root.geometry("600x520")
        self.root.resizable(True, True)
        self.root.minsize(400, 400)

        self.current_file = None

        # --- UI Styling ---
        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 8), foreground="#888888")
        style.configure("File.TLabel", font=("Consolas", 9), foreground="#005A9E")

        # --- Top Bar ---
        top_frame = ttk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(top_frame, text="Markdown to PDF", style="Title.TLabel").pack(side="left")

        self.file_label = ttk.Label(top_frame, text="No file loaded", style="File.TLabel")
        self.file_label.pack(side="right")

        # --- Button Bar ---
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=8)

        self.open_btn = ttk.Button(btn_frame, text="Open .md", command=self.open_file)
        self.open_btn.pack(side="left", padx=(0, 5))

        self.paste_btn = ttk.Button(btn_frame, text="Paste from Clipboard", command=self.paste_clipboard)
        self.paste_btn.pack(side="left", padx=5)

        self.preview_btn = ttk.Button(btn_frame, text="Preview", command=self.preview)
        self.preview_btn.pack(side="right", padx=(5, 0))

        self.export_btn = ttk.Button(btn_frame, text="Export PDF", command=self.export_pdf)
        self.export_btn.pack(side="right", padx=5)

        # --- Editor ---
        editor_frame = ttk.Frame(root)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        self.text_editor = tk.Text(editor_frame, font=("Consolas", 11), wrap="word", undo=True, bg="#FAFAFA", relief="flat", borderwidth=1, highlightthickness=1, highlightbackground="#CCCCCC")
        self.text_editor.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(editor_frame, orient="vertical", command=self.text_editor.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_editor.config(yscrollcommand=scrollbar.set)

        # Placeholder
        self.text_editor.insert("1.0", "Type or paste your Markdown here...")
        self.text_editor.config(foreground="#AAAAAA")
        self.text_editor.bind("<FocusIn>", self.clear_placeholder)
        self.text_editor.bind("<FocusOut>", self.show_placeholder)

        # Keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.export_pdf())
        self.root.bind("<Control-p>", lambda e: self.preview())

        # --- Status Bar ---
        status_frame = ttk.Frame(root)
        status_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.status_label = ttk.Label(status_frame, text="Ctrl+O open  |  Ctrl+S export  |  Ctrl+P preview", style="Status.TLabel")
        self.status_label.pack(side="left")

        self.char_label = ttk.Label(status_frame, text="0 chars", style="Status.TLabel")
        self.char_label.pack(side="right")

        self.text_editor.bind("<KeyRelease>", lambda e: self.update_char_count())

    def clear_placeholder(self, event):
        if self.text_editor.get("1.0", "end").strip() == "Type or paste your Markdown here...":
            self.text_editor.delete("1.0", "end")
            self.text_editor.config(foreground="#333333")

    def show_placeholder(self, event):
        if not self.text_editor.get("1.0", "end").strip():
            self.text_editor.insert("1.0", "Type or paste your Markdown here...")
            self.text_editor.config(foreground="#AAAAAA")

    def update_char_count(self):
        text = self.text_editor.get("1.0", "end").strip()
        if text == "Type or paste your Markdown here...":
            self.char_label.config(text="0 chars")
        else:
            self.char_label.config(text=f"{len(text)} chars")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md *.markdown *.txt")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", content)
        self.text_editor.config(foreground="#333333")
        self.current_file = path
        self.file_label.config(text=os.path.basename(path))
        self.status_label.config(text=f"Opened {os.path.basename(path)}")
        self.update_char_count()

    def paste_clipboard(self):
        try:
            text = self.root.clipboard_get()
            if text.strip():
                self.clear_placeholder(None)
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", text)
                self.text_editor.config(foreground="#333333")
                self.current_file = None
                self.file_label.config(text="Pasted from clipboard")
                self.status_label.config(text="Pasted markdown from clipboard")
                self.update_char_count()
        except tk.TclError:
            self.status_label.config(text="Nothing in clipboard to paste")

    def get_md_text(self):
        text = self.text_editor.get("1.0", "end").strip()
        if text == "Type or paste your Markdown here...":
            return ""
        return text

    def preview(self):
        md_text = self.get_md_text()
        if not md_text:
            self.status_label.config(text="Nothing to preview — enter some markdown first")
            return
        preview_md(md_text)
        self.status_label.config(text="Preview opened in browser")

    def export_pdf(self):
        md_text = self.get_md_text()
        if not md_text:
            self.status_label.config(text="Nothing to export — enter some markdown first")
            return

        default_name = ""
        if self.current_file:
            default_name = os.path.splitext(os.path.basename(self.current_file))[0] + ".pdf"

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Document", "*.pdf")],
            initialfile=default_name
        )
        if not path:
            return

        try:
            convert_md_to_pdf(md_text, path)
            self.status_label.config(text=f"Exported to {os.path.basename(path)}")
            self.export_btn.config(text="Exported!")
            self.root.after(2000, lambda: self.export_btn.config(text="Export PDF"))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_label.config(text=f"Export failed: {str(e)[:80]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MD2PDFApp(root)
    root.mainloop()
