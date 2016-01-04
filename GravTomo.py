import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
from matplotlib import pyplot as plt
import pyshtools as sht
import numpy as np

#loading in the EGM08 spherical harmonic coefficients
coeffs,errors,lmax = sht.SHReadError('EGM2008_to2190_TideFree.shm',2190)

#setting our constants
r0_pot_earth = sht.constant.r0_pot_earth
gm_earth = sht.constant.gm_earth
G_Me = 3986004.415E8
Re_EGM08 = 6378136.3

#Setting our density shell radius
r_i = 0.9*r0_pot_earth

#rotational velocity of earth, in radians/second
omega = 2. * np.pi / (24.*60.*60.)

#making a grid out of the EGM08 SH coefficients
grid = sht.MakeGridDH(coeffs,sampling=2,csphase=1)

#defining a function for the distance from our point of reference to every point on the density shell
def make_Rpm(R_e,r_i,co_lats,shp):
    rpm_1D = np.sqrt(-2.*r_i*R_e*np.cos(co_lats) + R_e**2 + r_i**2 )
    rpm_2D = np.zeros(shp,np.float32)
    rpm_2D[:,:] = rpm_1D[:,np.newaxis]
    return rpm_2D

#defining our colatitudes
co_lats = np.linspace(0.,np.pi,num=grid.shape[0],endpoint=True)

#defining the coordinates of our shell of radius r_i
rpm_2D = -make_Rpm(R_e = r0_pot_earth, r_i = r_i, co_lats = co_lats, shp = grid.shape)

#expanding to find SH coefficients for shell of radius r_i
rpm_2D_SH = sht.SHExpandDH(rpm_2D)

#convolution of EGM08 coefficients with the shell of radius r_i
convolved = rpm_2D_SH[0,:,0] * coeffs
convolved_c20 = convolved[0,2,0]
convolved[0,2,0] = 0.

#grid of gravitational source values on shell of radius r_i
tomo_r1 = sht.MakeGridDH(convolved,sampling=2,csphase=1)

#defining filter to be applied before backprojection
ramp_filter = np.linspace(0.,1.,num=convolved.shape[1],endpoint=True)
cone_filter_2d = np.sqrt(np.outer(ramp_filter*ramp_filter,ramp_filter*ramp_filter))

#convolution of coefficients and shell after filterning
filtered_convolved = cone_filter_2d[np.newaxis,:,:]* convolved
tomo_r1_filtered = sht.MakeGridDH(filtered_convolved,sampling=2,csphase=1)

#centrifugal potential, due to Earth's rotation
V_c = -(1./2.) * (omega**2) * (r0_pot_earth**2) * (np.sin(co_lats)**2)

#unitless centrifugal potential
V_c_unitless = V_c*Re_EGM08/G_Me

#EGM08 grid minus centrifugal potential, leaving potential due to masses
no_cetrifugal_grid = grid + V_c_unitless[:,np.newaxis]


#our J2n coefficients for our gravitational potential perturbation
def J2n(n, J2 = 1.08263E-3, a = 6378137., E = 522000.):
	ellip = E / a
	sgn = (-1)**(n+1)
	ans = (sgn*(3.*ellip**(2*n))/(((2.*n)+1.)*((2.*n)+3.))) * (1.-n+((5.*n)/(ellip**2))*J2)
	return ans

def deltaCnm(n,m,J2N):
	"""
		Computes the elliptical Earth correction terms to the SH expansion.
		We will subtract what is returned by this function from Cnm, the SH coeffs of V.
	"""
	if n == 0:
		#not perturbing C00
		#IF we decide to keep the mass of the Earth in the calculation, this subtracts zero from that value.
		#IF NOT, this still subtracts zero from it.
		return 0.
	elif (m == 0) and ((n % 2) == 0):
		#we have even degree and zero order
		#we correct the zonal coefficient by subtracting this value from it
		return -J2n(n)/np.sqrt((2.*n)+1)
	else:
		#all other cases, do not perturb the SH coefficients
		return 0.




