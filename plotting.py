"""
Rendering 3D IV surface plot for visualisation. Includes spot price ref plane
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_surface(ticker, spot, strikes, T_all, iv_list, X, Y, Z, save_path=None):
    fig = plt.figure(figsize=(10,6))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.9)
    Y_plane = np.linspace(min(T_all), max(T_all), 50)
    Z_plane = np.linspace(min(iv_list), max(iv_list), 50)
    Y_mesh, Z_mesh = np.meshgrid(Y_plane, Z_plane)
    X_mesh = np.full_like(Y_mesh, spot)
    ax.plot_surface(X_mesh, Y_mesh, Z_mesh, color="gray", alpha = 0.2)
    
    ax.set_xlabel("Strike Price (K)")
    ax.set_ylabel("Time to Expiry (Years)")
    ax.set_zlabel("Implied Volatility")
    ax.set_title(f"Implied Volatility Surface for {ticker}")
    fig.colorbar(surf, shrink=0.5, aspect = 10)
    
    plt.show()
