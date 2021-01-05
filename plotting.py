
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

class Plotting:
    
    @classmethod
    def get_map(cls):
        fig = plt.figure(figsize=(20,10),dpi=200)
        ax = fig.add_subplot(111,projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, alpha=0.5)
        ax.add_feature(cfeature.RIVERS)
        ax.stock_img()
        grid_lines = ax.gridlines(draw_labels=True)
        grid_lines.xformatter = LONGITUDE_FORMATTER
        grid_lines.yformatter = LATITUDE_FORMATTER

        return fig,ax


    @classmethod
    def get_fig(cls):
        fig,axes = plt.subplots(figsize=(20,10),dpi=200)
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))
        axes.grid()
        return fig,axes

    @classmethod
    def get_map_and_fig(cls):
        fig = plt.figure(figsize=(20,10),dpi=200,constrained_layout=False)
        gs = fig.add_gridspec(3,6)
        ax_map = fig.add_subplot(gs[:2,:],projection=ccrs.PlateCarree())
        ax_map.coastlines()
        ax_map.add_feature(cfeature.LAND)
        ax_map.add_feature(cfeature.OCEAN)
        ax_map.add_feature(cfeature.COASTLINE)
        ax_map.add_feature(cfeature.BORDERS, linestyle=':')
        ax_map.add_feature(cfeature.LAKES, alpha=0.5)
        ax_map.add_feature(cfeature.RIVERS)
        ax_map.stock_img()
        grid_lines = ax_map.gridlines(draw_labels=True)
        grid_lines.xformatter = LONGITUDE_FORMATTER
        grid_lines.yformatter = LATITUDE_FORMATTER

        ax_plot = fig.add_subplot(gs[2,1:5])
        ax_plot.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))
        ax_plot.grid()

        plt.subplots_adjust(hspace=0.5)

        return fig,ax_map,ax_plot

    @classmethod 
    def unique_legend(cls,ax):
        handles, labels = ax.get_legend_handles_labels()
        unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
        ax.legend(*zip(*unique),loc='upper right')
