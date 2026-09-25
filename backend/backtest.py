from typing import Dict, Any, List
import numpy as np
import pandas as pd

def run_test_period_backtest(
    test_indices: List[Any],
    test_preds: np.ndarray,
    df_raw: pd.DataFrame,
    cost_per_switch: float = 0.001  # 0.1% per trade switch
) -> Dict[str, Any]:
    """
    Simulates the ML trading strategy exclusively over the test set:
    - If prediction == 1 (UP): Hold the asset from today's close to tomorrow's close.
    - If prediction == 0 (DOWN): Hold cash (0.0 return).
    - Deducts realistic transaction fee (cost_per_switch) whenever the position flips (Cash <-> Stock).
    """
    # Extract actual test-period prices
    test_slice = df_raw.loc[test_indices].copy()
    
    # Calculate forward 1-day returns for each test day
    # Next day close:
    next_close = df_raw["Close"].shift(-1).loc[test_indices]
    current_close = test_slice["Close"]
    daily_asset_returns = (next_close - current_close) / current_close

    strategy_returns = []
    current_position = 0  # 0 = Cash, 1 = Stock
    
    wins = 0
    total_trades = 0

    for i, pred in enumerate(test_preds):
        r_asset = daily_asset_returns.iloc[i]
        new_position = int(pred)
        
        # Transaction cost incurred if switching position
        fee = cost_per_switch if (new_position != current_position) else 0.0
        current_position = new_position

        if new_position == 1:
            # Invested in stock
            net_return = r_asset - fee
            strategy_returns.append(net_return)
            if r_asset > 0:
                wins += 1
            total_trades += 1
        else:
            # In cash
            net_return = 0.0 - fee
            strategy_returns.append(net_return)

    strat_ret_arr = np.array(strategy_returns)
    asset_ret_arr = daily_asset_returns.fillna(0).values

    # Equity curves
    strat_equity = np.cumprod(1.0 + strat_ret_arr)
    buy_hold_equity = np.cumprod(1.0 + asset_ret_arr)

    # Strategy Cumulative Return
    total_strat_return = float(strat_equity[-1] - 1.0) if len(strat_equity) > 0 else 0.0
    total_buy_hold_return = float(buy_hold_equity[-1] - 1.0) if len(buy_hold_equity) > 0 else 0.0

    # Max Drawdown calculation
    peaks = np.maximum.accumulate(strat_equity)
    drawdowns = (strat_equity - peaks) / (peaks + 1e-10)
    max_drawdown = float(np.abs(np.min(drawdowns))) if len(drawdowns) > 0 else 0.0

    # Win rate
    win_rate = float(wins / total_trades) if total_trades > 0 else 0.0

    up_signals = int(np.sum(test_preds == 1))
    down_signals = int(np.sum(test_preds == 0))

    return {
        "strategy_return": round(total_strat_return * 100.0, 2),  # In percentage
        "buy_hold_return": round(total_buy_hold_return * 100.0, 2),  # In percentage
        "max_drawdown": round(max_drawdown * 100.0, 2),  # In percentage
        "win_rate": round(win_rate * 100.0, 2),  # In percentage
        "total_signals": len(test_preds),
        "up_signals": up_signals,
        "down_signals": down_signals,
        "transaction_cost_pct": round(cost_per_switch * 100.0, 2)
    }
