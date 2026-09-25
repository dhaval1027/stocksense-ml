from typing import Tuple, List, Dict, Any
import numpy as np
import pandas as pd

FEATURE_COLUMNS: List[str] = [
    "return_1d",
    "return_5d",
    "return_10d",
    "intraday_return",
    "range_ratio",
    "upper_wick",
    "lower_wick",
    "sma_10_ratio",
    "sma_20_ratio",
    "sma_50_ratio",
    "ema_10_ratio",
    "ema_20_ratio",
    "ema_cross_ratio",
    "momentum_10d",
    "rsi_14",
    "rsi_slope_3d",
    "macd",
    "macd_signal",
    "macd_hist",
    "macd_hist_slope",
    "stoch_k",
    "stoch_d",
    "bb_percent_b",
    "volatility_20d",
    "volume_change_1d",
    "volume_ratio_20d",
    "vol_mom_5d",
]

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI) using Wilder's smoothing.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's exponential smoothing
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi

def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes all technical indicators and feature columns without future lookahead.
    Operates strictly on OHLCV data.
    """
    data = df.copy()

    # Returns
    data["return_1d"] = data["Close"].pct_change(1)
    data["return_5d"] = data["Close"].pct_change(5)
    data["return_10d"] = data["Close"].pct_change(10)

    # Intraday Candlestick Dynamics
    data["intraday_return"] = (data["Close"] - data["Open"]) / (data["Open"] + 1e-10)
    data["range_ratio"] = (data["High"] - data["Low"]) / (data["Close"] + 1e-10)
    data["upper_wick"] = (data["High"] - data[["Open", "Close"]].max(axis=1)) / (data["Close"] + 1e-10)
    data["lower_wick"] = (data[["Open", "Close"]].min(axis=1) - data["Low"]) / (data["Close"] + 1e-10)

    # Moving Averages
    data["sma_10"] = data["Close"].rolling(window=10).mean()
    data["sma_20"] = data["Close"].rolling(window=20).mean()
    data["sma_50"] = data["Close"].rolling(window=50).mean()
    data["ema_10"] = data["Close"].ewm(span=10, adjust=False).mean()
    data["ema_20"] = data["Close"].ewm(span=20, adjust=False).mean()

    # Normalized Moving Average Ratios (Stationary features)
    data["sma_10_ratio"] = (data["Close"] / data["sma_10"]) - 1.0
    data["sma_20_ratio"] = (data["Close"] / data["sma_20"]) - 1.0
    data["sma_50_ratio"] = (data["Close"] / data["sma_50"]) - 1.0
    data["ema_10_ratio"] = (data["Close"] / data["ema_10"]) - 1.0
    data["ema_20_ratio"] = (data["Close"] / data["ema_20"]) - 1.0
    data["ema_cross_ratio"] = (data["ema_10"] - data["ema_20"]) / (data["Close"] + 1e-10)

    # Momentum
    data["momentum_10d"] = (data["Close"] / data["Close"].shift(10)) - 1.0

    # RSI (14) & Acceleration
    data["rsi_14"] = calculate_rsi(data["Close"], period=14)
    data["rsi_slope_3d"] = data["rsi_14"] - data["rsi_14"].shift(3)

    # MACD (12, 26, 9)
    ema_12 = data["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = data["Close"].ewm(span=26, adjust=False).mean()
    data["macd"] = ema_12 - ema_26
    data["macd_signal"] = data["macd"].ewm(span=9, adjust=False).mean()
    data["macd_hist"] = data["macd"] - data["macd_signal"]
    data["macd_hist_slope"] = data["macd_hist"] - data["macd_hist"].shift(2)

    # Stochastic Oscillator (14, 3)
    low_14 = data["Low"].rolling(14).min()
    high_14 = data["High"].rolling(14).max()
    data["stoch_k"] = 100.0 * ((data["Close"] - low_14) / (high_14 - low_14 + 1e-10))
    data["stoch_d"] = data["stoch_k"].rolling(3).mean()

    # Bollinger Bands (20, 2)
    bb_rolling_std = data["Close"].rolling(window=20).std()
    data["bb_middle"] = data["sma_20"]
    data["bb_upper"] = data["bb_middle"] + (2.0 * bb_rolling_std)
    data["bb_lower"] = data["bb_middle"] - (2.0 * bb_rolling_std)
    bb_width = data["bb_upper"] - data["bb_lower"]
    data["bb_percent_b"] = (data["Close"] - data["bb_lower"]) / (bb_width + 1e-10)

    # Rolling Volatility (20-day annualized std of returns)
    data["volatility_20d"] = data["return_1d"].rolling(window=20).std() * np.sqrt(252)

    # Volume Features
    data["volume_change_1d"] = data["Volume"].pct_change(1).replace([np.inf, -np.inf], 0)
    data["volume_sma_20"] = data["Volume"].rolling(window=20).mean()
    data["volume_ratio_20d"] = (data["Volume"] / (data["volume_sma_20"] + 1e-10)) - 1.0
    data["vol_mom_5d"] = (data["Volume"] / (data["Volume"].rolling(5).mean() + 1e-10)) - 1.0

    return data

def build_features_and_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Computes technical features and target variable.
    Target = 1 if next day's Close > today's Close, else 0.
    
    Returns:
    - X: DataFrame of features (NaN dropped)
    - y: Series of binary targets (aligned with X)
    - clean_df: Full DataFrame containing raw prices and indicators for charting
    """
    df_feat = compute_all_indicators(df)

    # Next day target: Close at t+1 > Close at t
    next_day_close = df_feat["Close"].shift(-1)
    df_feat["target"] = (next_day_close > df_feat["Close"]).astype(int)

    # Valid mask
    valid_mask = df_feat[FEATURE_COLUMNS].notna().all(axis=1) & df_feat.index.isin(df_feat.index[:-1])
    
    clean_training_df = df_feat[valid_mask].copy()
    X = clean_training_df[FEATURE_COLUMNS]
    y = clean_training_df["target"].astype(int)

    return X, y, df_feat

