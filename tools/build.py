"""Build the viewer pages from src/.

Run from the repo root after `npm install` (MapLibre's CSS is inlined from node_modules):

    python3 tools/build.py

Writes:
  index.html                   landing page linking both viewers (copied from src/index.html)
  maplibre/index.html          MapLibre viewer, standalone (committed; also works on GitHub Pages)
  native/index.html            three.js native-CRS viewer, standalone (committed)
  out/listmap3d.html           body-only MapLibre page for publishing as a claude.ai artifact
  out/native.html              body-only native page for publishing as a claude.ai artifact
  out/kunanyi_4m_dm.b64.*.txt  the bundled snapshot as base64 text, for hosts that do not serve .tif
"""
import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')


def standalone(body):
    split = body.index("</style>\n\n<div") + len("</style>\n")
    return HEAD + body[:split] + "</head>\n<body>\n" + body[split:] + "</body>\n</html>\n"


out = ROOT / "out"
out.mkdir(exist_ok=True)

css = (ROOT / "node_modules/maplibre-gl/dist/maplibre-gl.css").read_text()
app = (ROOT / "src/app.html").read_text().replace("/*MAPLIBRE_CSS*/", css)
(ROOT / "maplibre").mkdir(exist_ok=True)
(ROOT / "maplibre/index.html").write_text(standalone(app))
(out / "listmap3d.html").write_text(app)

(ROOT / "index.html").write_text((ROOT / "src/index.html").read_text())

native = (ROOT / "src/native.html").read_text()
(ROOT / "native").mkdir(exist_ok=True)
(ROOT / "native/index.html").write_text(standalone(native))
(out / "native.html").write_text(native)

enc = base64.b64encode((ROOT / "data/kunanyi_4m_dm.tif").read_bytes()).decode()
half = (len(enc) // 2) // 4 * 4
(out / "kunanyi_4m_dm.b64.0.txt").write_text(enc[:half])
(out / "kunanyi_4m_dm.b64.1.txt").write_text(enc[half:])
print("built index.html, maplibre/index.html, native/index.html and out/")
