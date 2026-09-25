# StockSense — ML Stock Trend Prediction

> **An AI-powered single-page market trend analysis web application for Indian equities.**  
> Built for academic research and college ML curriculum demonstration. Evaluates and compares machine learning classifiers on real historical stock data with strict prevention of look-ahead data leakage.

---

## 1. Project Overview

**StockSense** predicts whether an Indian stock's next trading-day closing price direction is likely to be:
- **↑ UP** ($Close_{t+1} > Close_t$)
- **↓ DOWN** ($Close_{t+1} \le Close_t$)

The system focuses on real data from the **National Stock Exchange of India (NSE)** for three major benchmark equities:
1. `RELIANCE.NS` — Reliance Industries
2. `TCS.NS` — Tata Consultancy Services
3. `HDFCBANK.NS` — HDFC Bank

The entire interface is delivered as a **single-page dashboard** without sidebars, logins, multi-page routing, or unnecessary clutter. Everything is immediately visible: live price, daily percentage change, next-day ML prediction, model confidence, historical price chart with 20-day SMA, technical indicators, test-set performance metrics, and a backtesting simulation.

---

## 2. Key Features

- **Strict Single-Page Design**: Clean, modern financial dashboard aesthetic built with React, Vite, and Tailwind CSS.
- **Genuine ML Pipeline**: No hardcoded dummy predictions or mock metrics. All figures come from actual trained classifiers and test calculations.
- **Strict Chronological Splitting**: Guarantees zero look-ahead bias and no data leakage. Preprocessing scalers are fitted exclusively on training sets.
- **Hyperparameter Tuning via TimeSeriesSplit**: Cross-validation respects time order. Randomized search tunes hyperparameters on training data.
- **Model Comparison & Selection**: Evaluates Logistic Regression, Random Forest, and XGBoost on validation data, selecting the best model using **Validation F1 Score**.
- **Historical Backtesting Engine**: Evaluates an ML-guided strategy (Long when UP, Cash when DOWN) on the untouched test period with a realistic **0.1% transaction cost** per trade switch.
- **Automatic Caching**: Daily data from Yahoo Finance is cached locally to prevent redundant downloads. Models are trained once and persisted via `joblib`.

---

## 3. Architecture

```
StockSense Architecture
┌────────────────────────────────────────────────────────┐
│             React Single-Page Application              │
│        (Vite + Tailwind CSS + Recharts + Lucide)       │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP JSON (Port 5173 -> 8000)
┌───────────────────────────▼────────────────────────────┐
│                    FastAPI Backend                     │
│                  (main.py / schemas.py)                │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
┌──────────────▼──────────┐    ┌──────────▼──────────────┐
│    Inference Service    │    │  Training & Backtesting │
│     (prediction.py)     │    │   (models.py, backtest) │
└──────────────┬──────────┘    └──────────┬──────────────┘
               │                          │
┌──────────────▼──────────┐    ┌──────────▼──────────────┐
│  Persisted Pipelines    │    │   Feature Engineering   │
│  (.joblib in /models)   │    │  (RSI, MACD, SMA, etc.) │
└─────────────────────────┘    └──────────┬──────────────┘
                                          │
                               ┌──────────▼──────────────┐
                               │  yfinance Data Loader   │
                               │   (Local CSV Cache)     │
                               └─────────────────────────┘
```

---

## 4. Machine Learning Methodology

```
Historical OHLCV Data (2018 - Present)
           │
           ▼
Data Cleaning & Normalization (Standardize Columns, Handle MultiIndex)
           │
           ▼
Technical Feature Engineering (Returns, SMAs, EMAs, RSI, MACD, BB, Volatility, Volume)
           │
           ▼
Next-Day Binary Target Creation (Target_t = 1 if Close_{t+1} > Close_t else 0)
           │
           ▼
Drop Invalid / Boundary Rows (Remove NaNs from Rolling Windows and Last Day)
           │
           ▼
Strict Chronological Split (70% Train | 15% Validation | 15% Untouched Test)
           │
           ▼
Hyperparameter Tuning with TimeSeriesSplit (4 Folds on Train Data Only)
├── Logistic Regression (C, Solver)
├── Random Forest (n_estimators, max_depth, min_samples_split, min_samples_leaf)
└── XGBoost (n_estimators, max_depth, learning_rate, subsample, colsample_bytree)
           │
           ▼
Validation Model Comparison (Select Winner on Validation F1 Score)
           │
           ▼
Final Evaluation on Untouched Test Set (Accuracy, Precision, Recall, F1, ROC-AUC)
           │
           ▼
Model Persistence (.joblib pipeline saved to backend/models/)
           │
           ▼
Test-Period Strategy Backtest (ML Strategy vs Buy & Hold with 0.1% Fee)
```

