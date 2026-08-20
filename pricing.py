"""
Black-Scholes option pricing and implied volatility solving
"""

import math

def N(x):
    """Standard normal CDF"""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def d1_d2(S, K, T, r, sigma):
    """Compute the BS d1 and d2 terms"""
    d1 = (math.log(S/K) + (r + 0.5*(sigma)**2) *T)/(sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return d1, d2

def black_scholes(S, K, T, R, sigma, option="call"):
    """Price an European call or put option using BS"""
    d1, d2 = d1_d2(S, K, T, R, sigma)
    disc_r = math.exp(-R *T)
    
    if option.lower() == "call":
        return S * N(d1) - K * disc_r * N(d2)
    elif option.lower() == "put":
        return K * disc_r * N(-d2) - S * N(-d1)
    else:
        raise ValueError("option must be call or put")

def implied_vol(market_price, S, K, T, R, option="call", tol=1e-6):
    """Work backwards from market price via bisection search to get implied volatiltiy"""
    lo, hi = 1e-6, 5.0
    for u in range(100):
        mid = (lo + hi) / 2
        price = black_scholes(S, K, T, R, mid, option)
        if abs(price-market_price)<tol:
            return mid
        if price>market_price:
            hi=mid
        else:
            lo=mid
    return None
