# Your file paths
files = {
    'Rice (Dryland)': 'DATA_GAEZ-V5_MAPSET_RES02-YLD_GAEZ-V5.RES02-YLD.HP0120.AGERA5.HIST.RICD.LILM.tif',
    'Rice (Wetland)': 'DATA_GAEZ-V5_MAPSET_RES02-YLD_GAEZ-V5.RES02-YLD.HP0120.AGERA5.HIST.RICW.LILM.tif',
    'Wheat': 'DATA_GAEZ-V5_MAPSET_RES02-YLD_GAEZ-V5.RES02-YLD.HP0120.AGERA5.HIST.WHEA.LILM.tif'
}

import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

fig = plt.figure(figsize=(20, 8))
axes = []
for i, (title, filepath) in enumerate(files.items(), 1):
    with rasterio.open(filepath) as src:
        data = src.read(1).astype(np.float32)
        nodata = src.nodata
        valid_mask = (data != nodata) & ~np.isnan(data)
        data_masked = np.ma.masked_where(~valid_mask, data)
                
        data_display = np.copy(data_masked)
        data_display[data_display < 0.1] = 0  
        
        data_log = np.log1p(data_display)  # use log scale to improve visibility of low yields, while still showing high yields without saturation
        
        # Create axes with PlateCarree projection (good for global)
        ax = fig.add_subplot(1, 3, i, projection=ccrs.PlateCarree())
        axes.append(ax)
        
        im = ax.imshow(data_log,
                       origin='upper',
                       extent=(src.bounds.left, src.bounds.right,
                               src.bounds.bottom, src.bounds.top),
                       transform=ccrs.PlateCarree(),
                       cmap='YlGn',          # classic yield: yellow low → green high
                       vmin=0,
                       vmax=np.nanpercentile(data_log, 99))
        
        ax.add_feature(cfeature.COASTLINE, lw=0.5, edgecolor='gray')
        ax.add_feature(cfeature.BORDERS, lw=0.3, edgecolor='gray', alpha=0.5)
        ax.set_title(title + f"\n(max raw ~{np.nanmax(data_display):.1f} t/ha)")
        
        fig.colorbar(im, ax=ax, orientation='horizontal', fraction=0.05, pad=0.05,
                     label='log(1 + yield t/ha)')

# focus on Eurasia for Fractured-Land
for ax in axes:
    ax.set_extent([-20, 180, -10, 80], crs=ccrs.PlateCarree())

plt.tight_layout()
plt.show()