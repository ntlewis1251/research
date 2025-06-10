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
    # fig, ax = plt.subplots(figsize = (9,9))
    # lsd.quickplot.get_basemap(mydem , cmap = "gist_earth", hillshade = True,
	#     alpha_hillshade = 0.35, cmin = None, cmax = None,
	#     hillshade_cmin = 0, hillshade_cmax = 1, colorbar = True,
	#     fig = fig, ax = ax, colorbar_label = "Elevation (m)", colorbar_ax = None, normalise_HS = True)
    
    # Calculating and plotting flow routines
    mydem.CommonFlowRoutines()
    # fig, ax = plt.subplots(figsize = (9,9))
    # cb = ax.imshow(np.log10(mydem.cppdem.get_DA_raster()), extent = mydem.extent, vmin = 2, vmax = 9, cmap = "viridis")
    # plt.colorbar(cb, label = "Log Drainage Area")

    # Extracting river network
    mydem.ExtractRiverNetwork( method = "area_threshold", area_threshold_min = 300)

    # Defining catchment
    mydem.DefineCatchment(method='main_basin')

    # KSN! If A_0 == 1, the parameter m_chi == KSN
    mydem.GenerateChi(theta = 0.28, A_0 = 1)
    # fig, ax = lsd.quickplot.get_basemap(mydem , figsize = (9,9), cmap = "gist_earth", hillshade = True,
	#     alpha_hillshade = 1, cmin = None, cmax = None,
	#     hillshade_cmin = 0, hillshade_cmax = 1, colorbar = False,
	#     fig = None, ax = None, colorbar_label = None, colorbar_ax = None, fontsize_ticks = 16, normalise_HS = True)
    # size_array = lsd.size_my_points(np.log10(mydem.df_base_river.drainage_area), 2,15)
    # ax.scatter(mydem.df_base_river.x, mydem.df_base_river.y, lw=0, c= "b",  zorder = 5, s=size_array)
    # lsd.quickplot_utilities.add_basin_outlines(mydem, fig, ax, size_outline = 10, zorder = 5, color = "k")
    
    mydem.ksn_MuddEtAl2014(target_nodes=30, n_iterations=60, skip=1, nthreads = 1)

    # fig, ax = plt.subplots(figsize = (9,9))
    # lsd.quickplot.get_basemap(mydem , figsize = (9,9), cmap = "gist_earth", hillshade = True,
	#     alpha_hillshade = 1, cmin = None, cmax = None,
	#     hillshade_cmin = 0, hillshade_cmax = 1, colorbar = False,
	#     fig = fig, ax = ax, colorbar_label = None, colorbar_ax = None, fontsize_ticks = 16, normalise_HS = True)
    # size_array = lsd.size_my_points(np.log10(mydem.df_ksn.drainage_area), 1,15)
    # lsd.quickplot_utilities.add_basin_outlines(mydem, fig, ax, size_outline = 10, zorder = 5, color = "k")
    # cb = ax.scatter(mydem.df_ksn.x, mydem.df_ksn.y, lw=0, c= mydem.df_ksn.m_chi, cmap = "magma", zorder = 5, s=size_array, vmin = 0, vmax = 10)
    # plt.colorbar(cb, label = r"$k_{sn}$")

    gdf = gpd.GeoDataFrame(mydem.df_ksn, geometry=gpd.points_from_xy(mydem.df_ksn.x,mydem.df_ksn.y))
    gdf = gdf[(gdf.m_chi >= 0) & (gdf.m_chi <= 100)]
    return gdf, mydem

def df_relief(dem, pix:int):
    """
    https://rvt-py.readthedocs.io/en/latest/examples/rvt_vis_example.html
    """
    pass