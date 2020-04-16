import astropy.units as astropy_units
import numpy as np

import pyatomdb

from astromodels.functions.function import Function1D, FunctionMeta
from astromodels.utils import configuration

from astropy.io import fits
import  os

import pkg_resources

def get_path_of_data_file(data_file):
    file_path = pkg_resources.resource_filename("astromodels", 'data/%s' % data_file)

    return file_path


# APEC class
class APEC(Function1D, metaclass=FunctionMeta):
    r"""
    description :
        The Astrophysical Plasma Emission Code (APEC, Smith et al. 2001)
    parameters :
        K :
            desc : Normalization in units of 1e-14/(4*pi*(1+z)^2*dA*2)*EM
            initial value : 1.0
            is_normalization : True
            transformation : log10
            min : 1e-30
            max : 1e3
            delta : 0.1
        kT :
            desc : Plasma temperature
            initial value : 1.0
            min : 0.08
            max : 64
            delta : 0.1
        abund :
            desc : Metal abundance
            initial value : 1
            min : 0.0
            max : 5.0
            delta : 0.01
            fix : yes
        redshift :
            desc : Source redshift
            initial value : 0.1
            min : 0.0
            max : 10.0
            delta : 1e-3
            fix : yes

    """

    def _set_units(self, x_unit, y_unit):
        self.kT.unit = astropy_units.keV

        self.abund.unit = astropy_units.dimensionless_unscaled

        self.redshift.unit = astropy_units.dimensionless_unscaled

        self.K.unit = astropy_units.ph / astropy_units.s / astropy_units.keV

    def init_session(self, abund_table='AG89'):
        # initialize PyAtomDB session
        self.session = pyatomdb.spectrum.CIESession(abundset=abund_table)

    def evaluate(self, x, K, kT, abund, redshift):
        sess = self.session

        nval = len(x)

        xz = x * (1. + redshift)

        ebplus = (np.roll(xz, -1) + xz)[:nval - 1] / 2.

        ebounds = np.empty(nval + 1)

        ebounds[1:nval] = ebplus

        ebounds[0] = xz[0] - (ebplus[0] - xz[0])

        ebounds[nval] = xz[nval - 1] + (xz[nval - 1] - ebplus[nval - 2])

        binsize = (np.roll(ebounds, -1) - ebounds)[:nval]

        sess.set_response(ebounds, raw=True)

        sess.set_abund(
            [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
            abund)

        spec = sess.return_spectrum(kT) / binsize / 1e-14

        return K * spec


# APEC class
class VAPEC(Function1D, metaclass=FunctionMeta):
    r"""
    description :
        The Astrophysical Plasma Emission Code (APEC, Smith et al. 2001), variable
    parameters :
        K :
            desc : Normalization in units of 1e-14/(4*pi*(1+z)^2*dA*2)*EM
            initial value : 1.0
            is_normalization : True
            transformation : log10
            min : 1e-30
            max : 1e3
            delta : 0.1
        kT :
            desc : Plasma temperature
            initial value : 1.0
            min : 0.08
            max : 64
            delta : 0.1
        abund :
            desc : Metal abundance
            initial value : 1
            min : 0.0
            max : 5.0
            delta : 0.01
            fix : yes
        redshift :
            desc : Source redshift
            initial value : 0.1
            min : 0.0
            max : 10.0
            delta : 1e-3
            fix : yes

    """

    def _set_units(self, x_unit, y_unit):
        self.kT.unit = astropy_units.keV

        self.abund.unit = astropy_units.dimensionless_unscaled

        self.redshift.unit = astropy_units.dimensionless_unscaled

        self.K.unit = astropy_units.ph / astropy_units.s / astropy_units.keV

    def init_session(self, abund_table='AG89'):
        # initialize PyAtomDB session
        self.session = pyatomdb.spectrum.CIESession(abundset=abund_table)

    def evaluate(self, x, K, kT, abund, redshift):
        sess = self.session

        nval = len(x)

        xz = x * (1. + redshift)

        ebplus = (np.roll(xz, -1) + xz)[:nval - 1] / 2.

        ebounds = np.empty(nval + 1)

        ebounds[1:nval] = ebplus

        ebounds[0] = xz[0] - (ebplus[0] - xz[0])

        ebounds[nval] = xz[nval - 1] + (xz[nval - 1] - ebplus[nval - 2])

        binsize = (np.roll(ebounds, -1) - ebounds)[:nval]

        sess.set_response(ebounds, raw=True)

        sess.set_abund(
            [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
            abund)

        spec = sess.return_spectrum(kT) / binsize / 1e-14

        return K * spec


# PhAbs class
class PhAbs(Function1D, metaclass=FunctionMeta):
    r"""
    description :
        Photometric absorption (phabs implementation), f(E) = exp(- NH * sigma(E))
    parameters :
        NH :
            desc : absorbing column density in units of 1e22 particles per cm^2
            initial value : 1.0
            is_normalization : True
            transformation : log10
            min : 1e-4
            max : 1e4
            delta : 0.1
    """

    def _set_units(self, x_unit, y_unit):
        self.NH.unit = astropy_units.cm ** 2

    def init_xsect(self, abund_table='AG89'):
        # load cross section data

        path_to_xsect = os.path.join(configuration.get_user_data_path() , 'xsect')

        if abund_table == 'AG89':
            fxs = fits.open(path_to_xsect + '/xsect_phabs_angr.fits')

        elif abund_table == 'ASPL':
            fxs = fits.open(path_to_xsect + '/xsect_phabs_aspl.fits')
        else:
            print('Unknown abundace table %s, reverting to AG89' % (abund_table))
            fxs = fits.open(path_to_xsect + '/xsect_phabs_angr.fits')

        dxs = fxs[1].data
        self.xsect_ene = dxs['ENERGY']
        self.xsect_val = dxs['SIGMA']

    def evaluate(self, x, NH):
        assert self.xsect_ene is not None and self.xsect_val is not None

        xsect_interp = np.interp(x, self.xsect_ene, self.xsect_val)

        spec = np.exp( - NH * xsect_interp)

        return spec

# TbAbs class
class TbAbs(Function1D, metaclass=FunctionMeta):
    r"""
    description :
        Photometric absorption (Tbabs implementation), f(E) = exp(- NH * sigma(E))
    parameters :
        NH :
            desc : absorbing column density in units of 1e22 particles per cm^2
            initial value : 1.0
            is_normalization : True
            transformation : log10
            min : 1e-4
            max : 1e4
            delta : 0.1
    """

    def _set_units(self, x_unit, y_unit):
        self.NH.unit = astropy_units.cm ** 2

    def init_xsect(self, abund_table='AG89'):
        # load cross section data

        path_to_xsect = os.path.join(configuration.get_user_data_path() , 'xsect')

        if abund_table == 'AG89':
            fxs = fits.open(path_to_xsect + '/xsect_tbabs_angr.fits')
        elif abund_table == 'ASPL':
            fxs = fits.open(path_to_xsect + '/xsect/xsect_tbabs_aspl.fits')
        elif abund_table == 'WILM':
            fxs = fits.open(path_to_xsect + '/xsect/xsect_tbabs_wilm.fits')
        else:
            print('Unknown abundace table %s, reverting to WILM' % (abund_table))
            fxs = fits.open(path_to_xsect + '/xsect/xsect_tbabs_wilm.fits')

        dxs = fxs[1].data
        self.xsect_ene = dxs['ENERGY']
        self.xsect_val = dxs['SIGMA']

    def evaluate(self, x, NH):
        assert self.xsect_ene is not None and self.xsect_val is not None

        xsect_interp = np.interp(x, self.xsect_ene, self.xsect_val)

        spec = np.exp( - NH * xsect_interp)

        return spec