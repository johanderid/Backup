# Bitcoin Trading Signals

This application analyzes Bitcoin price movements on Kraken and generates trading signals based on multiple technical indicators and cross-reference validation with external sources.

## Features

- Real-time price monitoring on Kraken exchange
- Technical analysis using multiple indicators:
  - MACD (Moving Average Convergence Divergence)
  - StochRSI (Stochastic Relative Strength Index)
  - Moving Averages (20 and 50 period)
  - OBV (On-Balance Volume)
- Cross-reference validation with Investing.com
- Hourly signal updates
- Detailed logging of all signals and analysis

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python trading_signals.py
```

The application will:
- Generate initial analysis
- Continue running and update signals every hour
- Log all signals to both console and `trading_signals.log`

## Signal Interpretation

The application combines multiple technical indicators and external sentiment to generate signals:
- STRONG BUY/SELL: When 3 or more indicators align
- MODERATE BUY/SELL: When 2 indicators align
- NEUTRAL: When indicators are mixed or unclear

## Notes

- This is a trading signal generator and should not be used as the sole basis for trading decisions
- Always perform your own research and risk assessment
- Past performance does not guarantee future results
