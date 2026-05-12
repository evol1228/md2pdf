# MD to PDF

A lightweight Markdown to PDF converter with a built-in editor and live preview.

## Features

- **Built-in editor** — Write or edit markdown directly in the app
- **Open .md files** — Load any markdown file from disk
- **Paste from clipboard** — One-click paste of markdown content
- **Live preview** — Preview rendered markdown in your browser
- **Export to PDF** — Clean A4 PDF with styled headings, code blocks, tables
- **Keyboard shortcuts** — Ctrl+O open, Ctrl+S export, Ctrl+P preview
- **Character counter** — Live char count in the status bar

## Requirements

| Dependency | Install |
|------------|---------|
| Python 3.6+ | [python.org](https://python.org) |
| tkinter | Included (Linux: `sudo apt install python3-tk`) |
| markdown | `pip install -r requirements.txt` |
| fpdf2 | `pip install -r requirements.txt` |

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
   ```bash
   python md2pdf.py
   ```

2. Type markdown, open a `.md` file, or paste from clipboard

3. Click **Preview** to see it in your browser, or **Export PDF** to save

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open markdown file |
| Ctrl+S | Export to PDF |
| Ctrl+P | Preview in browser |

## Building

To compile to a standalone executable (optional):

```bash
pip install nuitka
python -m nuitka --standalone --onefile --windows-disable-console md2pdf.py
```

## License

MIT
