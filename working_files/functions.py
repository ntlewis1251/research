import numpy  as np
import requests
import lsdtopytools as lsd
import utm
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from osgeo import gdal
import rasterio
import seaborn as sns

def get_key(filename:str, line:int)->str:
    """
    Goes into my super-secret api text file and gets my keys yurrr.

    args: Filename (str), line in file (int)

    returns: key

    """
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines[line-1]

make_dir = lambda name, : '/sciclone/home/ntlewis/research/working_files/data/' + name

def downloader(bounds:list, dir:str):
    """
    Takes in NE and SW bounding coordinates as well as a directory name.  Downloads a DEM from opentopo and places it in the chosen directory.
    """
    keys = ['north','east','south','west']
    downloader.bounds=[bounds[0],bounds[1],str(float(bounds[0])-0.125),str(float(bounds[1])-0.125)]
    dic = dict(zip(keys, downloader.bounds))
    url = f'https://portal.opentopography.org/API/usgsdem?datasetName=USGS10m&south={dic["south"]}&north={dic["north"]}&west={dic["west"]}&east={dic["east"]}&outputFormat=GTiff&API_Key={get_key("/sciclone/home/ntlewis/research/API_key.txt", 2)}'
    response = requests.get(url)
    with open(dir,'wb') as file:
        file.write(response.content)

def get_topo(north,east,name):
    """
    Runs downloader & make dir function.  For use in jupyter notebooks.  For a self-contained script, visit ___.
    """
    bounds = list([north,east])
    get_topo.name = name
    get_topo.dir = make_dir(name=get_topo.name)
    downloader(bounds=bounds, dir=get_topo.dir)
    get_topo.bounds = downloader.bounds

def generate_ksn(north, east, name):
    get_topo(north=north, east=east, name=name)
    # Reprojecting
    
    file = f'/sciclone/home/ntlewis/research/working_files/data/{name}'
    input_raster = gdal.Open(file)
    output_raster = f'/sciclone/home/ntlewis/research/working_files/data/{name}'
    warp = gdal.Warp(output_raster,input_raster, dstSRS='EPSG:32617')
    warp = None #close
    raster=rasterio.open(f'/sciclone/home/ntlewis/research/working_files/data/{name}')
    profile = raster.profile
    profile.update(nodata=None)
    with rasterio.open(f'/sciclone/home/ntlewis/research/working_files/data/{name}', 
                  mode="w", 
                  **profile,) as update_dataset:
        update_dataset.write(raster.read(1), 1)

    # Assigning to LSDDEM object for analysis, plotting DEM for debugging
    mydem = lsd.LSDDEM(path = '/sciclone/home/ntlewis/research/working_files/data/', file_name = get_topo.name, already_preprocessed = False)
    mydem.PreProcessing()
    
    # Calculating and plotting flow routines
    mydem.CommonFlowRoutines()

    # Extracting river network
    mydem.ExtractRiverNetwork( method = "area_threshold", area_threshold_min = 300)

    # Defining catchment
    mydem.DefineCatchment(method='main_basin')

    # KSN! If A_0 == 1, the parameter m_chi == KSN
    mydem.GenerateChi(theta = 0.28, A_0 = 1)
    
    mydem.ksn_MuddEtAl2014(target_nodes=30, n_iterations=60, skip=1, nthreads = 1)

    gdf = gpd.GeoDataFrame(mydem.df_ksn, geometry=gpd.points_from_xy(mydem.df_ksn.x,mydem.df_ksn.y))
    gdf = gdf[(gdf.m_chi >= 0) & (gdf.m_chi <= 100)]
    return gdf, mydem

def rast_to_df(rast):
    """
    for rasters of equal len and width.
    Takes in raster
    Returns df representation of raster.
    Returns df representation of each 1km sq relief.
    """
    # making df more readable.
    transform = rast.transform
    elev = rast.read(1)
    row, col = rast.shape
    x, y = np.meshgrid(np.arange(col), np.arange(row))
    lon, lat = rasterio.transform.xy(transform, y, x)
    df = pd.DataFrame({'lon':np.array(lon).flatten(), 'lat':np.array(lat).flatten(), 'elevation':np.array(elev).flatten(),'x':x.flatten(), 'y':y.flatten()})

    # Now calculating relief for each 1km x 1km square
    i=0
    df_relief = pd.DataFrame(columns = ['poly', 'relief', 'lat_max', 'lon_max', 'lat_min', 'lon_min'])
    
    for x in range(100, rast.shape[1], 100):
        for y in range(100, rast.shape[1], 100):
            poly_df = df.loc[df.x<=x].loc[df.x>=x-100].loc[df.y<=y].loc[df.y>=y-100]
            lon_max, lat_max = rasterio.transform.xy(transform, y, x)
            lon_min, lat_min = rasterio.transform.xy(transform, y-100, x-100)
            df_relief.loc[i] = [('sq_'+str(x)+'_'+str(y)), (poly_df.elevation.max()-poly_df.elevation.min()),
                                 np.array(lat_max).flatten(), np.array(lon_max).flatten(), np.array(lat_min).flatten(), np.array(lon_min).flatten()]
            i+=1
    df_relief['rank'] = df_relief['relief'].rank(pct=True)
    return df, df_relief