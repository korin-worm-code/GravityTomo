# coding: utf-8

# get_ipython().magic(u'matplotlib inline')
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid, addcyclic
#import cartopy.crs as ccrs
##from cartopy.util import add_cyclic_point
##import cartopy.img_transform as it
##import pyshtools as sht
import numpy as np
#from scipy.special import erfi
#plt.rcParams['figure.figsize'] = [12.0,8.0]

class MapDrawer(object):
    """Encapsulate all of the Basemap map-drawing stuff, so that it's once 
    and only once."""

    def __init__(self,projection,example_image):
        self.projection = projection
        self.nlat,self.nlon = example_image.shape
        #FIXME: this assumes the whole planet in cylindrical coords
        self.dlat = 180. / self.nlat
        self.dlon = 360. / self.nlon
        self.lats = np.linspace(0. + (self.dlat / 2.), 180. - (self.dlat / 2.), self.nlat)
        # FIXME: These are co-latitudes!
        self.lats = 90. - self.lats
        self.lons = np.linspace(0. + (self.dlon / 2.), 360. + (self.dlon / 2.), self.nlon)
        # Basemap transform_scalar() needs -180 <= lons <= 180.
        #self.lons[self.lons>=180.] -= 360.
        self.fig = plt.figure()


    def BuildArray(self,m,img,lon_0):
        if lon_0 != 180:
            new_img, new_lons = addcyclic(img,self.lons)
            new_img, new_lons = shiftgrid(lon_0, img, self.lons, start=False)
        else:
            new_img = img
            new_lons = self.lons
        transformed_img = m.transform_scalar(new_img,
                                             new_lons,
                                             self.lats[-1::-1],
                                             self.nlon,
                                             self.nlat,
                                             masked=1.e-5)
        return transformed_img

    def DrawMap(self,img,lon_0=180,cmap='inferno',units_label=None,vmin=None,vmax=None,title=None,returnImage=False):
        if lon_0 == 180:
            lon_0 -= 1.e-4
        if vmin == None:
        	vmin = img.min()
        if vmax == None:
        	vmax = img.max()
        m = Basemap(projection=self.projection,lon_0=lon_0,resolution='c')
        x,y = m(*np.meshgrid(self.lons,self.lats))

        m.drawcoastlines()
        # draw parallels and meridians.
        m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0])
        if self.projection == 'cyl':
            lbls = [0,0,0,1]
        else:
            lbls = [0,0,0,0]
        m.drawmeridians(np.arange(0.,420.,60.),labels=lbls)
        m.drawmapboundary()

        if title <> None:
            plt.title(title)
        transformed_img = self.BuildArray(m,img,lon_0)
        p = m.imshow(transformed_img,origin='upper',vmin=vmin,vmax=vmax,cmap=cmap,animated=True)
        cbar = m.colorbar(p,location='right',pad="5%")
        if units_label != None:
            cbar.set_label(units_label)

        if returnImage:
            return p
        else:
            return



    #def CartopyDrawMap(self,img,lon_0=0):
        # Warning. Not working...
        ##trans = ccrs.Mollweide(central_longitude=lon_0)
        ##ax = plt.axes(projection=trans)
        ##cyc_data, cyc_lons = add_cyclic_point(img,coord=self.lons)
        #ax.imshow(cyc_data,origin='upper',transform=trans)
        ##ax.coastlines()
        ##ax.gridlines()
        # warped_data,target_extent = it.warp_array(cyc_data,
        #                                           trans,
        #                                           target_res=(self.nlon, self.nlat),
        #                                           mask_extrapolated=True)
        # ax.pcolormesh(cyc_lons,self.lats,warped_data,transform=trans)
