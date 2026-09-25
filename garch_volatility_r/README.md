# GARCH(1,1) Volatility Modeling in R

Fits a GARCH(1,1) model to ITC's daily returns in R (fGarch), the
model promised as a follow-up in the "Possible extensions" section of
the sibling Python project `itc_volatility_forecasting`, and compares
its walk-forward forecast accuracy against that project's three
simpler methods (20-day rolling, 60-day rolling, EWMA) on the exact
same evaluation design, so the four are directly comparable.

## What this project shows

- Genuine R usage end to end: data loading, model fitting (fGarch),
  and native ggplot2 visualization, not just a Python analysis with
  an R wrapper
- A model diagnosed properly before being trusted: Ljung-Box tests on
  the squared standardized residuals check whether GARCH(1,1) actually
  removed the volatility clustering it was fit to capture, not just
  whether the optimizer converged
- An honest comparison across four methods and two languages, with the
  smaller sample size of the walk-forward GARCH evaluation stated
  plainly rather than quietly ignored when it makes GARCH's edge look
  less conclusive

## Data source

Same ITC price series as `itc_volatility_forecasting`
(`data/itc_price_data.csv`, copied from that project): 1,253 trading
days, 15 September 2021 to 15 September 2026, from the NSE Security-wise
Price Volume Archives.

## Repository structure

```
garch_volatility_r/
  install_packages.R           installs fGarch and ggplot2 from CRAN
  01_fit_garch.R                  full-sample GARCH(1,1) fit and diagnostics
  02_walk_forward_forecast.R       walk-forward forecast, same design as the Python project
  03_visualize.R                     ggplot2 figures
  data/itc_price_data.csv        ITC daily price data
  output/                        coefficients, walk-forward results, figures
```

## Setup

```bash
git clone <your-repo-url>
cd garch_volatility_r
Rscript install_packages.R
```

## Usage

```bash
Rscript 01_fit_garch.R                # prints model summary, writes garch_full_sample_coefficients.csv
Rscript 02_walk_forward_forecast.R    # writes garch_walk_forward.csv, garch_forecast_evaluation.csv
Rscript 03_visualize.R                # writes output/figures/*.png
```

## Methodology

**Model**: GARCH(1,1) on daily log returns (in percent, the
conventional scale for numerical stability), fit with `fGarch::garchFit()`.

    r_t = mu + epsilon_t
    sigma_t^2 = omega + alpha1 * epsilon_{t-1}^2 + beta1 * sigma_{t-1}^2

**Full-sample diagnostics** (all 1,252 daily returns): checks whether
the fitted model is a reasonable specification before using it for
anything, via the standard tests fGarch reports automatically
(Ljung-Box on residuals and squared residuals, Jarque-Bera normality).

**Walk-forward forecast**, matched to the Python project's design so
the two are comparable:

- Refit GARCH(1,1) every 20 trading days, using only the trailing 500
  days of returns (never future data)
- From each fit, forecast daily volatility 20 days ahead, average
  those daily forecasts, and annualize
- Compare against the realized volatility actually observed over that
  same forward 20-day window (used only for scoring afterward)
- Report RMSE, MAE and mean bias, the same three metrics and units the
  Python project used

## Results

**Full-sample GARCH(1,1) fit**:

    omega  = 0.554  (SE 0.144, p < 0.001)
    alpha1 = 0.134  (SE 0.041, p = 0.001)
    beta1  = 0.546  (SE 0.104, p < 0.001)

- alpha1 + beta1 = 0.68, comfortably below 1, so the fitted model is
  stationary (volatility shocks decay rather than explode)
- Both alpha1 and beta1 are highly statistically significant: there is
  real, detectable volatility clustering in this series for GARCH(1,1)
  to capture
- **Ljung-Box test on squared standardized residuals**: p = 0.969 to
  0.999 at lags 10, 15, and 20. High p-values here are the good
  outcome: they mean no significant volatility clustering is left over
  after fitting, i.e. the model actually did its job