---

## 5. Strict Prevention of Look-Ahead Data Leakage

Preventing future data leakage is essential in financial machine learning:

1. **Chronological Splitting**: Time-series observations are never randomly shuffled. Shuffling historical price data introduces future information into past predictions.
2. **Strict Target Shift**:
   $$\text{Target}_t = \mathbb{I}(Close_{t+1} > Close_t)$$
   Features at index $t$ are derived **only** from prices up to and including trading day $t$.
3. **Pipeline Preprocessing Isolation**: Feature scalers (`StandardScaler`) are fit solely on the training partition within a scikit-learn `Pipeline`. Scaler parameters (mean, standard deviation) never see validation or test sets during fitting.
4. **Validation-Based Model Selection**: Model architecture and hyperparameter choices are made on the validation set. The test set remains completely untouched until the final evaluation.
5. **TimeSeriesSplit Cross-Validation**: During hyperparameter tuning on the training fold, `TimeSeriesSplit` ensures that training folds always precede test folds in time.

---

## 6. Technical Indicators & Feature Engineering

| Feature | Calculation Method | Role in Model |
| :--- | :--- | :--- |
| **Returns** | 1-Day, 5-Day, and 10-Day percentage price changes | Captures recent short-term price velocity |
| **SMA 10, 20, 50** | Simple Moving Averages normalized as $(Close / SMA) - 1$ | Trend direction and mean-reversion signals |
| **EMA 10, 20** | Exponential Moving Averages normalized as $(Close / EMA) - 1$ | Weighting toward recent price momentum |
| **Momentum** | 10-day price momentum $(Close_t / Close_{t-10}) - 1$ | Trend strength over a two-week horizon |
| **RSI (14)** | Relative Strength Index using Wilder's exponential smoothing | Overbought (>70) and Oversold (<30) oscillation |
| **MACD** | $EMA_{12} - EMA_{26}$, 9-day Signal line, and Histogram | Momentum convergence/divergence indicator |
| **Bollinger Bands** | 20-day SMA $\pm 2\sigma$, %B oscillator $(Close - Lower) / (Upper - Lower)$ | Volatility boundaries and price breakouts |
| **Volatility** | 20-day rolling standard deviation of daily returns annualized $(\times \sqrt{252})$ | Market risk regime indicator |
| **Volume Ratio** | Current volume normalized against 20-day average volume | Buying/selling conviction indicator |

---

## 7. Models Implemented

1. **Logistic Regression** (Linear Baseline)
   - Fast, interpretable linear classification with L2 regularization.
   - Preprocessed with `StandardScaler` inside pipeline.
2. **Random Forest Classifier** (Non-linear Ensemble)
   - Bagging ensemble of decision trees.
   - Robust against outliers and non-linear feature interactions.
3. **XGBoost Classifier** (Gradient Boosted Trees)
   - Sequentially minimizes log-loss using gradient boosted trees.
   - Regularized via L2 penalty (`reg_lambda`) and feature subsampling.

---

## 8. Strategy Backtesting Simulation

The backtest evaluates whether following the ML model's direction signals on the **untouched test period** provides utility compared to a passive **Buy & Hold** benchmark:

- **Rule**:
  - If $\hat{y}_t = 1$ (UP): Hold the stock from day $t$ to $t+1$.
  - If $\hat{y}_t = 0$ (DOWN): Hold cash ($0.0\%$ return).
- **Realistic Transaction Costs**:
  - A fee of **0.1% (10 bps)** is subtracted whenever a position switch occurs (Cash $\leftrightarrow$ Stock).
