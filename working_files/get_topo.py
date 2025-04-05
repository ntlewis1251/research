"""
This script will take user-input bounds* and return SRTM3 or SRTM1 data in the form of a .tif file.

When run in a jupyter notebook, ensure all necessary packages are installed in your local environment and imported into the notebook.

"""
import numpy as np
import geopandas as gpd



def get_bounds(data = None):
    """
    Function for main function that collects bounds from user.

    args: 

    returns: GeoDataFrame
    """
    #In the case that the user already has a bounds df and provides it to let the rest of the script run, the following will not run.
    if data == None:
        #Gets input from user
        bounds_str:str = input('Enter a string with four values separated by commas that orders your coordinates in the following format: "minx, miny, maxx, maxy"')
        #Converts string input from user into np array readable by GeoPandas
        bounds_arr:np.array = np.array(bounds_str.split(','))
        #Return GeoPandas df for compatability, .bounds attribute adds columns to match input format above.
        return gpd.GeoDataFrame(bounds_arr).bounds
    else:
        return data
    






def main():
    bounds = get_bounds()
    pass

if __name__ == "__main__":
    main()