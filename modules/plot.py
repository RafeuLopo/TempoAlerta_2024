import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
from datetime import datetime

class NetPlotter:
    def __init__(self, nc_file_path, output_dir='tp_images', corrompido=0):
        self.nc_file_path = nc_file_path
        self.output_dir = output_dir
        self.corrompido = corrompido
        self._load_nc_file()
        self._create_output_dir()
    
    def _load_nc_file(self):
        self.nc_file = nc.Dataset(self.nc_file_path)
        self.ucomp = self.nc_file.variables['u10'][:]
        self.vcomp = self.nc_file.variables['v10'][:]
        self.tpcomp = self.nc_file.variables['tp'][:]
        self.lats = self.nc_file.variables['latitude'][:]
        self.lons = self.nc_file.variables['longitude'][:]
        time_var = self.nc_file.variables['time']
        time_values = time_var[:]
        time_units = time_var.units
        self.time_dates = nc.num2date(time_values, time_units)

        ucomp_array = np.array(self.ucomp)
        vcomp_array = np.array(self.vcomp)
        self.ws = np.sqrt(ucomp_array**2 + vcomp_array**2) * 0.51

        self.tpcomp *= 1000

        self.ws *= 3.6

        if self.corrompido == 1:
            self.tpcomp = self.tpcomp[:, 0, :, :]
            self.ws = self.ws[:, 0, :, :]

        elif self.corrompido == 0:
            pass

    def _create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Pasta criada: {self.output_dir}")
        else:
            print(f"Pasta já existe: {self.output_dir}")

    def save_images(self, data, data_type, colormap='viridis', bordas=False, start_date=None, end_date=None):
        if start_date is not None:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date is not None:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        for index, date in enumerate(self.time_dates):

            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date > end_date:
                continue

            fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': ccrs.PlateCarree()})
            ax.set_extent([np.min(self.lons), np.max(self.lons), np.min(self.lats), np.max(self.lats)], crs=ccrs.PlateCarree())

            if bordas == True:
                ax.add_feature(cfeature.BORDERS, linestyle=':')
                ax.add_feature(cfeature.COASTLINE)
                ax.add_feature(cfeature.LAND, edgecolor='black')
                ax.add_feature(cfeature.OCEAN)
                ax.add_feature(cfeature.STATES)

            mesh = ax.pcolormesh(self.lons, self.lats, data[index, :, :], shading='auto', cmap=colormap, transform=ccrs.PlateCarree())
            cbar = plt.colorbar(mesh, ax=ax, orientation='vertical', location='right', pad=0.02)
            cbar.set_label('Intensidade')
            file_name = os.path.join(self.output_dir, f'{data_type}_{date.strftime("%Y-%m-%d_%H-%M-%S")}.png')
            plt.savefig(file_name, bbox_inches='tight', pad_inches=0.1)
            print(f"Salvando a figura de {data_type}: {file_name}")
            plt.close(fig)
    
    def plot_wind_speed_images(self, colormap='viridis', bordas=False, start_date=None, end_date=None):
        self.save_images(self.ws, 'ws', colormap, bordas, start_date, end_date)
    
    def plot_tp_images(self, colormap='viridis', bordas=False, start_date=None, end_date=None):
        self.save_images(self.tpcomp, 'tp', colormap, bordas, start_date, end_date)
