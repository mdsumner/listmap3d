# listmap3d

A browser 3D viewer for the Tasmania 2 m DEM, with LIST open data WFS layers paged in for the current view.

![Statewide view built from the DEM overviews](docs/statewide.png)

Open `index.html` in a browser (double-click works, or serve the folder or turn on GitHub Pages). There is no build step
needed to run it; scripts come from jsDelivr.

## How it works

**DEM.** The 2 m DEM on Source Cooperative is a single 95 GB cloud-optimised GeoTIFF
(`Tasmania_Statewide_2m_DEM_14-08-2021.tif`, EPSG:28355, float32, LZW, 512 px tiles, overviews 2 to 1024). S3 serves
it with `Access-Control-Allow-Origin: *`:

    https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/alexgleith/tasmania-dem-2m/Tasmania_Statewide_2m_DEM_14-08-2021.tif

A MapLibre custom protocol (`cogdem://`) builds each Web Mercator terrain tile on demand. It projects an 8 x 8 control
grid to MGA55 with proj4, picks the coarsest overview whose pixel is still finer than the screen pixel on the ground,
reads that window with geotiff.js range requests, resamples bilinearly, and encodes Terrarium RGB. The same tiles feed
the terrain mesh, the hillshade and the hypsometric tint. So the DEM has real level of detail: the whole state uses the
1:512 overview (about 1 km pixels) and street level uses the 2 m data.

**Overlays.** WFS 2.0 at
`https://services.thelist.tas.gov.au/arcgis/services/Public/OpenDataWFS/MapServer/WFSServer`, 56 feature types under
`Public_OpenDataWFS:`, requested as `outputFormat=GEOJSON`. Each layer has a minimum zoom. At or above it the viewer
requests Web Mercator cells (tiles at the layer's minimum zoom, the 16 nearest the view centre) with `count` and
`startIndex` paging (1000 per page, 4 pages per cell), dedupes on OBJECTID and drapes the result on the terrain. Click a
feature for its attributes. Any of the 56 layers can be added from the list under the curated ones.

The Orthophoto and Topographic buttons use the LIST Web Mercator tile caches
(`rest/services/Basemaps/Orthophoto` and `Basemaps/Topographic`, `MapServer/tile/{z}/{y}/{x}`).

**WFS quirk.** The default GEOJSON output is EPSG:4326 in **lat, lon** order, with a legacy `crs` member and the string
`"null"` for empty fields. The viewer asks for EPSG:3857 output with a 3857 bbox first, falls back to a lat/lon 4326
bbox, and detects the axis order from the coordinates either way.

**Offline fallback.** If the live COG cannot be reached (for example in a sandboxed page), the viewer loads
`data/kunanyi_4m_dm.tif`, a 4 m int16-decimetre COG of kunanyi / Hobart (12.5 MB), and limits the view to it.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The viewer, built from `src/app.html` |
| `src/app.html` | Page source; the build inlines the MapLibre CSS |
| `tools/build.py` | Builds `index.html`, plus `out/` files for publishing as a claude.ai artifact (`npm install` first) |
| `tools/snap.py`, `tools/snapshot_int16.py` | Make the bundled snapshot from the statewide COG (needs rasterio) |
| `data/kunanyi_4m_dm.tif` | The bundled snapshot |

## Why it is local-bound, and what cloud-ready LIST data would fix

![kunanyi from the live COG](docs/kunanyi.png)

- **WFS has no level of detail.** Cadastre, buildings, roads and contours can only be shown close in. Every pan is a
  fresh set of server queries, and a dense cell is truncated at the paging cap. A statewide view of any of them is not
  possible this way. Vector tiles (PMTiles / MVT) or GeoParquet with a spatial index would remove the limit.
- **The DEM scales, at a cost.** It is already a COG, but opening it reads about 8 MB of header (tile offset arrays for
  roughly 500k full-resolution tiles) before the first pixel. Float32 with LZW and no predictor makes each view heavy:
  about 40 MB for a pitched valley view, and 25 MB more at street level. A floating-point predictor or LERC compression,
  per-region files, or a Terrarium / quantized-mesh tile pyramid would cut both.
- **The default WFS GeoJSON axis order (lat, lon) breaks standard GeoJSON readers.**

## Data

DEM and overlays: The LIST, (c) State of Tasmania, licensed CC BY 3.0 AU. DEM copy on
[Source Cooperative](https://source.coop/alexgleith/tasmania-dem-2m) uploaded by Alex Leith.
Libraries: [MapLibre GL JS](https://maplibre.org/), [geotiff.js](https://geotiffjs.github.io/), [proj4js](http://proj4js.org/).
