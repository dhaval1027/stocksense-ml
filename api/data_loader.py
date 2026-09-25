import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Optional, Dict
import pandas as pd
import yfinance as yf

# Base data directory
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Supported stocks mapping
SUPPORTED_STOCKS: Dict[str, str] = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
}

def get_official_live_price(ticker: str) -> Optional[float]:
    """
    Fetches the exact real-time / post-market auction settled price from Google Finance (NSE).
    Matches official exchange settlements (e.g. 1,224.70 for Reliance).
    """
    sym = ticker.replace(".NS", "")
    url = f"https://www.google.com/finance/quote/{sym}:NSE"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    )
    try:
        html = urllib.request.urlopen(req, timeout=5).read().decode("utf-8")
        m = re.search(r"<span>₹([0-9,]+\.[0-9]{2})</span>", html)
        if m:
            price = float(m.group(1).replace(",", ""))
            if price > 0:
                return price
    except Exception:
        pass
    return None

def clean_yfinance_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes the DataFrame returned by yfinance.
    Handles MultiIndex columns, duplicates, and missing values.
    """
    if df.empty:
        return df

    # Handle modern yfinance MultiIndex columns (Price, Ticker)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Standardize column names (strip whitespace and title-case)
    df.columns = [str(c).strip().title() for c in df.columns]

    # Required columns
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    available_cols = [c for c in required_cols if c in df.columns]
    
    if len(available_cols) < len(required_cols):
        raise ValueError(f"Missing required columns in price data. Found: {list(df.columns)}")

    df = df[required_cols].copy()

    # Convert numeric columns
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with NaN or zero Close prices
    df = df.dropna(subset=["Close", "Open", "High", "Low"])
    df = df[df["Close"] > 0]

    # Ensure index is datetime and chronologically sorted
    df.index = pd.to_datetime(df.index)
    # Remove timezone information for consistent CSV caching
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    df = df.sort_index()
    # Remove duplicate timestamps
    df = df[~df.index.duplicated(keep="last")]

    return df

def get_stock_data(ticker: str, start_date: str = "2018-01-01", force_refresh: bool = False, max_cache_age_hours: int = 12) -> pd.DataFrame:
    """
    Loads stock historical OHLCV data for the given ticker.
    Checks local CSV cache first; downloads from yfinance if missing or stale.
    """
    if ticker not in SUPPORTED_STOCKS:
        raise ValueError(f"Ticker '{ticker}' is not supported. Supported: {list(SUPPORTED_STOCKS.keys())}")

    cache_path = DATA_DIR / f"{ticker.replace('^', '').replace(':', '_')}.csv"
    now = time.time()

    # Check cache existence and age
    cache_valid = False
    if cache_path.exists() and not force_refresh:
        file_age_hours = (now - cache_path.stat().st_mtime) / 3600
        if file_age_hours < max_cache_age_hours:
            cache_valid = True

    if cache_valid:
        try:
            df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            df = clean_yfinance_dataframe(df)
            if len(df) >= 200:
                # Optionally sync latest live price
                live_price = get_official_live_price(ticker)
                if live_price and len(df) > 0:
                    df.iloc[-1, df.columns.get_loc("Close")] = live_price
                return df
        except Exception as e:
            print(f"[WARN] Failed to read cache for {ticker}: {e}. Falling back to download.")

    # Download from yfinance
    print(f"[INFO] Fetching historical data for {ticker} from yfinance (start={start_date})...")
    try:
        raw_df = yf.download(
            tickers=ticker,
            start=start_date,
            auto_adjust=False,
            progress=False
        )
        cleaned_df = clean_yfinance_dataframe(raw_df)

        if cleaned_df.empty or len(cleaned_df) < 100:
            raise ValueError(f"Downloaded insufficient data for {ticker} ({len(cleaned_df)} rows).")

        # Sync latest price if live official settlement is available
        live_price = get_official_live_price(ticker)
        if live_price and len(cleaned_df) > 0:
            cleaned_df.iloc[-1, cleaned_df.columns.get_loc("Close")] = live_price

        # Save to local CSV cache if filesystem is writable
        try:
            cleaned_df.to_csv(cache_path)
            print(f"[INFO] Cached {len(cleaned_df)} rows for {ticker} to {cache_path}")
        except Exception as write_err:
            print(f"[WARN] Could not write cache to {cache_path} (read-only environment): {write_err}")
        return cleaned_df
    except Exception as e:
        # If download fails, fallback to existing cache if available
        if cache_path.exists():
            print(f"[WARN] Download failed ({e}), loading available cached data.")
            fallback_df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            res_df = clean_yfinance_dataframe(fallback_df)
            live_price = get_official_live_price(ticker)
            if live_price and len(res_df) > 0:
                res_df.iloc[-1, res_df.columns.get_loc("Close")] = live_price
            return res_df
        raise RuntimeError(f"Failed to fetch stock data for {ticker}: {str(e)}")
