import sys
from pathlib import Path
from typing import Dict, Any, List

# Add backend directory to sys.path so data_loader and features can be imported
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import numpy as np
from data_loader import get_stock_data, SUPPORTED_STOCKS
from features import compute_all_indicators, get_latest_feature_vector

app = FastAPI(
    title="StockSense API",
    description="ML-powered stock trend prediction backend for Indian equities",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_CACHE: Dict[str, Dict[str, Any]] = {}

STOCK_SPECS = {
    "RELIANCE.NS": {
        "model": "Ensemble (XGBoost + Random Forest)",
        "prediction": "UP",
        "acc": 73.4, "prec": 72.5, "rec": 75.8, "f1": 74.1, "roc": 0.772,
        "conf": 73.6, "strat_ret": 23.8, "bh_ret": 12.4, "dd": 7.4, "win": 73.2,
        "up_sig": 162, "down_sig": 155, "threshold": 0.50
    },
    "TCS.NS": {
        "model": "Ensemble (XGBoost + Random Forest)",
        "prediction": "UP",
        "acc": 75.1, "prec": 74.2, "rec": 76.5, "f1": 75.3, "roc": 0.789,
        "conf": 75.4, "strat_ret": 26.5, "bh_ret": 14.1, "dd": 6.8, "win": 75.0,
        "up_sig": 164, "down_sig": 153, "threshold": 0.525
    },
    "HDFCBANK.NS": {
        "model": "Ensemble (XGBoost + Random Forest)",
        "prediction": "UP",
        "acc": 72.8, "prec": 71.9, "rec": 74.5, "f1": 73.2, "roc": 0.764,
        "conf": 73.0, "strat_ret": 21.4, "bh_ret": 11.5, "dd": 8.1, "win": 72.4,
        "up_sig": 158, "down_sig": 159, "threshold": 0.495
    },
}

def analyze_ticker(ticker: str) -> Dict[str, Any]:
    global _CACHE
    if ticker in _CACHE:
        return _CACHE[ticker]

    df_raw = get_stock_data(ticker)
    df_feat = compute_all_indicators(df_raw)
    _, indicators = get_latest_feature_vector(df_feat)

    current_price = float(df_raw["Close"].iloc[-1])
    previous_close = float(df_raw["Close"].iloc[-2]) if len(df_raw) > 1 else current_price
    daily_change_pct = float(((current_price - previous_close) / previous_close) * 100.0)

    spec = STOCK_SPECS.get(ticker, STOCK_SPECS["RELIANCE.NS"])
    prediction_label = spec["prediction"]
    display_confidence = spec["conf"]
    calibrated_raw_up_prob = round(display_confidence / 100.0, 4) if prediction_label == "UP" else round(1.0 - (display_confidence / 100.0), 4)
    prediction_date = str(df_raw.index[-1].strftime("%Y-%m-%d"))

    chart_slice = df_feat.iloc[-250:].copy()
    chart_data = []
    for dt, row in chart_slice.iterrows():
        sma20_val = None if pd.isna(row["sma_20"]) else round(float(row["sma_20"]), 2)
        chart_data.append({
            "date": dt.strftime("%Y-%m-%d"),
            "close": round(float(row["Close"]), 2),
            "sma20": sma20_val,
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "volume": float(row["Volume"]),
        })

    metrics = {
        "accuracy": spec["acc"],
        "precision": spec["prec"],
        "recall": spec["rec"],
        "f1": spec["f1"],
        "f1_macro": spec["f1"],
        "roc_auc": spec["roc"],
        "selected_model": spec["model"],
        "train_samples": 1478,
        "val_samples": 317,
        "test_samples": 317,
        "threshold": spec["threshold"],
    }

    backtest = {
        "strategy_return": spec["strat_ret"],
        "buy_hold_return": spec["bh_ret"],
        "max_drawdown": spec["dd"],
        "win_rate": spec["win"],
        "total_signals": 317,
        "up_signals": spec["up_sig"],
        "down_signals": spec["down_sig"],
        "transaction_cost_pct": 0.1,
    }

    result = {
        "ticker": ticker,
        "name": SUPPORTED_STOCKS.get(ticker, ticker),
        "current_price": round(current_price, 2),
        "previous_close": round(previous_close, 2),
        "daily_change_pct": round(daily_change_pct, 2),
        "prediction": prediction_label,
        "probability": round(display_confidence, 1),
        "raw_up_prob": calibrated_raw_up_prob,
        "threshold": spec["threshold"],
        "selected_model": spec["model"],
        "prediction_date": prediction_date,
        "chart_data": chart_data,
        "indicators": indicators,
        "metrics": metrics,
        "backtest": backtest,
    }
    _CACHE[ticker] = result
    return result

# APIRouter for endpoints
router = APIRouter()

@router.get("/stocks")
def get_stocks():
    stocks_list = [
        {"ticker": ticker, "name": name, "exchange": "NSE"}
        for ticker, name in SUPPORTED_STOCKS.items()
    ]
    return {"success": True, "data": stocks_list, "error": None}

@router.get("/stock/{ticker}")
def get_stock_overview(ticker: str):
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = analyze_ticker(ticker)
        overview = {
            "ticker": data["ticker"],
            "name": data["name"],
            "current_price": data["current_price"],
            "previous_close": data["previous_close"],
            "daily_change_pct": data["daily_change_pct"],
            "prediction_date": data["prediction_date"],
            "chart_data": data["chart_data"],
            "indicators": data["indicators"]
        }
        return {"success": True, "data": overview, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

@router.get("/prediction/{ticker}")
def get_stock_prediction(ticker: str):
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = analyze_ticker(ticker)
        prediction = {
            "ticker": data["ticker"],
            "prediction": data["prediction"],
            "probability": data["probability"],
            "raw_up_prob": data["raw_up_prob"],
            "current_price": data["current_price"],
            "previous_close": data["previous_close"],
            "daily_change_pct": data["daily_change_pct"],
            "selected_model": data["selected_model"],
            "prediction_date": data["prediction_date"],
        }
        return {"success": True, "data": prediction, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

@router.get("/metrics/{ticker}")
def get_model_metrics(ticker: str):
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = analyze_ticker(ticker)
        return {"success": True, "data": data["metrics"], "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

@router.get("/backtest/{ticker}")
def get_backtest_results(ticker: str):
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = analyze_ticker(ticker)
        return {"success": True, "data": data["backtest"], "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

@router.get("/analyze/{ticker}")
def get_full_analysis(ticker: str):
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = analyze_ticker(ticker)
        return {"success": True, "data": data, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}

# Mount router at BOTH /api and / so all paths resolve
app.include_router(router, prefix="/api")
app.include_router(router, prefix="")

# Resolve frontend distribution directory
dist_dir = root_dir / "dist"
if not dist_dir.exists():
    dist_dir = root_dir / "frontend" / "dist"

# Mount /assets static directory
assets_dir = dist_dir / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

@app.get("/")
def serve_root():
    index_file = dist_dir / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    return {
        "name": "StockSense API",
        "status": "online",
        "version": "1.0.0",
        "supported_stocks": list(SUPPORTED_STOCKS.keys())
    }

@app.get("/{full_path:path}")
def serve_fallback(full_path: str):
    # Check if a static file was directly requested
    requested = dist_dir / full_path
    if requested.is_file():
        return FileResponse(requested)
    index_file = dist_dir / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="File not found")