- Jarque-Bera and Shapiro-Wilk both strongly reject normality of the
  standardized residuals (p < 0.0001), an expected result for daily
  equity returns and a sign that a Student-t innovation distribution
  (a one-line change in fGarch) would likely fit better than the
  normal assumption used here

**Walk-forward forecast comparison, all four methods** (RMSE/MAE/bias
in annualized-volatility units, lower is better for RMSE/MAE):

| Method | N | RMSE | MAE | Mean Bias |
|---|---|---|---|---|
| 20-Day Rolling (Python) | 1,213 | 0.0785 | 0.0594 | +0.0024 |
| 60-Day Rolling (Python) | 1,173 | 0.0693 | 0.0527 | +0.0095 |
| EWMA, lambda=0.94 (Python) | 1,213 | 0.0731 | 0.0545 | +0.0070 |
| **GARCH(1,1) (R)** | **37** | **0.0680** | **0.0522** | **+0.0185** |

- **GARCH(1,1) has the lowest RMSE and MAE of all four methods**, but
  only marginally ahead of the 60-day rolling window (RMSE 0.0680 vs
  0.0693, about a 2 percent improvement), and it has the largest mean
  bias of the four (systematically over-forecasting realized
  volatility by 1.85 percentage points on average, versus 0.24 to 0.95
  points for the other three).
- **This comparison is not on equal footing, and that matters more
  than the RMSE ranking**: the GARCH walk-forward evaluation has only
  37 refit points (constrained by needing a 500-day trailing window
  before the first fit, then refitting only every 20 days), versus
  1,173 to 1,213 daily observations for the three Python methods. A
  10-percentage-point sample-size difference this large means GARCH's
  narrow RMSE win is well within what could be noise; it should be
  read as "GARCH performed competitively," not as "GARCH proven best."
- **The walk-forward chart makes this visible directly**
  (`garch_walk_forward.png`): the GARCH forecast (navy) is
  substantially smoother than the realized volatility (black), and
  visibly misses several of the sharpest realized spikes, most clearly
  in 2025, where realized volatility jumps to 34% while the forecast
  stays near 18.5%.

See `output/figures/`:
1. `garch_conditional_volatility.png`: the full-sample fitted
   conditional volatility, showing the classic GARCH volatility-
   clustering pattern (spikes that decay back toward a baseline level)
2. `garch_walk_forward.png`: the 37 walk-forward forecasts against
   realized volatility, the chart behind the comparison table above

## Limitations

- **The walk-forward GARCH sample (37 points) is much smaller than the
  Python methods' (1,173-1,213 points)**, stated above and repeated
  here because it is the single most important caveat on the headline
  RMSE result
- **Single stock, single model specification**: no comparison against
  EGARCH, GJR-GARCH (which would let bad news and good news have
  different volatility impact, a well-documented equity-market
  asymmetry this plain GARCH(1,1) cannot capture), or a Student-t
  innovation distribution, despite the normality test result above
  suggesting the last one would likely help
- **Refitting only every 20 days** (rather than daily) is a
  computational-cost tradeoff, not a methodological choice; a daily
  refit would use more information per forecast at the cost of far
  more compute
- Same corporate-action caveat as `nse_itc_analysis` and
  `itc_volatility_forecasting`: the price series is not adjusted for
  ITC's demergers and bonus issues in this window

## Possible extensions

- Refit daily instead of every 20 days, for a walk-forward sample
  size comparable to the Python methods' evaluation
- Try a Student-t innovation distribution (`cond.dist = "std"` in
  `garchFit`) given the normality rejection above
- Try GJR-GARCH or EGARCH to test for a leverage effect (does a large
  negative return raise forecast volatility more than an equally large
  positive one?)
- Extend to the other stocks already covered elsewhere in this
  portfolio, to see whether GARCH's edge over simpler methods holds up
  outside ITC

## License

MIT
