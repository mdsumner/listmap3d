import rasterio, numpy as np, os
from rasterio.warp import transform
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
u='/vsicurl/https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/alexgleith/tasmania-dem-2m/Tasmania_Statewide_2m_DEM_14-08-2021.tif'
xs,ys=transform('EPSG:4326','EPSG:28355',[147.2368,147.3272],[-42.8957,-42.8821]); print(xs,ys)
# region: kunanyi summit to Derwent
L,B,R,T = 512000, 5245000, 532000, 5259000
res=float(os.environ.get('RES','4'))
os.environ['GDAL_DISABLE_READDIR_ON_OPEN']='EMPTY_DIR'
with rasterio.open(u) as d:
    w=from_bounds(L,B,R,T,d.transform)
    W=int((R-L)/res); H=int((T-B)/res)
    a=d.read(1,window=w,out_shape=(H,W),resampling=Resampling.average if res>2 else Resampling.nearest, masked=True)
    print(a.shape, a.min(), a.max(), a.mask.mean())
    out=np.where(a.mask, -9999, np.round(a.filled(-9999),2)).astype('float32')
    prof=dict(driver='COG',dtype='float32',count=1,width=W,height=H,crs=d.crs,
      transform=rasterio.transform.from_origin(L,T,res,res),nodata=-9999,
      compress='DEFLATE',predictor=3,level=9,blocksize=256,overview_resampling='average')
    fn=f'kunanyi_{int(res)}m.tif'  # then run snapshot_int16.py
    with rasterio.open(fn,'w',**prof) as o: o.write(out,1)
    print(fn, os.path.getsize(fn)/1e6,'MB')
