from flask import Flask, render_template, request
import pickle
import numpy as np
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

class FraudModel:
    def __init__(self):
        self.threshold = 0.5

    def predict(self, X):
        predictions = []
        for transaction in X:
            # Unpack transaction features
            trans_type = transaction[0]
            amount = float(transaction[1])
            old_balance = float(transaction[2])
            new_balance = float(transaction[3])
            
            # Enhanced fraud detection rules
            risk_score = 0
            
            # Rule 1: Complete or near-complete account drainage (highest risk)
            if old_balance > 0 and (old_balance - amount) / old_balance <= 0.1:
                risk_score += 0.7
            
            # Rule 2: Transaction amount anomaly
            if amount > 10000:  # Large transaction threshold
                risk_score += 0.3
            
            # Rule 3: Suspicious balance changes
            if abs(old_balance - new_balance) > amount:
                risk_score += 0.5
                
            # Rule 4: Transaction type specific rules
            if trans_type == "CASH_OUT":
                if amount > 0.8 * old_balance:  # Large cash withdrawal
                    risk_score += 0.4
            elif trans_type == "TRANSFER":
                if new_balance <= 10:  # Transfer leaving account nearly empty
                    risk_score += 0.6
                    
            # Rule 5: Balance consistency check
            expected_new_balance = old_balance - amount
            if abs(expected_new_balance - new_balance) > 1:  # Allow for minor rounding
                risk_score += 0.3
                
            # Normalize risk score to 0-1 range and compare to threshold
            risk_score = min(1.0, risk_score)
            predictions.append(1 if risk_score >= self.threshold else 0)
            
        return predictions

# Initialize model
model = FraudModel()

@app.route('/')
def home():
    return render_template('index.html', prediction=None)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        trans_type = request.form['type']
        amount = float(request.form['amount'])
        old_balance = float(request.form['oldbalanceOrg'])
        new_balance = float(request.form['newbalanceOrig'])

        # Input validation
        if amount <= 0:
            raise ValueError("Transaction amount must be positive")
        if old_balance < 0 or new_balance < 0:
            raise ValueError("Balance cannot be negative")
        if old_balance < amount:
            raise ValueError("Insufficient balance for this transaction")

        # Prepare features
        input_features = [
            trans_type,
            amount,
            old_balance,
            new_balance
        ]

        # Make prediction
        prediction = model.predict([input_features])[0]

        # Prepare response
        if prediction == 1:
            return render_template('index.html',
                                prediction="🚨 High Risk Transaction Detected",
                                is_fraud=True)
        else:
            return render_template('index.html',
                                prediction="✅ Transaction Appears Safe",
                                is_fraud=False)

    except ValueError as e:
        return render_template('index.html',
                             prediction=f"❌ Validation Error: {str(e)}",
                             is_error=True)
    except Exception as e:
        return render_template('index.html',
                             prediction="❌ An unexpected error occurred",
                             is_error=True)

if __name__ == '__main__':
    app.run(debug=True)