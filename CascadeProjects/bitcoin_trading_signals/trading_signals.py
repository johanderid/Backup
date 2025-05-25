import ccxt
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
import schedule
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_signals.log'),
        logging.StreamHandler()
    ]
)

class CryptoSignalAnalyzer:
    def __init__(self, symbol='BTC/USD'):
        self.exchange = ccxt.kraken()
        self.timeframe = '1d'
        self.symbol = symbol
        
    def fetch_historical_data(self, since=None):
        """Fetch historical OHLCV data"""
        try:
            # If since is not provided, default to one year ago
            if since is None:
                since = int((datetime.now() - pd.Timedelta(days=365)).timestamp() * 1000)
            
            # Fetch OHLCV data with 1-day timeframe
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=self.symbol,
                timeframe='1d',
                since=since,
                limit=500  # Add a reasonable limit to ensure we get enough data
            )
            
            if not ohlcv:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
            
        except Exception as e:
            logging.error(f"Error fetching historical data for {self.symbol}: {e}")
            return None

    def fetch_comparison_data(self):
        """Fetch data for price comparisons"""
        try:
            now = datetime.now()
            
            # Get timestamps for comparison periods
            last_week = int((now - pd.Timedelta(days=7)).timestamp() * 1000)
            last_month = int((now - pd.Timedelta(days=30)).timestamp() * 1000)
            last_year = int((now - pd.Timedelta(days=365)).timestamp() * 1000)
            
            # Fetch historical data
            df = self.fetch_historical_data(since=last_year)
            if df is None:
                logging.error(f"No historical data available for {self.symbol}")
                return None
            
            # Get current price
            current_price = df['close'].iloc[-1]
            
            # Get comparison prices using rolling windows
            df.set_index('timestamp', inplace=True)
            df = df.sort_index()
            
            # Find closest matches for each timeframe
            last_week_price = df[df.index >= pd.Timestamp.now() - pd.Timedelta(days=7)].iloc[0]['close']
            last_month_price = df[df.index >= pd.Timestamp.now() - pd.Timedelta(days=30)].iloc[0]['close']
            last_year_price = df[df.index >= pd.Timestamp.now() - pd.Timedelta(days=365)].iloc[0]['close']
            
            # Calculate percentage changes
            weekly_change = ((current_price - last_week_price) / last_week_price * 100)
            monthly_change = ((current_price - last_month_price) / last_month_price * 100)
            yearly_change = ((current_price - last_year_price) / last_year_price * 100)
            
            return {
                'current': current_price,
                'last_week': last_week_price,
                'last_month': last_month_price,
                'last_year': last_year_price,
                'weekly_change': weekly_change,
                'monthly_change': monthly_change,
                'yearly_change': yearly_change
            }
            
        except Exception as e:
            logging.error(f"Error fetching comparison data for {self.symbol}: {e}")
            return None

    def get_detailed_sentiment(self):
        """Get detailed market sentiment"""
        try:
            df = self.fetch_historical_data()
            if df is None:
                return None
                
            # Calculate simple moving averages
            df['SMA20'] = df['close'].rolling(window=20).mean()
            df['SMA50'] = df['close'].rolling(window=50).mean()
            df['SMA200'] = df['close'].rolling(window=200).mean()
            
            current_price = df['close'].iloc[-1]
            sma20 = df['SMA20'].iloc[-1]
            sma50 = df['SMA50'].iloc[-1]
            sma200 = df['SMA200'].iloc[-1]
            
            # Determine trend based on moving averages
            trend = 'Neutral'
            if current_price > sma20 and current_price > sma50 and current_price > sma200:
                trend = 'Strong Uptrend'
            elif current_price < sma20 and current_price < sma50 and current_price < sma200:
                trend = 'Strong Downtrend'
            elif current_price > sma50 and current_price > sma200:
                trend = 'Uptrend'
            elif current_price < sma50 and current_price < sma200:
                trend = 'Downtrend'
            
            return {
                'market_summary': {
                    'Trend': trend,
                    'Price vs SMA20': f"{'Above' if current_price > sma20 else 'Below'}",
                    'Price vs SMA50': f"{'Above' if current_price > sma50 else 'Below'}",
                    'Price vs SMA200': f"{'Above' if current_price > sma200 else 'Below'}"
                },
                'technical_indicators': {
                    'SMA20': f"${sma20:.2f}",
                    'SMA50': f"${sma50:.2f}",
                    'SMA200': f"${sma200:.2f}"
                }
            }
            
        except Exception as e:
            logging.error(f"Error getting detailed sentiment for {self.symbol}: {e}")
            return None

    def run_analysis(self):
        """Run technical analysis and return trading signal"""
        try:
            df = self.fetch_historical_data()
            if df is None:
                return None
            
            # Calculate moving averages
            df['SMA20'] = df['close'].rolling(window=20).mean()
            df['SMA50'] = df['close'].rolling(window=50).mean()
            
            # Get latest values
            current_price = df['close'].iloc[-1]
            sma20 = df['SMA20'].iloc[-1]
            sma50 = df['SMA50'].iloc[-1]
            
            # Generate signal based on moving average crossover
            signal = 'hold'
            if current_price > sma20 and current_price > sma50:
                signal = 'buy'
            elif current_price < sma20 and current_price < sma50:
                signal = 'sell'
            
            return {
                'signal': signal,
                'current': current_price
            }
            
        except Exception as e:
            logging.error(f"Error running analysis for {self.symbol}: {e}")
            return None

def main():
    analyzer = CryptoSignalAnalyzer(symbol='BTC/USD')
    result = analyzer.run_analysis()
    print(result)  # Print the result directly

if __name__ == "__main__":
    main()
