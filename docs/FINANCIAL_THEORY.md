# Financial Concepts Behind the Code

## Black-Scholes Greeks Explained

### Delta (Δ)
- Definition: Rate of change of option price w.r.t. underlying
- Formula: ∂C/∂S
- Practical use: "If my stock position moves €1, how much does my option hedge move?"
- Range: 0 to 1 for calls, -1 to 0 for puts

### Gamma (Γ)
- Definition: Rate of change of Delta
- Why it matters: Tells you when your Delta hedge needs rebalancing
- High Gamma = Higher rehedging costs = More expensive options

### Vega (ν)
- Definition: Sensitivity to implied volatility
- Crisis impact: During market crashes, Vega explodes → hedges become worthless


## Altman Z-Score: When It Breaks

**Not suitable for**:
- Banks & Financial Institutions (different capital structure)
- REITs (asset-heavy, low leverage by design)
- Early-stage growth companies (negative earnings by design)
- Utilities (highly regulated, stable leverage)

**Your code handles this** → User gets a smart warning, not a garbage result.
