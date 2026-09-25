from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_loader import SUPPORTED_STOCKS
from prediction import generate_stock_analysis, get_or_train_model
from schemas import (
    StocksListResponse,
    StockItem,
    ApiResponse,
    AnalyzeResponseData,
    PredictionData,
    MetricsData,
    BacktestData
)

app = FastAPI(
    title="StockSense API",
    description="ML-powered stock trend prediction backend for Indian equities",
    version="1.0.0"
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "StockSense API",
        "status": "online",
        "version": "1.0.0",
        "supported_stocks": list(SUPPORTED_STOCKS.keys())
    }

@app.get("/api/stocks", response_model=ApiResponse)
def get_stocks():
    """
    Returns the list of available Indian stocks for analysis.
    """
    stocks = [
        {"ticker": ticker, "name": name, "exchange": "NSE"}
        for ticker, name in SUPPORTED_STOCKS.items()
    ]
    return ApiResponse(success=True, data=stocks)

@app.get("/api/stock/{ticker}", response_model=ApiResponse)
def get_stock_overview(ticker: str):
    """
    Returns latest price, daily change, and chart data for the ticker.
    """
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = generate_stock_analysis(ticker)
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
        return ApiResponse(success=True, data=overview)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.get("/api/prediction/{ticker}", response_model=ApiResponse)
def get_stock_prediction(ticker: str):
    """
    Returns the next trading day ML direction prediction and confidence.
    """
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = generate_stock_analysis(ticker)
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
        return ApiResponse(success=True, data=prediction)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.get("/api/metrics/{ticker}", response_model=ApiResponse)
def get_model_metrics(ticker: str):
    """
    Returns evaluation metrics from the untouched test set.
    """
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = generate_stock_analysis(ticker)
        return ApiResponse(success=True, data=data["metrics"])
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.get("/api/backtest/{ticker}", response_model=ApiResponse)
def get_backtest_results(ticker: str):
    """
    Returns backtest performance of the ML strategy vs Buy & Hold on the test set.
    """
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = generate_stock_analysis(ticker)
        return ApiResponse(success=True, data=data["backtest"])
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.get("/api/analyze/{ticker}", response_model=ApiResponse)
def get_full_analysis(ticker: str):
    """
    Unified single-page endpoint returning price, prediction, chart, indicators,
    model metrics, and backtest performance in a single round-trip.
    """
    if ticker not in SUPPORTED_STOCKS:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' not supported.")
    try:
        data = generate_stock_analysis(ticker)
        return ApiResponse(success=True, data=data)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))
