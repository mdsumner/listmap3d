"""Build the viewer pages from src/app.html.

Run from the repo root after `npm install` (MapLibre's CSS is inlined from node_modules):

    python3 tools/build.py

Writes:
  index.html                 standalone page (committed; also works on GitHub Pages)
  out/listmap3d.html         body-only page for publishing as a claude.ai artifact
  out/kunanyi_4m_dm.b64.*.txt  the bundled snapshot as base64 text, for hosts that do not serve .tif
"""
import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
css = (ROOT / "node_modules/maplibre-gl/dist/maplibre-gl.css").read_text()
app = (ROOT / "src/app.html").read_text().replace("/*MAPLIBRE_CSS*/", css)

head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
split = app.index("</style>\n\n<div") + len("</style>\n")
(ROOT / "index.html").write_text(head + app[:split] + "</head>\n<body>\n" + app[split:] + "</body>\n</html>\n")

out = ROOT / "out"
out.mkdir(exist_ok=True)
(out / "listmap3d.html").write_text(app)
enc = base64.b64encode((ROOT / "data/kunanyi_4m_dm.tif").read_bytes()).decode()
half = (len(enc) // 2) // 4 * 4
(out / "kunanyi_4m_dm.b64.0.txt").write_text(enc[:half])
(out / "kunanyi_4m_dm.b64.1.txt").write_text(enc[half:])
print("built index.html and out/")
