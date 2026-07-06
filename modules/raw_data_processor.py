import xarray as xr
import pandas as pd
import zipfile
from bs4 import BeautifulSoup
import netCDF4 as nc
import numpy as np


def extract_kml_from_kmz(kmz_file):
    with zipfile.ZipFile(kmz_file, 'r') as z:
        kml_file = [name for name in z.namelist() if name.endswith('.kml')][0]
        
        with z.open(kml_file) as kml:
            kml_content = kml.read()
            soup = BeautifulSoup(kml_content, 'xml')
            return soup


def parse_placemarks(kml_data):
    placemarks_data = []

    for placemark in kml_data.find_all('Placemark'):
        name = placemark.find('name').text.strip()
        coordinates = placemark.find('coordinates').text.strip()
        data = placemark.find('SimpleData', attrs={'name': 'data'}).text.strip()
        ocorrencia = placemark.find('SimpleData', attrs={'name': 'ocorrencia'}).text.strip()
        subpreit = placemark.find('SimpleData', attrs={'name': 'subpreit'}).text.strip()

        placemark_dict = {
            'Name': name,
            'Coordinates': coordinates,
            'Data': data,
            'Ocorrencia': ocorrencia,
            'Subpreit': subpreit
        }
        placemarks_data.append(placemark_dict)
    
    return pd.DataFrame(placemarks_data)


def process_ocorrencias(ocorrencias_df):
    ocorrencias_df = ocorrencias_df[ocorrencias_df['Ocorrencia'] == 'QUEDA DE ARVORE']
    ocorrencias_df['Data'] = pd.to_datetime(ocorrencias_df['Data'].astype(str), format='%Y%m%d')
    return ocorrencias_df


def filter_by_municipio(coordenada_df, municipio='SAO PAULO'):
    return coordenada_df[coordenada_df['MUNICIPIO'] == municipio]


def get_centroid(coordenada_gdf):
    coordenada_gdf['coordenadas'] = coordenada_gdf['geometry'].centroid
    return coordenada_gdf


def process_coordenadas(coordenada_gdf):
    coordenada_gdf['longitude'] = coordenada_gdf['coordenadas'].apply(lambda x: x.x)
    coordenada_gdf['latitude'] = coordenada_gdf['coordenadas'].apply(lambda x: x.y)
    coordenada_gdf.drop(columns=['geometry'], inplace=True)
    coordenada_gdf.dropna(subset=['CEP_E', 'CEP_D'], inplace=True)
    return coordenada_gdf


def concat_nc_data(nc_file1, nc_file2):
    nc_file1 = r'D:\Data_Science_Test\raw-data\nc_files\data_2023.nc'
    nc_file2 = r'D:\Data_Science_Test\raw-data\nc_files\data_2024.nc'

    arquivo1 = xr.open_dataset(nc_file1)
    arquivo2 = xr.open_dataset(nc_file2)
    arquivo2 = arquivo2.drop_dims('expver')
    concat_dados = xr.concat([arquivo1, arquivo2], dim='time')
    concat_dados.to_netcdf(r'D:\Data_Science_Test\raw-data\nc_files\data_full.nc')

    arquivo1.close()
    arquivo2.close()

    return concat_dados

def extract_nc_data(nc_file_path):
    nc_file = nc.Dataset(nc_file_path)
    ucomp = nc_file.variables['u10'][:]
    vcomp = nc_file.variables['v10'][:]
    tpcomp = nc_file.variables['tp'][:]
    lats = nc_file.variables['latitude'][:]
    lons = nc_file.variables['longitude'][:]
    time_var = nc_file.variables['time']
    time_values = time_var[:]
    time_units = time_var.units
    time_dates = nc.num2date(time_values, time_units)

    ucomp_array = np.array(ucomp)
    vcomp_array = np.array(vcomp)
    ws = np.sqrt(ucomp_array**2 + vcomp_array**2) * 0.51

    tpcomp_mean = np.mean(tpcomp, axis=(1, 2))

    return time_dates, lats, lons, tpcomp, ws

def create_meteorological_df(time_dates, lats, lons, tpcomp, ws):
    data = []
    for t, time in enumerate(time_dates):
        for lat in range(len(lats)):
            for lon in range(len(lons)):
                data.append([time, lats[lat], lons[lon], tpcomp[t, lat, lon], ws[t, lat, lon]])

    return pd.DataFrame(data, columns=['time', 'latitude', 'longitude', 'tpcomp', 'ws'])
