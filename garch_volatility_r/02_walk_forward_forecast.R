#!/usr/bin/env Rscript
# ============================================================
# 02_walk_forward_forecast.R
#
# Walk-forward GARCH(1,1) volatility forecasting on the same ITC
# series and evaluation design as the sibling Python project
# itc_volatility_forecasting, so the two are directly comparable:
#
#   - Refit GARCH(1,1) every REFIT_EVERY trading days, using only the
#     trailing ROLLING_WINDOW days of returns (never future data).
#   - From each fit, forecast daily volatility FORECAST_HORIZON days
#     ahead, average those daily forecasts, and annualize.
#   - Compare that forecast to the REALIZED volatility actually
#     observed over the same forward FORECAST_HORIZON days (used only
#     for evaluation afterward, never fed into the forecast itself).
#   - Report RMSE, MAE and mean bias, same metrics and same units as
#     the Python project's rolling-window and EWMA methods, for a
#     direct side-by-side comparison.
# ============================================================

suppressMessages(library(fGarch))

data_dir <- "data"
output_dir <- "output"

ROLLING_WINDOW <- 500     # ~2 years of trailing returns used for each refit
REFIT_EVERY <- 20         # trading days between refits
FORECAST_HORIZON <- 20    # trading days ahead forecast, matches the Python project
TRADING_DAYS <- 252

df <- read.csv(file.path(data_dir, "itc_price_data.csv"), stringsAsFactors = FALSE)
df$Date <- as.Date(df$Date)
df <- df[order(df$Date), ]
close <- df$Close.Price
dates <- df$Date[-1]  # returns start one day later than prices
log_returns <- diff(log(close))       # decimal scale, used for realized vol
log_returns_pct <- 100 * log_returns  # percent scale, used for GARCH fitting

n <- length(log_returns)
refit_points <- seq(ROLLING_WINDOW, n - FORECAST_HORIZON, by = REFIT_EVERY)

cat(sprintf("Walk-forward GARCH(1,1): %d refits, window=%d days, horizon=%d days\n\n",
            length(refit_points), ROLLING_WINDOW, FORECAST_HORIZON))

results <- data.frame(
  Date = as.Date(character()),
  ForecastVol = numeric(),
  RealizedVol = numeric()
)

for (t in refit_points) {
  window_returns <- log_returns_pct[(t - ROLLING_WINDOW + 1):t]

  fit <- tryCatch(
    garchFit(~ garch(1, 1), data = window_returns, trace = FALSE),
    error = function(e) NULL
  )
  if (is.null(fit)) next

  pred <- predict(fit, n.ahead = FORECAST_HORIZON)
  # pred$standardDeviation is the forecast daily sigma (percent scale)
  # for each of the next FORECAST_HORIZON days; average then annualize.
  avg_daily_sigma_pct <- mean(pred$standardDeviation)
  forecast_vol_annualized <- (avg_daily_sigma_pct / 100) * sqrt(TRADING_DAYS)

  realized_window <- log_returns[(t + 1):(t + FORECAST_HORIZON)]
  realized_vol_annualized <- sd(realized_window) * sqrt(TRADING_DAYS)

  results <- rbind(results, data.frame(
    Date = dates[t],
    ForecastVol = forecast_vol_annualized,
    RealizedVol = realized_vol_annualized
  ))
}

write.csv(results, file.path(output_dir, "garch_walk_forward.csv"), row.names = FALSE)

error <- results$ForecastVol - results$RealizedVol
rmse <- sqrt(mean(error^2))
mae <- mean(abs(error))
bias <- mean(error)

cat(sprintf("GARCH(1,1) walk-forward forecast evaluation (n=%d):\n", nrow(results)))
cat(sprintf("  RMSE = %.4f\n", rmse))
cat(sprintf("  MAE  = %.4f\n", mae))
cat(sprintf("  Mean bias = %+.4f\n\n", bias))

summary_row <- data.frame(Method = "GARCH_1_1", N = nrow(results), RMSE = rmse, MAE = mae, MeanBias = bias)
write.csv(summary_row, file.path(output_dir, "garch_forecast_evaluation.csv"), row.names = FALSE)

cat("Saved output/garch_walk_forward.csv and output/garch_forecast_evaluation.csv\n")