def get_latest_feature_vector(df_feat: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Extracts the feature vector from the most recent available trading day (for live inference),
    along with latest indicator values for dashboard display.
    """
    latest_row = df_feat.iloc[-1]
    
    # In case the very latest row has any NaN, fallback to previous valid row
    if latest_row[FEATURE_COLUMNS].isna().any():
        valid_indices = df_feat[FEATURE_COLUMNS].dropna().index
        if len(valid_indices) == 0:
            raise ValueError("No valid indicator rows found.")
        latest_row = df_feat.loc[valid_indices[-1]]

    X_latest = pd.DataFrame([latest_row[FEATURE_COLUMNS]])

    # RSI status string
    rsi_val = float(latest_row["rsi_14"])
    if rsi_val >= 70:
        rsi_status = "Overbought"
    elif rsi_val <= 30:
        rsi_status = "Oversold"
    else:
        rsi_status = "Neutral"

    indicators = {
        "rsi": round(rsi_val, 2),
        "rsi_status": rsi_status,
        "macd": round(float(latest_row["macd"]), 2),
        "macd_signal": round(float(latest_row["macd_signal"]), 2),
        "macd_hist": round(float(latest_row["macd_hist"]), 2),
        "sma20": round(float(latest_row["sma_20"]), 2),
        "sma50": round(float(latest_row["sma_50"]), 2),
        "ema20": round(float(latest_row["ema_20"]), 2),
        "volatility": round(float(latest_row["volatility_20d"]) * 100.0, 2),
        "bb_upper": round(float(latest_row["bb_upper"]), 2),
        "bb_middle": round(float(latest_row["bb_middle"]), 2),
        "bb_lower": round(float(latest_row["bb_lower"]), 2),
    }

    return X_latest, indicators
