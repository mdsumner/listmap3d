# Run from the repo root after tools/snap.py. Converts the 4 m float snapshot (from snap.py) to int16 decimetres, DEFLATE + predictor 2 (12.5 MB).
import rasterio, numpy as np
with rasterio.open('kunanyi_4m.tif') as d:
    a = d.read(1); prof = d.profile
dm = np.round(a * 10).astype('int16')
p = dict(driver='COG', dtype='int16', count=1, width=a.shape[1], height=a.shape[0], crs=prof['crs'],
         transform=prof['transform'], nodata=-32768, compress='DEFLATE', predictor=2, level=9,
         blocksize=256, overview_resampling='average')
with rasterio.open('data/kunanyi_4m_dm.tif', 'w', **p) as o:
    o.write(dm, 1)
