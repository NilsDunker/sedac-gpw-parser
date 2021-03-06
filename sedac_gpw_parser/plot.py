"""
Plot statistics of a country's spatial population distribution.

Relies on parsing input data that has been preprocessed by the classes Grid and
Population.
"""
import os
from matplotlib import pyplot as plt
from matplotlib import cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from .population import Population


def _add_colorbar_axs(fig, plot_axs):

    axpos = plot_axs.get_position()
    pos_x = axpos.x0 + axpos.width + 0.025
    pos_y = axpos.y0 + axpos.height * 0.1
    cax_width = 0.025
    cax_height = axpos.height * 0.8
    cax = fig.add_axes([pos_x, pos_y, cax_width, cax_height])

    return cax


class Plot(Population):
    """Plot population data for a specfied country on a map."""


    def __init__(self, country_id, plot_folder="./plots/"):
        """__init__.

        :param country_id: The numeric id of a country in the sedac gpw
                           population dataset
        :type country: int

        :param plot_folder: The relative path to the folder in which the plot i
                            to be saved.
        :type plot_folder: str
        """

        if plot_folder[-1] != "/":
            plot_folder += "/"

        if not os.path.exists(plot_folder):
            os.mkdir(plot_folder)

        Population.__init__(self, country_id=country_id)

        self._country_id = country_id
        self.plot_folder = plot_folder

        self._output_path = plot_folder + str(country_id) + ".png"

        self._compute_image_extent()
        self.set_colormap()

    def _compute_image_extent(self):
        """
        Compute the extent of the final image.

        The extent is given by two points that measure the lower left corner
        and the upper right corner of the entire image.

                         +-------+ <-- (ur_x, ur_y)
                         |       |
                         |       |
        (ll_x, ll_y) --> +-------+

        The extent is stored as a tuple: (ll_x, ur_x, ll_y, ur_y).

        The coodinates are measured in radiants.
        """
        data = self._population
        ll_x = self._llcrnrlon
        ll_y = self._llcrnrlat
        cellsize = self._cellsize
        n_row, n_col = data.shape

        extent = (ll_x, ll_x + n_col * cellsize, ll_y, ll_y + n_row * cellsize)
        self._img_extent = extent


    def _add_padding(self, axs, padding=0.025):
        """
        Add some padding around an axis, e.g., a colorbar or plot-axis.

        :param axs: The axs around which the padding shall be added.
        :type axs: A matplotlib.axis instance.
        """
        ll_x, ur_x, ll_y, ur_y = self._img_extent
        delta_x = (ur_x - ll_x) * padding
        delta_y = (ur_y - ll_y) * padding

        axs.set_extent(
            (ll_x - delta_x, ur_x + delta_x, ll_y - delta_y, ur_y + delta_y))


    def set_colormap(self, colormap="Purples"):
        """
        Set the colormap for plotting.

        :param colormap: One of the standard matplotlib colormaps. See
                         https://matplotlib.org/examples/color/colormaps_reference.html
                         for a comprehensive list.
        :type colormap: str
        """
        cmap = cm.get_cmap(colormap)
        cmap.set_under('0.8')
        self._cmap = cmap


    def plot(self, title="", show=False):
        """
        Plot the population data for the specified country on a map.

        :param title: A title for the plot
        :type title: str

        :param show: Whether or not to show the plot inline. Set to True if you
                     use this class within a Jupyter Notebook.
        :type show: bool
        """
        data = self._population

        ll_x, ur_x, ll_y, ur_y = self._img_extent

        # Set up the plot
        fig = plt.figure(figsize=(8*(ur_x - ll_x)/(ur_y - ll_y), 8))
        axs = plt.axes(projection=ccrs.PlateCarree())
        plt.subplots_adjust(right=0.85, left=0.05, bottom=0.05, top=0.95)

        # Draw map
        border = cfeature.NaturalEarthFeature(
            'cultural', 'admin_0_countries', '50m', edgecolor='black',
            facecolor="None")
        axs.add_feature(border, zorder=2, linewidth=0.5)
        axs.coastlines(resolution="50m", linewidth=1.5, zorder=3)
        self._add_padding(axs=axs)

        if len(data[data > 0]) > 0:
            vmax = np.percentile(data[data > 0], 90)
        else:
            vmax = 0

        colorscheme = axs.imshow(data, vmin=0, vmax=vmax, origin='upper',
                                 extent=self._img_extent, cmap=self._cmap,
                                 transform=ccrs.PlateCarree())

        cax = _add_colorbar_axs(fig=fig, plot_axs=axs)
        cbar = plt.colorbar(colorscheme, cax=cax, extend="max", shrink=0.85)
        cbar.set_label("Population per pixel", size=12)

        axs.set_title(title)

        if show:
            plt.show()

        plt.savefig(self._output_path)
        plt.close()


def main():
    """
    Plot as an example the data for Germany (country id 276).
    """
    plot = Plot(country_id=276)
    plot.plot()


if __name__ == "__main__":
    main()
