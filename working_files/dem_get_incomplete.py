import os
import requests
from functions import *

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

def main():
    bounds = input('Enter NE bounding coordinates in the following format: "north,east": ').split(',')
    name = input('Name of where new tiff will be stored: ')
    dir = make_dir(name=name)
    downloader(bounds=bounds, dir=dir)
    get_topo.bounds = downloader.bounds