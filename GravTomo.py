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

# These are appropriate values for the GRS80 model
omega_earth = 7.292115e-5
a_earth = 6378137.
b_earth = 6356752.3141
GM_earth = 3.986005e14
f_earth = 0.003352810681183637418
pot_ref_geoid_earth = 6263686.0850E1

#Setting our density shell radius
r_i = 0.9*r0_pot_earth

#rotational velocity of earth, in radians/second
omega = 2. * np.pi / (24.*60.*60.)



grav = sht.MakeGravGridDH(coeffs,
                          gm = GM_earth,
                          r0 = a_earth,
                          omega=omega_earth,
                          a = a_earth,
                          f = f_earth,
                          normal_gravity = 1)


geoid = sht.MakeGeoidGridDH(coeffs,
                            r0pot = a_earth,
                            GM = GM_earth,
                            PotRef=pot_ref_geoid_earth,
                            omega=omega_earth,
                            a = a_earth,
                            f = f_earth)


nlat,nlon = geoid.shape
dlat = 360. / nlat
lats = np.linspace(0. + (dlat / 2.), 360. - (dlat / 2.), nlat)
normal_gravs = [sht.NormalGravity(lat,GM_earth,omega_earth,a_earth,b_earth) for lat in lats]
ng = np.array(normal_gravs,np.float64)

# Brun's formula
T = geoid * ng[:,np.newaxis]

gravity_disturbance_SH = sht.SHExpandDH(grav[0])

anti_radial_deriv_op = -a_earth/np.arange(1.,gravity_disturbance_SH.shape[1]+1.,1.)

T_SH = gravity_disturbance_SH * anti_radial_deriv_op[np.newaxis,:,np.newaxis]

T_grid = sht.MakeGridDH(T_SH,sampling=2,csphase=1)



#defining a function for the distance from our point of reference to every point on the density shell
def make_Rpm(R_e,r_i,co_lats,shp):
    rpm_1D = np.sqrt(-2.*r_i*R_e*np.cos(co_lats) + R_e**2 + r_i**2 )
    rpm_2D = np.zeros(shp,np.float32)
    rpm_2D[:,:] = rpm_1D[:,np.newaxis]
    return rpm_2D

#defining our colatitudes
co_lats = np.linspace(0.,np.pi,num=T.shape[0],endpoint=True)

#defining the coordinates of our shell of radius r_i
rpm_2D = -make_Rpm(R_e = r0_pot_earth, r_i = r_i, co_lats = co_lats, shp = grid.shape)

#expanding to find SH coefficients for shell of radius r_i
rpm_2D_SH = sht.SHExpandDH(rpm_2D)

kernel =  rpm_2D_SH[0,:,0]


convolved = kernel[np.newaxis,:,np.newaxis] * T_SH
convolved[:,1,1] = 0.

#grid of gravitational source values on shell of radius r_i
tomo_r1 = sht.MakeGridDH(convolved,sampling=2,csphase=1)

#defining filter to be applied before backprojection
ramp_filter = np.linspace(0.,1.,num=convolved.shape[1],endpoint=True)
cone_filter_2d = np.sqrt(np.outer(ramp_filter*ramp_filter,ramp_filter*ramp_filter))

#convolution of coefficients and shell after filterning
filtered_convolved = cone_filter_2d[np.newaxis,:,:] * convolved
tomo_r1_filtered = sht.MakeGridDH(filtered_convolved,sampling=2,csphase=1)



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




