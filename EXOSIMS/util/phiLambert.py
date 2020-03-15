import numpy as np
import astropy.units as u

def phiLambert(beta):
    """Calculate the phase function. Prototype method uses the Lambert phase 
    function from Sobolev 1975.
    
    Args:
        beta (astropy Quantity array):
            Planet phase angles at which the phase function is to be calculated,
            in units of rad
            
    Returns:
        Phi (ndarray):
            Planet phase function
    
    """
    
    beta = beta.to('rad').value
    Phi = (np.sin(beta) + (np.pi - beta)*np.cos(beta))/np.pi
    
    return Phi