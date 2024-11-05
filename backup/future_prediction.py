import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import StackingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Sample data preparation (assuming df_optimized has historical data)
# Features include 'Day', 'ElectricityUsage(kWh)', and 'PumpedWater(L)'
df=[]

# Converting 'Day' to ordinal values for easier modeling
df['Day'] = pd.to_datetime(df['Day']).map(lambda date: date.toordinal())

# Feature columns
features = ['Day', 'ElectricityUsage(kWh)']
target = 'PumpedWater(L)'

# Train-test split
X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Stacking model setup
base_models = [
    ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
    ('rf', RandomForestRegressor(n_estimators=100, random_state=42))
]
meta_model = Ridge()

stacking_model = StackingRegressor(estimators=base_models, final_estimator=meta_model)

# Training the model
stacking_model.fit(X_train, y_train)

# Predicting on the test set
y_pred = stacking_model.predict(X_test)

# Evaluating the model
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print(f"Root Mean Squared Error (RMSE): {rmse}")

# Future prediction
# Assuming you want to predict for the next 7 days
future_days = pd.date_range(start="2024-08-08", end="2024-08-14", freq="D")
future_data = pd.DataFrame({
    'Day': future_days.map(lambda date: date.toordinal()),
    'ElectricityUsage(kWh)': np.random.uniform(10, 50, len(future_days))  # Replace with more accurate estimates if available
})

# Predict future water usage
future_predictions = stacking_model.predict(future_data)
future_data['PredictedWaterUsage(L)'] = future_predictions

# Display predictions
print(future_data)

# Visualization of future predictions
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(future_days, future_predictions, marker='o', color='blue', label='Predicted Water Usage')
plt.title('Predicted Water Usage for Next 7 Days')
plt.xlabel('Date')
plt.ylabel('Water Usage (L)')
plt.legend()
plt.show()
