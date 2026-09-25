import time
from data_loader import SUPPORTED_STOCKS, get_stock_data
from features import build_features_and_target
from models import train_and_select_best_model
from prediction import get_or_train_model

def main():
    print("=" * 60)
    print("StockSense ML Model Training & Hyperparameter Tuning Pipeline")
    print(f"Supported stocks: {list(SUPPORTED_STOCKS.keys())}")
    print("=" * 60)

    start_total = time.time()
    for ticker, name in SUPPORTED_STOCKS.items():
        print(f"\nProcessing {name} ({ticker})...")
        t0 = time.time()
        # force_retrain=True to ensure clean tuning and persistence
        bundle = get_or_train_model(ticker, force_retrain=True)
        print(f"Successfully processed {ticker} in {time.time() - t0:.1f}s")
        print(f"Selected Model: {bundle['selected_model']}")
        print(f"Test Accuracy: {bundle['test_metrics']['accuracy']*100:.2f}% | F1: {bundle['test_metrics']['f1']*100:.2f}%")
        print(f"Backtest Strategy Return: {bundle['backtest_results']['strategy_return']}% vs Buy & Hold: {bundle['backtest_results']['buy_hold_return']}%")

    print("\n" + "=" * 60)
    print(f"ALL 3 STOCKS TRAINED, TESTED, AND PERSISTED in {time.time() - start_total:.1f}s")
    print("=" * 60)

if __name__ == "__main__":
    main()
