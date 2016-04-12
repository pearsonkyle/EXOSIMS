from EXOSIMS.Prototypes.SimulatedUniverse import SimulatedUniverse
import numpy as np
import astropy.units as u
import astropy.constants as const

class KnownRVPlanetsUniverse(SimulatedUniverse):
    """
    Simulated universe implementation inteded to work with the Known RV planet
    planetary population and target list implementations.
    
    Args: 
        \*\*specs: 
            user specified values
            
    Attributes: 

    Notes:
        
    """

    def __init__(self, **specs):

        SimulatedUniverse.__init__(self, **specs)

    def gen_planetary_systems(self,**specs):
        """
        Generate the planetary systems for the current simulated universe.
        This routine populates arrays of the orbital elements and physical 
        characteristics of all planets, and generates indexes that map from 
        planet to parent star.

        All parameters are generated by adding consistent error terms to the 
        catalog values for each planet.
        """

        TL = self.TargetList
        PPop = self.PlanetPopulation
        PPMod = self.PlanetPhysicalModel

        # Go through the target list and pick out the planets belonging to those hosts
        starinds = np.array([])
        planinds = np.array([])
        for j,name in enumerate(TL.Name):
            tmp = np.where(PPop.hostname == name)[0]
            planinds = np.hstack((planinds,tmp))
            starinds = np.hstack((starinds,[j]*len(tmp)))
        planinds = planinds.astype(int)
        starinds = starinds.astype(int)
        # map planets to stars in standard format
        self.plan2star = starinds
        self.sInds = np.unique(self.plan2star)
        self.nPlans = len(planinds)

        #populate parameters
        self.a = PPop.sma[planinds] +  np.random.normal(size=self.nPlans)\
                *PPop.smaerr[planinds]                      # semi-major axis
        self.e = PPop.eccentricity[planinds] + np.random.normal(size=self.nPlans)\
                *PPop.eccentricityerr[planinds]             # eccentricity
        self.e[self.e < 0.] = 0.
        self.e[self.e > 0.9] = 0.9
        self.w = PPop.gen_w(self.nPlans)                    # argument of periapsis
        self.O = lper.data*u.deg - self.w                   # longitude of ascending node
        self.O[np.isnan(self.O)] =  PPop.gen_O(len(np.where(np.isnan(self.O))[0]))
        self.I = PPop.allplanetdata['pl_orbincl'][planinds] + np.random.normal\
                (size=self.nPlans)*PPop.allplanetdata['pl_orbinclerr1'][planinds] 
        self.I[self.I.mask] = PPop.gen_I(len(np.where(self.I.mask)[0])).to('deg').value
        self.I = self.I.data*u.deg                          # inclination
        lper = PPop.allplanetdata['pl_orblper'][planinds] + \
                np.random.normal(size=self.nPlans)*PPop.allplanetdata['pl_orblpererr1'][planinds] 
        self.Mp = PPop.mass[planinds]                       # mass
        self.Rp = PPMod.calc_radius_from_mass(self.Mp)      # radius
        self.p = PPMod.calc_albedo_from_sma(self.a)         # albedo
        self.r, self.v = self.planet_pos_vel()              # initial position
        self.d = np.sqrt(np.sum(self.r**2, axis=1))         # planet-star distance
        self.s = np.sqrt(np.sum(self.r[:,0:2]**2, axis=1))  # apparent separation
        
        # exo-zodi levels for systems with planets
        self.fEZ = self.ZodiacalLight.fEZ(self.TargetList,self.plan2star,self.I)

