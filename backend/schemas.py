from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class StockItem(BaseModel):
    ticker: str
    name: str
    exchange: str = "NSE"

class StocksListResponse(BaseModel):
    success: bool = True
    stocks: List[StockItem]

class ChartDataPoint(BaseModel):
    date: str
    close: float
    sma20: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[float] = None

class PredictionData(BaseModel):
    ticker: str
    prediction: str = Field(description="UP or DOWN")
    probability: float = Field(description="Model confidence probability between 0.50 and 1.00")
    raw_up_prob: float = Field(description="Raw probability of UP class between 0.0 and 1.0")
    current_price: float
    previous_close: float
    daily_change_pct: float
    selected_model: str
    prediction_date: str

class MetricsData(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
    f1_macro: Optional[float] = None
    roc_auc: float
    selected_model: str
    train_samples: int
    val_samples: int
    test_samples: int
    threshold: Optional[float] = None

class BacktestData(BaseModel):
    strategy_return: float
    buy_hold_return: float
    max_drawdown: float
    win_rate: float
    total_signals: int
    up_signals: int
    down_signals: int
    transaction_cost_pct: float = 0.1

class TechnicalIndicators(BaseModel):
    rsi: float
    rsi_status: str
    macd: float
    macd_signal: float
    macd_hist: float
    sma20: float
    sma50: float
    ema20: float
    volatility: float
    bb_upper: float
    bb_middle: float
    bb_lower: float

class AnalyzeResponseData(BaseModel):
    ticker: str
    name: str
    current_price: float
    previous_close: float
    daily_change_pct: float
    prediction: str
    probability: float
    raw_up_prob: Optional[float] = None
    threshold: Optional[float] = None
    selected_model: str
    prediction_date: str
    chart_data: List[ChartDataPoint]
    indicators: TechnicalIndicators
    metrics: MetricsData
    backtest: BacktestData

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
