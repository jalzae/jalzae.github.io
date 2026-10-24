#!/usr/bin/env python3
"""Convert ATS resume markdown to index.html (screen + print CSS), then PDF via headless Chrome."""
import re
import subprocess
import sys
from pathlib import Path

MD = Path(__file__).parent / "Jaisy_Al_Huda_Sibghotullah_ATS_Resume_CV.md"
HTML = Path(__file__).parent / "index.html"
PDF = Path(__file__).parent / "Jaisy_Al_Huda_Sibghotullah_ATS_Resume_CV.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BASE_CSS = """
* { box-sizing: border-box; }
body {
  font-family: Arial, Helvetica, sans-serif;
  color: #111;
  margin: 0;
  background: #fff;
}
h1 { letter-spacing: .3pt; }
h2 {
  text-transform: uppercase; letter-spacing: .6pt;
  border-bottom: 1pt solid #333; padding-bottom: 1.5pt;
}
p.date { font-weight: bold; }
strong { font-weight: bold; }
ul.edu { list-style: none; padding-left: 0; }
ul.cols { columns: 2; column-gap: 18pt; }
"""

SCREEN_CSS = """
@media screen {
  body { font-size: 10.5pt; line-height: 1.5; background: #e8eaed; padding: 28px 12px; }
  .page { max-width: 820px; margin: 0 auto; background: #fff; padding: 40px 48px;
          box-shadow: 0 1px 6px rgba(0,0,0,.18); border-radius: 4px; }
  h1 { font-size: 22pt; margin: 0 0 2pt; }
  h2 { font-size: 12pt; margin: 16pt 0 5pt; }
  h3 { font-size: 11.5pt; margin: 9pt 0 0; }
  h4 { font-size: 10.5pt; margin: 7pt 0 0; }
  p { margin: 2pt 0; }
  p.date { margin: 0 0 3pt; }
  ul { margin: 3pt 0 6pt; padding-left: 16pt; }
  li { margin: 0 0 2pt; }
  ul.edu { margin: 3pt 0; }
}
"""

PRINT_CSS = """
@page { size: A4; margin: 10mm 11mm; }
body { font-size: 9pt; line-height: 1.26; }
h1 { font-size: 14pt; margin: 0 0 2pt; }
h2 { font-size: 9.8pt; margin: 8pt 0 3.2pt; }
h3 { font-size: 9.6pt; margin: 6pt 0 0; }
h4 { font-size: 9pt; margin: 5pt 0 0; }
p { margin: 1.2pt 0; }
p.date { margin: 0 0 2pt; }
p.impact { margin: 1pt 0; }
ul { margin: 2pt 0 3.5pt; padding-left: 13pt; }
li { margin: 0 0 0.8pt; }
ul.edu { margin: 2pt 0; }
h2, h3, h4, p.date { page-break-after: avoid; }
li { page-break-inside: avoid; }
"""

def bold(s: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

def convert(md_text: str) -> str:
    lines = md_text.splitlines()
    out, i, n = [], 0, len(lines)
    two_col_next = False
    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        # tables -> linearized plain-text lines (ATS/AI safe)
        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") and c for c in cells):  # skip separator
                    rows.append(cells)
                i += 1
            for r in rows[1:]:  # skip header row
                area, result, ctx = (r + ["", ""])[:3]
                out.append(f'<p class="impact"><strong>{bold(area)}:</strong> {bold(result)} — {bold(ctx)}</p>')
            continue
        if s.startswith("#### "):
            out.append(f"<h4>{bold(s[5:])}</h4>")
        elif s.startswith("### "):
            out.append(f"<h3>{bold(s[4:])}</h3>")
        elif s.startswith("## "):
            two_col_next = "certification" in s.lower()
            out.append(f"<h2>{s[3:]}</h2>")
        elif s.startswith("# "):
            out.append(f"<h1>{s[2:]}</h1>")
        elif s.startswith("- "):
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(f"<li>{bold(lines[i].strip()[2:])}</li>")
                i += 1
            cls = "edu" if any("University" in it or "Nusa Mandiri" in it for it in items) else ""
            if two_col_next:
                cls = (cls + " cols").strip()
                two_col_next = False
            out.append(f'<ul class="{cls}">{"".join(items)}</ul>')
            continue
        else:
            txt = bold(s)
            if re.fullmatch(r"\*\*.+\*\*", s):  # standalone bold line = date or subtitle
                cls = "date" if re.search(r"\d{4}", s) else "tagline"
                out.append(f'<p class="{cls}">{txt}</p>')
            elif "GitHub:" in s or ("|" in s and "+" in s):
                out.append(f'<p class="contact">{txt}</p>')
            else:
                out.append(f"<p>{txt}</p>")
        i += 1
    return "\n".join(out)

def main():
    body = convert(MD.read_text())
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jaisy Al Huda Sibghotullah — Senior Full-Stack Software Engineer</title>
<style>{BASE_CSS}{SCREEN_CSS}@media print {{ {PRINT_CSS} }}</style></head>
<body><div class="page">{body}</div></body></html>"""
    HTML.write_text(html)
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={PDF}", HTML.as_uri(),
    ], check=True, capture_output=True)
    print(f"OK {HTML}\nOK {PDF}")

if __name__ == "__main__":
    sys.exit(main())
