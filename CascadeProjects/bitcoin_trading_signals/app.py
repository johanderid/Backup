import logging
from flask import Flask, render_template, jsonify, request
from trading_signals import CryptoSignalAnalyzer
from datetime import datetime
import time
import threading

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global variable to store analysis results
analysis_results = {}

def update_analysis():
    """Update analysis for all pairs"""
    global analysis_results
    pairs = ['BTC/USD', 'ETH/USD', 'ETH/BTC']
    
    for pair in pairs:
        try:
            analyzer = CryptoSignalAnalyzer(pair)
            
            # Get signal analysis
            signal_data = analyzer.run_analysis()
            if signal_data is None:
                logging.error(f"Failed to get signal analysis for {pair}")
                continue
                
            # Get comparison data
            comparison = analyzer.fetch_comparison_data()
            if comparison is None:
                logging.error(f"Failed to get comparison data for {pair}")
                continue
                
            # Get detailed sentiment
            sentiment = analyzer.get_detailed_sentiment()
            if sentiment is None:
                logging.error(f"Failed to get sentiment data for {pair}")
                continue
            
            # Format the data properly
            analysis_results[pair] = {
                'signal': signal_data['signal'],
                'current': float(signal_data['current']),
                'last_week': float(comparison.get('last_week', 0)),
                'last_month': float(comparison.get('last_month', 0)),
                'last_year': float(comparison.get('last_year', 0)),
                'weekly_change': float(comparison.get('weekly_change', 0)),
                'monthly_change': float(comparison.get('monthly_change', 0)),
                'yearly_change': float(comparison.get('yearly_change', 0)),
                'detailed_sentiment': sentiment,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logging.info(f"Updated analysis for {pair}")
            
        except Exception as e:
            logging.error(f"Error updating analysis for {pair}: {e}")

def background_analysis():
    """Background task to update analysis periodically"""
    while True:
        update_analysis()
        time.sleep(300)  # Update every 5 minutes

@app.route('/')
def index():
    """Render main page with analysis results"""
    return render_template('index.html', analysis=analysis_results)

@app.route('/api/analysis')
def get_analysis():
    """API endpoint to get latest analysis results"""
    return jsonify(analysis_results)

@app.route('/api/dca-calculator', methods=['POST'])
def calculate_dca():
    """API endpoint for DCA calculator"""
    data = request.get_json()
    
    # Get parameters from request
    investment_amount = float(data.get('investment_amount', 0))
    frequency = data.get('frequency', 'monthly')  # weekly, monthly
    duration = int(data.get('duration', 12))  # number of months
    
    # Calculate total investment
    num_investments = duration
    if frequency == 'weekly':
        num_investments = duration * 4  # approximate weeks per month
    
    total_investment = investment_amount * num_investments
    
    # Get historical price data for analysis
    analyzer = CryptoSignalAnalyzer('BTC/USD')
    df = analyzer.fetch_historical_data()
    
    if df is None:
        return jsonify({
            'error': 'Failed to fetch historical data'
        }), 400
    
    # Calculate average price over the period
    avg_price = df['close'].mean()
    current_price = df['close'].iloc[-1]
    
    # Calculate estimated holdings
    estimated_coins = total_investment / avg_price
    current_value = estimated_coins * current_price
    
    return jsonify({
        'total_investment': total_investment,
        'estimated_coins': estimated_coins,
        'current_value': current_value,
        'avg_price': avg_price,
        'current_price': current_price,
        'profit_loss': current_value - total_investment,
        'profit_loss_percentage': ((current_value - total_investment) / total_investment) * 100
    })

if __name__ == '__main__':
    # Start background analysis thread
    analysis_thread = threading.Thread(target=background_analysis, daemon=True)
    analysis_thread.start()
    
    # Force initial update
    update_analysis()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=10000, debug=True)
