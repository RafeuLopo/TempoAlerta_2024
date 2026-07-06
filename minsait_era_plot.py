# %%
from modules import plot
import netCDF4 as nc
import numpy as np

# %%
nc_file_path = r'D:\Data_Science_Test\Datalake\raw-data\nc_files\data_2024.nc'
plotter = plot.NetPlotter(nc_file_path, output_dir='D:\Data_Science_Test\ERA5_maps\Chuva (mm)', corrompido=1)
plotter.plot_tp_images(colormap='viridis', bordas=True, start_date='2024-01-07', end_date='2024-01-09')
plotter = plot.NetPlotter(nc_file_path, output_dir=r'D:\Data_Science_Test\ERA5_maps\Vento (kmh)', corrompido=1)
plotter.plot_wind_speed_images(colormap='viridis', bordas=True, start_date='2024-01-07', end_date='2024-01-09')

# %%
