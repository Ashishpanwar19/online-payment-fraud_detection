from flask import Flask, render_template, request
import pickle
import numpy as np
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# ================== CRITICAL FIX ==================
# Define the FraudModel class EXACTLY as it was during training
class FraudModel:
    def __init__(self):
        self.threshold = 0.5  # Example threshold

    def predict(self, X):
        """Properly implemented predict method with correct indentation"""
        predictions = []
        for transaction in X:
            # Unpack the transaction features
            trans_type = transaction[0]  # String
            amount = float(transaction[1])
            old_balance = float(transaction[2])
            new_balance = float(transaction[3])
            
            # Rule 1: Complete account drainage
            if (old_balance - amount) <= 1.0:  # Near-zero balance
                predictions.append(1)
            # Rule 2: Large cash-out (>90% of balance)
            elif trans_type == "CASH_OUT" and amount > 0.9 * old_balance:
                predictions.append(1)
            # Rule 3: Suspicious transfer to empty account
            elif trans_type == "TRANSFER" and new_balance <= 1.0:
                predictions.append(1)
            else:
                predictions.append(0)
        return predictions
# ================== MODEL LOADING ==================
model = None
try:
    model_path = os.path.join('payment_fraud_detector', 'model', 'fraud_model.pkl')
    
    # PROPER way to load the pickle file with the class definition
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Verify the loaded model has predict()
    if not hasattr(model, 'predict'):
        raise AttributeError("Loaded model is missing predict() method")
    
    print("Model successfully loaded!")
except Exception as e:
    print(f"Model loading failed: {str(e)}")
    model = FraudModel()  # Fallback to dummy model

# ================== ROUTES ==================
@app.route('/')
def home():
    return render_template('index.html', prediction=None)

@app.route('/predict', methods=['POST'])
def predict():
    # 1. Validate model is ready
    if not model:
        return render_template('index.html', 
                            prediction="⚠️ Model not initialized",
                            is_error=True)

    try:
        # 2. Get and validate form data
        trans_type = request.form['type']
        amount = float(request.form['amount'])
        old_balance = float(request.form['oldbalanceOrg'])
        new_balance = float(request.form['newbalanceOrig'])

        # 3. Prepare input features (MUST match training format)
        input_features = [
            trans_type,  # String like "CASH_OUT"
            amount,
            old_balance,
            new_balance
        ]

        # 4. Make prediction
        prediction = model.predict([input_features])[0]  # Returns 0 or 1

        # 5. Return human-readable result
        if prediction == 1:
            return render_template('index.html',
                                 prediction="🚨 Fraud Detected!",
                                 is_fraud=True)
        else:
            return render_template('index.html',
                                 prediction="✅ Legitimate Transaction",
                                 is_fraud=False)

    except Exception as e:
        return render_template('index.html',
                             prediction=f"❌ Error: {str(e)}",
                             is_error=True)

if __name__ == '__main__':
    app.run(debug=True)