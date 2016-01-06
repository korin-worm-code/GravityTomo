import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
from matplotlib import pyplot as plt
import pyshtools as sht
import numpy as np

# Loading in the EGM08 spherical harmonic coefficients
coeffs, errors, lmax = sht.SHReadError('EGM2008_to2190_ZeroTide.shm',2190)


# These are appropriate values for the GRS80 model
omega_earth = 7.292115e-5
a_earth = 6378137.
b_earth = 6356752.3141
GM_earth = 3.986005e14
f_earth = 0.003352810681183637418
pot_ref_geoid_earth = 6263686.0850E1

# Setting our density shell radius
r_i = 0.9 * 6371000.

# Creating the geoid
geoid = sht.MakeGeoidGridDH(coeffs,
                            r0pot = a_earth,
                            GM = GM_earth,
                            PotRef = pot_ref_geoid_earth,
                            omega = omega_earth,
                            a = a_earth,
                            f = f_earth,
                            order = 2)

# Defining the normal gravity
nlat, nlon = geoid.shape
dlat = 360. / nlat
lats = np.linspace(0. + (dlat / 2.), 360. - (dlat / 2.), nlat)
normal_gravs = [sht.NormalGravity(lat, GM_earth, omega_earth, a_earth, b_earth) for lat in lats]
ng = np.array(normal_gravs, np.float64)

# Brun's formula
T = geoid * ng[:, np.newaxis]

# Expanding our T
T_SH = sht.SHExpandDH(T)


# Function for distance from point of reference to all points on density shell
def make_Rpm(R_e, r_i, co_lats, shp):
    rpm_1D = np.sqrt(-2. * r_i * R_e * np.cos(co_lats) + R_e**2 + r_i**2 )
    rpm_2D = np.zeros(shp, np.float64)
    rpm_2D[:, :] = rpm_1D[:, np.newaxis]
    return rpm_2D

# Defining colatitudes
co_lats = np.linspace(0., np.pi, num = T.shape[0], endpoint=True)

# Defining coordinates of shell of radius r_i
rpm_2D = -make_Rpm(R_e = 6371000., r_i = r_i, co_lats = co_lats, shp = T.shape)

# Expanding to find SH coefficients for shell of radius r_i
rpm_2D_SH = sht.SHExpandDH(rpm_2D)


kernel_1 = rpm_2D_SH[0, :, 0]


# Function for distance from point of reference to all points on density shell
def make_Rpm(R_e, r_i, co_lats, shp):
    rpm_1D = np.sqrt(-2. * r_i * R_e * np.cos(co_lats) + R_e**2 + r_i**2 )
    PlB = sht.PlBar(T.shape[0], co_lats)
    rpm_PlB = rpm_1D * PlB
    return rpm_PlB

# Defining colatitudes
co_lats = np.linspace(0., np.pi, num = T.shape[0], endpoint=True)

# Defining coordinates of shell of radius r_i
rpm_PlB = -make_Rpm(R_e = 6371000., r_i = r_i, co_lats = co_lats, shp = T.shape)


kernel_2 = rpm_PlB

# Convolution of density shell with T
convolved = kernel[np.newaxis, :, np.newaxis] * T_SH
convolved[:, 1, 1] = 0.

# Gravitational source values on shell of radius r_i
tomo_r1 = sht.MakeGridDH(convolved, sampling=2, csphase=1)

# Filter to apply before backprojection
ramp_filter = np.linspace(0., 1., num = convolved.shape[1], endpoint = True)
cone_filter_2d = np.sqrt(np.outer(ramp_filter * ramp_filter, ramp_filter * ramp_filter))

# Convolution of coefficients and shell after filterning
filtered_convolved = cone_filter_2d[np.newaxis, :, :] * convolved
tomo_r1_filtered = sht.MakeGridDH(filtered_convolved, sampling=2, csphase=1)



