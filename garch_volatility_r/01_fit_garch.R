#!/usr/bin/env Rscript
# ============================================================
# 01_fit_garch.R
#
# Fits a GARCH(1,1) model to ITC daily returns (the same NSE price
# series used in the sibling Python project itc_volatility_forecasting)
# using fGarch, and prints the full-sample model summary: parameter
# estimates, standard errors, and standard diagnostic tests
# (Ljung-Box on standardized residuals and their squares, Jarque-Bera
# normality).
#
# This script only fits and reports the full-sample model as a
# diagnostic check that GARCH(1,1) is a reasonable specification for
# this series before using it for the walk-forward forecast in
# 02_walk_forward_forecast.R.
# ============================================================

suppressMessages(library(fGarch))

data_dir <- "data"
output_dir <- "output"
dir.create(output_dir, showWarnings = FALSE)

df <- read.csv(file.path(data_dir, "itc_price_data.csv"), stringsAsFactors = FALSE)
df$Date <- as.Date(df$Date)
df <- df[order(df$Date), ]

# Daily log returns, in percent (the conventional scale for GARCH
# fitting: keeps coefficient magnitudes well away from numerical
# underflow, and is rescaled back to decimal wherever it matters).
close <- df$Close.Price
log_returns_pct <- 100 * diff(log(close))

cat(sprintf("Loaded %d trading days, %d daily returns\n", nrow(df), length(log_returns_pct)))
cat(sprintf("Date range: %s to %s\n\n", df$Date[1], df$Date[nrow(df)]))

fit <- garchFit(~ garch(1, 1), data = log_returns_pct, trace = FALSE)

cat("=== GARCH(1,1) full-sample fit ===\n")
print(summary(fit))

# Save the coefficient table plainly, for the README and for anyone
# who wants the numbers without re-running R.
coefs <- data.frame(
  Parameter = names(coef(fit)),
  Estimate = as.numeric(coef(fit)),
  StdError = as.numeric(fit@fit$se.coef)
)
write.csv(coefs, file.path(output_dir, "garch_full_sample_coefficients.csv"), row.names = FALSE)

cat("\nSaved coefficient table to output/garch_full_sample_coefficients.csv\n")
