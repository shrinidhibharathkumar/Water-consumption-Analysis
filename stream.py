from threading import Thread, Event
import random
from websocket_server import WebsocketServer
import json
import serial
import time
from pymongo import MongoClient
from datetime import datetime

# Setup serial connection (change port name accordingly)
ser = serial.Serial('COM3', 9600, timeout=1)  # For Windows, use 'COMx' port, for Linux use '/dev/ttyUSBx'
time.sleep(2)  # Wait for Arduino to reset

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
    # Check if any clients are still connected
    if len(server.clients) == 0:
        clients_connected = False

# Function to send data to connected WebSocket clients
def send_data_to_clients(server, data):
    # Create a message object with frame and unique counts
    message = {
        "HomeID": data.get("HomeID"),
        "CurrentWaterLevel": data.get("CurrentWaterLevel"),
        # "ElectricityUsage": data.get("ElectricityUsage"),
        "Power": data.get("Power"),
        "PumpRunningStatus": data.get("PumpRunningStatus"),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    # Send the message to all connected clients
    server.send_message_to_all(json.dumps(message))



# Function to read and process data from serial
def read_from_serial(server):
    while not stop_event.is_set():  # Continue reading until stop_event is set
        if ser.in_waiting > 0:
            serial_data = ser.readline().decode('utf-8').rstrip()
            try:
                data = json.loads(serial_data)
                if is_valid_data(data):
                    save_to_database(data)
                    if clients_connected:
                        send_data_to_clients(server, data)
            except json.JSONDecodeError:
                print("Error decoding JSON data")
            except Exception as e:
                print(f"Unexpected error: {e}")

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
    # Create a WebSocket server on port 3001
    server = WebsocketServer(host="127.0.0.1", port=3002)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)

    # Start the WebSocket server in a separate thread
    print("Starting WebSocket server on port 3002...")
    server_thread = Thread(target=server.run_forever)
    server_thread.start()

    # Start reading data from serial in a separate thread
    serial_thread = Thread(target=read_from_serial, args=(server,))
    serial_thread.start()

    try:
        # Wait for threads to complete
        server_thread.join()
        serial_thread.join()
    except KeyboardInterrupt:
        print("Stopping the server...")
        stop_event.set()  # Signal threads to stop
        ser.close()  # Close the serial port
        client.close()  # Close MongoDB connection
        print("Server stopped.")