- **Metrics Calculated**:
  - **Strategy Cumulative Return (%)**
  - **Buy & Hold Cumulative Return (%)**
  - **Maximum Drawdown (%)**
  - **Trade Win Rate (%)**
  - **Signal Counts (UP vs DOWN)**

---

## 9. Project Structure

```
Final/
├── backend/
│   ├── main.py                  # FastAPI server with CORS & endpoints
│   ├── schemas.py               # Pydantic data schemas
│   ├── data_loader.py           # yfinance fetcher with local CSV caching
│   ├── features.py              # Technical indicator calculation
│   ├── models.py                # Chronological split, model selection & evaluation
│   ├── tuning.py                # TimeSeriesSplit hyperparameter tuning
│   ├── prediction.py            # Live inference service
│   ├── backtest.py              # Test-period strategy simulation
│   ├── train_all.py             # Script to pre-train all models and generate reports
│   ├── requirements.txt         # Python dependencies
│   ├── data/                    # Cached historical stock CSVs
│   ├── models/                  # Saved .joblib model pipelines
│   └── reports/                 # JSON tuning reports & test metrics
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx       # Branding header
│   │   │   ├── StockSelector.jsx# Stock dropdown & Analyze button
│   │   │   ├── SummaryCards.jsx # Price, Daily Change, Prediction, Confidence
│   │   │   ├── PriceChart.jsx   # Interactive Recharts Line chart (Close + SMA 20)
│   │   │   ├── Indicators.jsx   # RSI, MACD, SMA 20, Volatility grid
│   │   │   ├── ModelMetrics.jsx # Accuracy, Precision, Recall, F1, ROC-AUC
│   │   │   └── Backtest.jsx     # Strategy return vs Buy & Hold, Drawdown
│   │   ├── App.jsx              # Main Single-Page Application
│   │   ├── api.js               # Backend API client
│   │   ├── main.jsx             # React entrypoint
│   │   └── index.css            # Tailwind CSS custom styling
│   ├── package.json             # NPM dependencies
│   ├── vite.config.js           # Vite dev server with /api proxy
│   └── tailwind.config.js       # Tailwind theme configuration
├── README.md                    # Project documentation
└── .gitignore                   # Git ignore file
```

---

## 10. Installation & Running Instructions

### Prerequisites
- **Python 3.10+** (Python 3.13 tested)
- **Node.js 18+** (Node v20 tested) and `npm`

### Step 1: Clone or Navigate to the Project
```bash
cd Final
```

### Step 2: Backend Setup & Running
Navigate into the `backend/` directory and install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

*(Optional)* Train all models and produce evaluation reports ahead of time:
```bash
python train_all.py
```

Start the FastAPI backend server:
```bash
uvicorn main:app --reload --port 8000
```
The backend API will be available at `http://127.0.0.1:8000`.  
Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

### Step 3: Frontend Setup & Running
Open a second terminal window and navigate into the `frontend/` directory:
```bash
cd frontend
npm install
npm run dev
```
Open your browser and navigate to:
```
http://127.0.0.1:5173
```

---

## 11. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/stocks` | Lists all supported Indian stocks (`RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`) |
| `GET` | `/api/stock/{ticker}` | Returns current price, daily change, and chart data points |
| `GET` | `/api/prediction/{ticker}`| Returns next trading day direction (`UP`/`DOWN`) and probability |
| `GET` | `/api/metrics/{ticker}` | Returns test-set performance metrics (Accuracy, Precision, Recall, F1) |
| `GET` | `/api/backtest/{ticker}` | Returns backtest results (Strategy Return, Buy & Hold, Drawdown) |
| `GET` | `/api/analyze/{ticker}` | Unified single-page payload returning all of the above in one call |

---

## 12. Academic & Educational Disclaimer

> **Educational Project Only**: This application is built strictly for academic demonstration and research into time-series machine learning. Market price predictions are probabilistic estimations based on historical technical indicators and do not constitute financial advice, investment recommendations, or guaranteed returns. Real-world financial markets are subject to exogenous shocks, policy changes, and liquidity fluctuations.
