# Implied Volatility Surface  
# About the project
A Python project which pulls live options data for a given stock ticker via yfinance and backs out the Black-Scholes implied volatility for each contract. Implied volatility is a measure of how much the market believes the price of a stock or asset will move in the future and can be used to quantify market sentiment and uncertainty. The aim of this project was for research into a market's view of an equity such as Apple. I wanted to build the program so I could understand why the surface looked like it did and understand the mathematics underneath it all.

# How it works 
1. Prompts for a stock ticker (I used AAPL) and pulls its live option chain via 'yfinance'
2. For every liquid call and put across the first 15 expiries, the market's IV is computed by inverting the Black-Scholes formula
3. Illiquid, wide-spread or numerically unstable quotes are filtered
4. IV points are scattered and interpolated along the axes: strike, expiry, IV
5. Plots a 3D surface with a vertical plane marking the current spot price so you can visualise the smile and how it splits into OTM calls vs OTM puts

# Underlying Mathematics 
## Black-Scholes Formula
The script prices a European option under the standard Black-Scholes assumptions (lognormal stock price, constant volatility and risk-free rate, no dividends, no early exercise) 

**Variables**
 
| Symbol | Meaning |
|---|---|
| $S$ | Current stock price (spot) |
| $K$ | Strike price |
| $T$ | Time to expiry, in years |
| $r$ | Risk-free rate (hardcoded to 4.5%) |
| $\sigma$ | Volatility (the unknown we're solving for) |
| $N(x)$ | Standard normal CDF |

**The two intermediate terms** 

$$
d_1 = \frac{\ln(S/K) + \left(r + \dfrac{\sigma^2}{2}\right)T}{\sigma\sqrt{T}}
\qquad\qquad
d_2 = d_1 - \sigma\sqrt{T}
$$
 
**Option prices**
 
$$
C = S\,N(d_1) \;-\; K e^{-rT} N(d_2)
$$
 
$$
P = K e^{-rT} N(-d_2) \;-\; S\,N(-d_1)
$$ 
A call's price is the discounted expected payoff
$\max(S_T - K,\, 0)$ under the risk-neutral measure. $N(d_2)$ is the
(risk-neutral) probability the option finishes in the money, and $S\,N(d_1)$
is the present value of receiving the stock conditional on that. The put
price follows from put-call parity. 

## Bisection Search 

Black-Scholes gives a price from a volatility. The market gives a price and we are trying to find what volatility it implies. There is no closed-form inverse so we use a bisection search to solve it numerically. 

Define:
 
$$
f(\sigma) = \text{BS}(\sigma) - P_{\text{market}}
$$
 
where $\text{BS}(\sigma)$ is the Black-Scholes price at volatility $\sigma$
and $P_{\text{market}}$ is the observed mid/last price. Implied volatility is
the $\sigma$ that makes $f(\sigma) = 0$. 

**Why Bisection?** 
Black-Scholes price is an increasing, continuous function of $\sigma$ 

**Process** 
1. Start with a bracket $[\,\sigma_{lo},\, \sigma_{hi}\,] = [0.0001\%,\ 500\%]$ — wide enough to contain any realistic implied vol.
2. Price the option at the midpoint $\sigma_{mid} = \dfrac{\sigma_{lo} + \sigma_{hi}}{2}$.
3. Since price increases with $\sigma$, if the model price is **too high**, the true vol is **lower** → new bracket $[\sigma_{lo}, \sigma_{mid}]$. If **too low**, the true vol is **higher** → new bracket $[\sigma_{mid}, \sigma_{hi}]$
4. We repeat until $\lvert \text{BS}(\sigma_{mid}) - P_{\text{market}} \rvert < \text{tolerance}$. I set the tolerance to 0.000001.

## Restrictions 
- Any expiry under 3.65 days is skipped as bisection gets numerically unstable as T → 0.
- Calls with K < S and puts with K >= S are skipped. I focussed on OTM contracts as they tend to be the most liquid and they trade on pure time value rather than intrinsic value of ITM contracts.
- Zero-volume contracts are skipped
- Wide bid-ask spreads are skipped due to the fact that it signals low liquidity and price uncertainty.

##Filtering and Data cleaning 
After collecting every (strike, expiry, IV) triple, a second filtering pass
narrows the dataset before interpolation:
 
- **Strikes:** kept within ±15% of spot — deep wings are thin, noisy, and
  would otherwise dominate the interpolation's extrapolated corners.
- **Expiries:** kept between roughly 1 week and 1 year — very short-dated
  contracts are noisy (see above) and LEAPS are sparse enough to distort the
  grid.
- **IV:** re-clipped to (0.01, 5.0) as a final sanity bound.

Surviving scattered points are then interpolated onto a regular 100x100 grid and we use cubic interpolation initially.

- Cubic does not extrapolate `NaN` points so these gaps filled with nearest-neighbour interpolation for a smoother surface.
- Combined surface is clamped at a 1% floor so no interpolation dips into negative volatility.

# Visual Output
![Implied volatility surface for AAPL](assets/AAPL-iv-surface.png)

