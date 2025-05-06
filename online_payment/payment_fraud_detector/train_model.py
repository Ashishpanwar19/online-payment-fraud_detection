import pickle
import os

# Ensure model directory exists
os.makedirs('model', exist_ok=True)

# Dummy model: if amount > 10000 => fraud, else not fraud
class FraudModel:
    def predict(self, X):
        predictions = []
        for x in X:
            amount = x[1]  # assuming the second column is 'amount'
            if amount > 10000:
                predictions.append(1)  # 1 means fraud
            else:
                predictions.append(0)  # 0 means not fraud
        return predictions

# Save the dummy model
model = FraudModel()
with open('model/fraud_model.pkl','wb') as f:
    pickle.dump(model, f)

print("✅ Dummy fraud model saved to model/fraud_model.pkl")
