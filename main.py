"""
Implied Volatility Surface Generator
-------------------------------------
Fetches live options data for a given stock ticker, computes implied
volatility for each contract using the Black-Scholes model, and plots
a 3D implied volatility surface (strike x time-to-expiry x IV).
 
Usage:
    python main.py --ticker AAPL
"""
import argparse

from data import fetch_iv_data, filter_iv
from surface_generation import build_surface
from plotting import plot_surface

def main():
    parser = argparse.ArgumentParser(description="Generate an implied volatility surface for a stock ticker.")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker symbol, e.g. AAPL")
    parser.add_argument("--rate", type=float, default=0.045, help="Risk-free rate (default: 0.045)")
    parser.add_argument("--max-expiries", type=int, default=15, help="Number of expiries to pull (default: 15)")
    args = parser.parse_args()
 
    print(f"Fetching options data for {args.ticker}...")
    spot, strikes, T_all, iv_list = fetch_iv_data(args.ticker, r=args.rate, max_expiries=args.max_expiries)
 
    strikes, T_all, iv_list = filter_iv(spot, strikes, T_all, iv_list)
 
    if len(strikes) < 4:
        raise SystemExit("Not enough valid data points to build a surface. Try a more liquid ticker.")
 
    print(f"Building surface from {len(strikes)} data points...")
    X, Y, Z = build_surface(strikes, T_all, iv_list)
 
    plot_surface(args.ticker, spot, strikes, T_all, iv_list, X, Y, Z)
 
 
if __name__ == "__main__":
    main()
