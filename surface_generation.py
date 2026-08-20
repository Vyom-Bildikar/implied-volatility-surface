"""
Interpolating scattered IV points onto a regular surface grid
"""

import numpy as np
from scipy.interpolate import griddata

def build_surface(strikes, T_all, iv_list, grid_size=100):
    
    """Interpolate scatters points onto a regular grid

        Cubic interpolation, with nearest-neighbour interpolation for filling gaps left by cubic
        """
    strike_grid = np.linspace(min(strikes), max(strikes), 100)
    T_grid = np.linspace(min(T_all), max(T_all), 100)
    X, Y = np.meshgrid(strike_grid, T_grid)

    Z_cubic = griddata(
            (strikes, T_all),
            iv_list,
            (X, Y),
            method='cubic'
        )

    Z_nearest = griddata((strikes, T_all), iv_list, (X,Y), method="nearest")
    Z_filled = np.where(np.isnan(Z_cubic), Z_nearest, Z_cubic)
    Z_clamped = np.maximum(Z_filled, 0.01)
    Z_final = Z_clamped

    return X,Y, Z_final 
