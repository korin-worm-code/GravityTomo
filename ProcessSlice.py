import numpy
import pyfftw
from numba import jit

@jit(nopython=True,cache=True)
def accumulate(Ntheta, Nphi, cart_inds, xray_val):
    
    sum_buf = numpy.zeros((Ntheta,Ntheta,Ntheta),dtype=numpy.float32)
    for i in range(Ntheta):
        for j in range(Nphi):
            x,y,z = cart_inds[i,j,:]
            sum_buf[x,y,z] += xray_val[i,j]
    return sum_buf


def dot(x1,y1,z1,x2,y2,z2):
    return (x1*x2 + y1*y2 + z1*z2)

def processSlice(Ntheta,Nphi,bound_coords_1d,
                 radial_cartesian_field,
                 pos_x_hat,pos_y_hat,pos_z_hat,
                 rx,ry,rz):
    """Calculate the FFT slice for a given Cartesian radius vector."""

    # This is the dot product of each position vector on the sphere with
    # the current radius vector
    proj_scalar = dot(rx,ry,rz,pos_x_hat,pos_y_hat,pos_z_hat)
    
    # And these are the positions of the projections onto
    # a slice through the origin that is normal to the current radius vector
    slice_posns = (pos_x_hat - proj_scalar*rx,
                   pos_y_hat - proj_scalar*ry,
                   pos_z_hat - proj_scalar*rz)

    # These are the Cartesian voxel (array) indices of the slice projections
    cart_inds = numpy.stack((numpy.digitize(slice_posns[0],bound_coords_1d),
                             numpy.digitize(slice_posns[1],bound_coords_1d),
                             numpy.digitize(slice_posns[2],bound_coords_1d)), axis=2) - 1

    # These are the values of Xray transform approximation
    xray_val = dot(radial_cartesian_field[0],
                   radial_cartesian_field[1],
                   radial_cartesian_field[2],
                   rx,ry,rz)
                         
    # This sums the values from xray_val into the slice's voxels
    sum_buf = accumulate(Ntheta,Nphi,cart_inds,xray_val)

    # While this counts the number of values accumulated into the slice's voxels
    # Not done in the accumulate function because of memory issues...
    nx,ny,comps = cart_inds.shape
    rci = numpy.reshape(cart_inds,(nx*ny,3))
    count_buf,edges = numpy.histogramdd(rci,(Ntheta,Ntheta,Ntheta))

    # This calculates the average value in the voxels
    mask = (count_buf <> 0.)
    sum_buf[mask] /= count_buf[mask]

    # This takes the forward 3DFFT of the voxel buffer
    csum_buf = pyfftw.interfaces.numpy_fft.fftn(sum_buf,threads=8)

    # And this zeros out all elements of the complex result away from the slice plane.
    # According to the generalized Fourier Slice Theorem of Ng(2005), that is
    # equal to the 2D transform in the slice but already in the correct orientation in
    # the 3DFFT. 
    csum_buf[count_buf == 0] = 0.j

    return csum_buf
    
