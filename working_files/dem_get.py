import os
import requests
from functions import *

def make_dir(name):
    return '/sciclone/home/ntlewis/research/working_files/data/' + name

def get_topo(bounds:list, dir:str):
    keys = ['south','north','west','east']
    dic = dict(zip(keys, bounds))
    url = f'https://portal.opentopography.org/API/globaldem?demtype=NASADEM&south={dic["south"]}&north={dic["north"]}&west={dic["west"]}&east={dic["east"]}&outputFormat=GTiff&API_Key={get_key("/sciclone/home/ntlewis/research/API_key.txt", 2)}'
    response = requests.get(url)
    with open(dir,'wb') as file:
        file.write(response.content)

def main():
    bounds = input('Enter bounding coordinates in the following format: "miny,maxy,minx,maxx": ').split(',')
    name = input('Name of where new tiff will be stored: ')
    dir = make_dir(name=name)
    get_topo(bounds=bounds, dir=dir)

if __name__ == '__main__':
    main()