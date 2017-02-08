import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import pyshtools as sht
import numpy as np

def buildImage(depth,T_SH,max_degree=2190,filter_parm = 5.e-10):
        R_E = 6371000.
        r_inner = R_E - depth
        P_degrees = np.arange(0,max_degree+1,1.)
        P_coeffs = (1./R_E)*np.sqrt((4.*np.pi)/((2*P_degrees)+1.))*(r_inner/R_E)**(P_degrees)
        # We need to fully populate the array in memory otherwise the fortran code barfs...
        forward_op_SH = np.zeros_like(T_SH)
        forward_op_SH[:,:,0] = P_coeffs[np.newaxis,:]
        sh_degree = np.arange(T_SH.shape[1])
        factor = 2.*np.pi*np.sqrt((4.*np.pi)/(1+(2*sh_degree)))
        BP_op_deg_0 = forward_op_SH[:,:,0]*factor[np.newaxis,:]

        Stab_FBP_SH = (BP_op_deg_0[:,:,np.newaxis] / ((BP_op_deg_0**2 + (filter_parm/R_E))[:,:,np.newaxis])) * T_SH
        ret_grid = sht.MakeGridDH(Stab_FBP_SH,sampling=2,csphase=-1,norm=4)
        return ret_grid
