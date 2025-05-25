from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    
    principal = float(data['principal'])
    interest_rate = float(data['interest_rate']) / 100  # Convert percentage to decimal
    goal = float(data['goal'])
    frequency = int(data['frequency'])
    contribution = float(data['contribution'])
    
    # Calculate monthly breakdown
    monthly_details = []
    current_balance = principal
    monthly_rate = interest_rate / 12  # Monthly interest rate
    month = 1
    
    while current_balance < goal:
        # Calculate interest for this month
        interest_earned = current_balance * monthly_rate
        
        # Add monthly contribution
        if frequency == 12:  # Monthly
            contribution_this_month = contribution
        elif frequency == 52:  # Weekly
            contribution_this_month = contribution * 52/12
        elif frequency == 26:  # Bi-weekly
            contribution_this_month = contribution * 26/12
        elif frequency == 4:  # Quarterly
            contribution_this_month = contribution * 4/12 if month % 3 == 0 else 0
        else:  # Annually
            contribution_this_month = contribution if month % 12 == 0 else 0
            
        # Update balance
        current_balance += interest_earned + contribution_this_month
        
        # Add to monthly details
        monthly_details.append({
            'month': month,
            'starting_balance': round(current_balance - interest_earned - contribution_this_month, 2),
            'interest_earned': round(interest_earned, 2),
            'contribution': round(contribution_this_month, 2),
            'ending_balance': round(current_balance, 2)
        })
        
        month += 1
    
    years = (month - 1) / 12
    years = round(years, 2)
    
    return jsonify({
        'years': years,
        'monthly_details': monthly_details
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
