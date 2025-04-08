import numpy  as np
import requests
import lsdtopytools as lsd
import utm

def get_key(filename:str, line:int)->str:
    """
    Goes into my super-secret api text file and gets my keys yurrr.

    args: Filename (str), line in file (int)

    returns: key

    """
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines[line-1]

def make_dir(name):
    return '/sciclone/home/ntlewis/research/working_files/data/' + name

def downloader(bounds:list, dir:str):
    keys = ['north','east','south','west']
    downloader.bounds=[bounds[0],bounds[1],str(float(bounds[0])-0.125),str(float(bounds[1])-0.125)]
    dic = dict(zip(keys, downloader.bounds))
    url = f'https://portal.opentopography.org/API/usgsdem?datasetName=USGS10m&south={dic["south"]}&north={dic["north"]}&west={dic["west"]}&east={dic["east"]}&outputFormat=GTiff&API_Key={get_key("/sciclone/home/ntlewis/research/API_key.txt", 2)}'
    response = requests.get(url)
    with open(dir,'wb') as file:
        file.write(response.content)

def get_topo():
    bounds = input('Enter NE bounding coordinates in the following format: "north,east": ').split(',')
    get_topo.name = input('Name of where new tiff will be stored: ')
    get_topo.dir = make_dir(name=get_topo.name)
    downloader(bounds=bounds, dir=get_topo.dir)
    get_topo.bounds = downloader.bounds

def generate_ksn():
    get_topo()
    bounds= get_topo.bounds
    #nor_ea_max = list(utm.from_latlon(float(bounds[0]),float(bounds[1]))[0:2])
    #nor_ea_min = list(utm.from_latlon(float(bounds[2]),float(bounds[3]))[0:2])
    mydem = lsd.LSDDEM(path = '/sciclone/home/ntlewis/research/working_files/data/', file_name = get_topo.name, already_preprocessed = False)
    mydem.PreProcessing()
    mydem.CommonFlowRoutines()
    mydem.ExtractRiverNetwork( method = "area_threshold", area_threshold_min = 300)
    mydem.DefineCatchment( method = "main_basin")
    mydem.GenerateChi(theta = 0.28, A_0 = 1)
    mydem.ksn_MuddEtAl2014(target_nodes=30, n_iterations=60, skip=1, nthreads = 1)
    return mydem.df_ksn