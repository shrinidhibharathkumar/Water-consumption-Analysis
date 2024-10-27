import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Function to generate a training dataset for the water management model
def generate_training_data(start_date, num_days=60, num_houses=5):
    data = []
    current_time = start_date

    for day in range(num_days):
        for house_id in range(1, num_houses + 1):
            for hour in range(24):
                timestamp = current_time + timedelta(hours=hour)
                
                # Simulating realistic water levels and power consumption
                if hour < 12:  # Morning usage
                    water_level = np.clip(np.random.normal(40, 5), 20, 50)  # Mean 40, std dev 5
                else:  # Evening usage
                    water_level = np.clip(np.random.normal(30, 5), 20, 50)  # Mean 30, std dev 5

                # Power consumption in the range of 10 to 50
                power_consumption = np.random.randint(10, 51)  # Power consumption between 10W and 50W
                pump_status = np.random.choice([0, 1], p=[0.7, 0.3])  # 70% chance pump is off
                electricity_cost = round(np.random.uniform(8, 18), 2)  # Random cost per kWh in rupees
                predicted_water_usage = round(np.random.uniform(30, 40), 2)  # Predicted usage between 30% and 40%

                # Append data to the list
                data.append([timestamp, house_id, water_level, power_consumption, pump_status, electricity_cost, predicted_water_usage])

        # Move to the next day
        current_time += timedelta(days=1)

    # Create a DataFrame
    columns = ['timestamp', 'house_id', 'water_level (%)', 'power_consumption (W)', 'pump_status', 'electricity_cost (₹/kWh)', 'predicted_water_usage (%)']
    df = pd.DataFrame(data, columns=columns)

    return df

# Generate training dataset starting from a specified date
start_date = datetime(2024, 10, 1)
training_data = generate_training_data(start_date)

# Save the training dataset to a CSV file
training_data.to_csv('water_management_training_data_2_months_in_rupees.csv', index=False)
