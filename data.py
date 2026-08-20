import datetime
import math

import numpy as np
import yfinance as yf

from pricing import implied_vol

def fetch_iv_data(ticker, r=0.045, max_expiries=15):
    """ Pull option chains for a ticker and compute implied volatiltiy points.

    returns:
    current spot price, numpy array of strike, time-to-expiry and IV
    """
    stock = yf.Ticker(ticker)
    S = stock.history(period="1d")['Close'].iloc[-1]
    strikes = []
    iv_list = []
    T_all = []
    
    for expiry in stock.options[:max_expiries]: 
        opt_chain = stock.option_chain(expiry)
        calls = opt_chain.calls
        puts = opt_chain.puts

        expiry_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        today = datetime.date.today()
        T = (expiry_date - today).days / 365
        
        """Prevents math errors in BS"""
        if T < 0.01:
            continue

        for opt_type, df in [("call", opt_chain.calls), ("put", opt_chain.puts)]:
            for x, row in df.iterrows():
                K = row["strike"]

                volume = row.get("volume", 0)
                if volume == 0 or math.isnan(volume):
                    continue
                
                """Only OTM options used due to being more liquid"""
                if opt_type == "call" and K < S:
                    continue
                if opt_type == "put" and K >= S:
                    continue

                bid = row.get("bid", 0)
                ask = row.get("ask", 0)
                last_price = row.get("lastPrice", 0)
                """Filter to remove bid-ask spreads that are too wide with 30% benchmark"""
                if bid> 0 and ask > 0:
                    mid = (bid+ask)/2
                    spread = (ask - bid) / mid
                    if spread > 0.3:
                        continue
                    market_price = mid
                elif last_price > 0:
                    market_price = last_price
                    
                else:
                    continue
                
                iv = implied_vol(market_price,S,K,T,r,opt_type)
                if iv is not None and 0.01 < iv < 3:
                        strikes.append(K)
                        iv_list.append(iv)
                        T_all.append(T)
    strikes = np.array(strikes)
    iv_list = np.array(iv_list)
    T_all = np.array(T_all)
    spot = S        
    return spot, strikes, T_all, iv_list


def filter_iv(spot, strikes, T_all, iv_list):
    """Remove outlier strikes/expiries/IVs to keep surface even"""
    mask_strikes = (strikes > 0.85 * spot) & (strikes < 1.15 * spot)
    mask_expiries = (T_all > 0.02) & (T_all < 1.0)
    mask_iv = (iv_list > 0.01) & (iv_list < 5.0)

    mask = mask_strikes & mask_expiries & mask_iv
    return strikes[mask], T_all[mask], iv_list[mask]
