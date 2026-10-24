#!/usr/bin/env python3
"""Convert ATS resume markdown to print-ready HTML, then PDF via headless Chrome."""
import re
import subprocess
import sys
from pathlib import Path

MD = Path(__file__).parent / "Jaisy_Al_Huda_Sibghotullah_ATS_Resume_CV.md"
HTML = Path(__file__).parent / "Jaisy_Al_Huda_Sibghotullah_ATS_Resume_CV.html"
PDF = Path(__file__).parent / "Jaisy_Al_Huda_Sibghotullah_ATS_Resume_CV.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 8mm 9mm; }
* { box-sizing: border-box; }
body {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8.8pt;
  line-height: 1.14;
  color: #111;
  margin: 0;
}
h1 { font-size: 14pt; margin: 0 0 1pt; letter-spacing: .3pt; }
h2 {
  font-size: 9.8pt; text-transform: uppercase; letter-spacing: .6pt;
  border-bottom: 1pt solid #333; padding-bottom: 1pt;
  margin: 5pt 0 2.2pt;
}
h3 { font-size: 9.4pt; margin: 4pt 0 0; }
h4 { font-size: 8.8pt; margin: 3.5pt 0 0; }
p { margin: 0.8pt 0; }
p.tagline, p.contact { margin: 0.8pt 0; }
p.date { font-weight: bold; margin: 0 0 1.2pt; }
p.impact { margin: 0.6pt 0; }
ul { margin: 1.2pt 0 2.5pt; padding-left: 12pt; }
li { margin: 0 0 0.3pt; }
ul.edu { list-style: none; padding-left: 0; margin: 1.5pt 0; }
ul.cols { columns: 2; column-gap: 18pt; }
.section { page-break-inside: auto; }
.job { page-break-inside: avoid; }
strong { font-weight: bold; }
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
            out.append(f'<h3>{bold(s[4:])}</h3>')
        elif s.startswith("## "):
            two_col_next = "certification" in s.lower()
            out.append(f'<h2>{s[3:]}</h2>')
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
            elif "GitHub:" in s or "|" in s and "+" in s:
                out.append(f'<p class="contact">{txt}</p>')
            else:
                out.append(f"<p>{txt}</p>")
        i += 1
    return "\n".join(out)

def main():
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Resume</title><style>{CSS}</style></head>
<body>{convert(MD.read_text())}</body></html>"""
    HTML.write_text(html)
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={PDF}", HTML.as_uri(),
    ], check=True, capture_output=True)
    print(f"OK {PDF}")

if __name__ == "__main__":
    sys.exit(main())
