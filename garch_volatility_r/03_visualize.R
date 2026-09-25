#!/usr/bin/env Rscript
# ============================================================
# 03_visualize.R
#
# Two figures, both built natively in R with ggplot2:
# 1. Full-sample GARCH(1,1) fitted conditional volatility over time
# 2. Walk-forward GARCH forecast vs realized volatility at each
#    refit point (directly comparable to the sibling Python project's
#    volatility_estimates.png)
# ============================================================

suppressMessages({
  library(fGarch)
  library(ggplot2)
})

data_dir <- "data"
output_dir <- "output"
fig_dir <- file.path(output_dir, "figures")
dir.create(fig_dir, showWarnings = FALSE, recursive = TRUE)

TRADING_DAYS <- 252

theme_set(
  theme_minimal(base_size = 12) +
    theme(
      panel.background = element_rect(fill = "white", color = NA),
      plot.background = element_rect(fill = "white", color = NA),
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(color = "grey90")
    )
)

# ---------- Figure 1: full-sample fitted conditional volatility ----------
df <- read.csv(file.path(data_dir, "itc_price_data.csv"), stringsAsFactors = FALSE)
df$Date <- as.Date(df$Date)
df <- df[order(df$Date), ]
close <- df$Close.Price
dates <- df$Date[-1]
log_returns_pct <- 100 * diff(log(close))

fit <- garchFit(~ garch(1, 1), data = log_returns_pct, trace = FALSE)
cond_vol_annualized <- (fit@sigma.t / 100) * sqrt(TRADING_DAYS)

fitted_df <- data.frame(Date = dates, AnnualizedVol = cond_vol_annualized * 100)

p1 <- ggplot(fitted_df, aes(x = Date, y = AnnualizedVol)) +
  geom_line(color = "#1F3864", linewidth = 0.5) +
  labs(
    title = "ITC: GARCH(1,1) Fitted Conditional Volatility (Full Sample)",
    x = "Date", y = "Annualized Volatility (%)"
  )
ggsave(file.path(fig_dir, "garch_conditional_volatility.png"), p1, width = 10, height = 5, dpi = 150, bg = "white")

# ---------- Figure 2: walk-forward forecast vs realized ----------
wf <- read.csv(file.path(output_dir, "garch_walk_forward.csv"), stringsAsFactors = FALSE)
wf$Date <- as.Date(wf$Date)

wf_long <- data.frame(
  Date = rep(wf$Date, 2),
  Volatility = c(wf$ForecastVol, wf$RealizedVol) * 100,
  Series = rep(c("GARCH(1,1) Forecast", "Realized (next 20 days)"), each = nrow(wf))
)

p2 <- ggplot(wf_long, aes(x = Date, y = Volatility, color = Series)) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.5) +
  scale_color_manual(values = c("GARCH(1,1) Forecast" = "#1F3864", "Realized (next 20 days)" = "black")) +
  labs(
    title = "ITC: Walk-Forward GARCH(1,1) Volatility Forecast vs Realized",
    x = "Refit Date", y = "Annualized Volatility (%)", color = NULL
  ) +
  theme(legend.position = "top")
ggsave(file.path(fig_dir, "garch_walk_forward.png"), p2, width = 10, height = 5.5, dpi = 150, bg = "white")

cat("Saved figures to output/figures/\n")
