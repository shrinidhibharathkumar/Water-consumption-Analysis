import serial
import json
import time
from pymongo import MongoClient
from datetime import datetime  # To add a timestamp

# Setup serial connection (change port name accordingly)
ser = serial.Serial('COM3', 9600, timeout=1)  # For Windows, use 'COMx' port, for Linux use '/dev/ttyUSBx'
time.sleep(2)  # Wait for Arduino to reset

# Setup MongoDB connection
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI
db = client['sensor_data']  # Replace 'sensor_data' with your database name
collection = db['readings']  # Replace 'readings' with your collection name

def read_from_serial():
    if ser.in_waiting > 0:
        serial_data = ser.readline().decode('utf-8').rstrip()
        try:
            data = json.loads(serial_data)
            return data
        except json.JSONDecodeError:
            print("Error decoding JSON data")
            return None

def is_valid_data(data):
    # Check if all values are greater than or equal to 0
    return (data.get("HomeID", -1) >= 0 and
            data.get("CurrentWaterLevel", -1) >= 0 and
            data.get("ElectricityUsage", -1) >= 0 and
            data.get("Power", -1) >= 0 and
            isinstance(data.get("PumpRunningStatus"), bool))  # Ensure PumpRunningStatus is a boolean

def save_to_database(data):
    try:
        # Add a timestamp field to the data
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert the data into MongoDB
        result = collection.insert_one(data)
        print(f"Data inserted with id: {result.inserted_id}")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

while True:
    data = read_from_serial()
    if data and is_valid_data(data):
        save_to_database(data)
    time.sleep(1)
