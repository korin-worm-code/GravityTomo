#### cython: linetrace=True
"""A Cythonized version of X-ray transform backprojection.

   We pass in the positions, radial field, and current pole normal.
   We locally allocate sum and count buffers in Cartesian coords, and fill them
   with the approximated xray transform value, and hit count for a specific
   voxel in the buffer.
"""


import numpy
cimport numpy

cimport cython

DTYPE_INT = numpy.int
ctypedef numpy.int_t DTYPE_INT_T

DTYPE_UINT32 = numpy.uint32
ctypedef numpy.uint32_t DTYPE_UINT32_T

DTYPE_FLOAT = numpy.float32
ctypedef numpy.float32_t DTYPE_FLOAT_T

DTYPE_DOUBLE = numpy.float64
ctypedef numpy.float64_t DTYPE_DOUBLE_T

DTYPE_BOOL = numpy.bool_
ctypedef numpy.npy_bool DTYPE_BOOL_T

@cython.boundscheck(False)
def backprojectRays(DTYPE_INT_T Ntheta,
                    DTYPE_INT_T Nphi,
                    numpy.ndarray[DTYPE_FLOAT_T, ndim=1] bound_coords_1d,
                    numpy.ndarray[DTYPE_DOUBLE_T,  ndim=3] radial_cartesian_field,
                    numpy.ndarray[DTYPE_DOUBLE_T, ndim=2] px,
                    numpy.ndarray[DTYPE_DOUBLE_T, ndim=2] py,
                    numpy.ndarray[DTYPE_DOUBLE_T, ndim=2] pz,
                    DTYPE_DOUBLE_T dx_in,
                    DTYPE_DOUBLE_T dy_in,
                    DTYPE_DOUBLE_T dz_in,
                    DTYPE_DOUBLE_T infty=1.E9):

    cdef numpy.ndarray[DTYPE_UINT32_T, ndim=1] Thetas = numpy.arange(0,Ntheta,dtype=DTYPE_UINT32)
    cdef DTYPE_UINT32_T theta

    cdef numpy.ndarray[DTYPE_UINT32_T, ndim=1] Phis   = numpy.arange(0,Nphi,  dtype=DTYPE_UINT32)
    cdef DTYPE_UINT32_T phi
    
    # Allocate these locally to avoid race conditions in the calling routine
    # if we parallelize over multiple cores...
    cdef numpy.ndarray[DTYPE_DOUBLE_T, ndim=3] sum_buf   = numpy.zeros((Ntheta,Ntheta,Ntheta),dtype=DTYPE_DOUBLE)
    cdef numpy.ndarray[DTYPE_INT_T, ndim=3]    count_buf = numpy.zeros((Ntheta,Ntheta,Ntheta),dtype=DTYPE_INT)

    cdef DTYPE_BOOL_T closer_hemisphere
    cdef DTYPE_FLOAT_T dotprod

    cdef numpy.ndarray[DTYPE_DOUBLE_T, ndim=1] steps = numpy.linspace(0.,2.,Ntheta)
    cdef DTYPE_DOUBLE_T db = bound_coords_1d[1]-bound_coords_1d[0]

    cdef DTYPE_FLOAT_T pos_x,pos_y,pos_z

    cdef DTYPE_DOUBLE_T surf_point_x, surf_point_y,surf_point_z

    cdef DTYPE_UINT32_T cart_ind_x, cart_ind_y, cart_ind_z

    cdef DTYPE_FLOAT_T base_val = bound_coords_1d[0]

    cdef DTYPE_DOUBLE_T xray_val
    
    for phi in Phis:
        for theta in Thetas:
            # We need the ray directions to point *in* to the sphere.
            # In the hemisphere closer to the current pole, that's negative the (outward directed)
            # unit vector of the current pole.
            # In the hemisphere further from the current pole, that's the non-negated unit vector.
            #
            surf_point_x = px[theta,phi]
            surf_point_y = py[theta,phi]
            surf_point_z = pz[theta,phi]
            dotprod = (surf_point_x*dx_in +
                       surf_point_y*dy_in +
                       surf_point_z*dz_in)
            # The closer hemisphere is where the dot product of the position and the outward directed
            # pole vector is positive and vice-versa for the further hemisphere.
            closer_hemisphere = (dotprod > 0.)
            if closer_hemisphere:
                dx = -dx_in
                dy = -dy_in
                dz = -dz_in
            else:
                dx = dx_in
                dy = dy_in
                dz = dz_in

            # The approximated xray_projection value is the dot product of
            # the local radial vector field, and the direction of the current pole
            xray_val = (radial_cartesian_field[0,theta,phi] * dx +
                        radial_cartesian_field[1,theta,phi] * dy +
                        radial_cartesian_field[2,theta,phi] * dz )
                       
            # The idea is to step down along the rays, and average in the values
            # Deal with the stuff outside of the sphere shortly...
            # Start at the second entry to avoid divide-by-zero in scaling below.
            for s in steps[1:]:
                pos_x = surf_point_x + s*dx
                pos_y = surf_point_y + s*dy
                pos_z = surf_point_z + s*dz
                if ( (pos_x*pos_x + pos_y*pos_y + pos_z*pos_z) > 1. ):
                    # We are outside the sphere; don't process
                    continue
                cart_ind_x = <DTYPE_UINT32_T> ((pos_x-base_val)/db)
                cart_ind_y = <DTYPE_UINT32_T> ((pos_y-base_val)/db)
                cart_ind_z = <DTYPE_UINT32_T> ((pos_z-base_val)/db)
                sum_buf[cart_ind_x,cart_ind_y,cart_ind_z] += xray_val
                #sum_buf[cart_ind_x,cart_ind_y,cart_ind_z] += xray_val/(s*s)
                count_buf[cart_ind_x,cart_ind_y,cart_ind_z] += 1

    return sum_buf, count_buf
