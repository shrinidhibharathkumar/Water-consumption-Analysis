from threading import Thread, Event
import random
import json
import time
from datetime import datetime
from websocket_server import WebsocketServer
from pymongo import MongoClient

# Setup MongoDB connection
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI
db = client['sensor_data']  # Replace 'sensor_data' with your database name
collection = db['readings']

clients_connected = False
stop_event = Event()  # Event to stop the threads gracefully

# WebSocket event handlers
def new_client(client, server):
    global clients_connected
    print("New client connected:", client)
    clients_connected = True

def client_left(client, server):
    global clients_connected
    print("Client disconnected:", client)
    if len(server.clients) == 0:
        clients_connected = False

# Function to send data to connected WebSocket clients
def send_data_to_clients(server, data):
    message = {
        "HomeID": data.get("HomeID"),
        "CurrentWaterLevel": data.get("CurrentWaterLevel"),
        "Power": data.get("Power"),
        "PumpRunningStatus": data.get("PumpRunningStatus"),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    server.send_message_to_all(json.dumps(message))

# Function to generate mock data
def mock_serial_data():
    return {
        "HomeID": random.randint(1, 2),  # Limited to 2 homes
        "CurrentWaterLevel": random.randint(0, 100),
        "ElectricityUsage": random.uniform(100.0, 500.0),
        "Power": random.uniform(0.0, 100.0),
        "PumpRunningStatus": random.choice([True, False])
    }

# Function to simulate data reading and processing
def read_from_mock_serial(server):
    while not stop_event.is_set():
        mock_data = mock_serial_data()
        try:
            if is_valid_data(mock_data):
                save_to_database(mock_data)
                if clients_connected:
                    send_data_to_clients(server, mock_data)
            time.sleep(1)  # Simulate a 1-second interval between readings
        except Exception as e:
            print(f"Unexpected error in data processing: {e}")

def is_valid_data(data):
    return (data.get("HomeID", -1) >= 0 and
            data.get("CurrentWaterLevel", -1) >= 0 and
            data.get("ElectricityUsage", -1) >= 0 and
            data.get("Power", -1) >= 0 and
            isinstance(data.get("PumpRunningStatus"), bool))

def save_to_database(data):
    try:
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = collection.insert_one(data)
        print(f"Data inserted with id: {result.inserted_id}")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

if __name__ == "__main__":
    # Create a WebSocket server on port 3002
    server = WebsocketServer(host="127.0.0.1", port=3002)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)

    # Start the WebSocket server in a separate thread
    print("Starting WebSocket server on port 3002...")
    server_thread = Thread(target=server.run_forever)
    server_thread.start()

    # Start reading data from mock serial in a separate thread
    serial_thread = Thread(target=read_from_mock_serial, args=(server,))
    serial_thread.start()

    try:
        # Wait for threads to complete
        server_thread.join()
        serial_thread.join()
    except KeyboardInterrupt:
        print("Stopping the server...")
        stop_event.set()  # Signal threads to stop
        client.close()  # Close MongoDB connection
        print("Server stopped.")
