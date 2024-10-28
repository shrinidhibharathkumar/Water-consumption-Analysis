from threading import Thread, Event
from websocket_server import WebsocketServer
import json
import serial
import time
from pymongo import MongoClient
from datetime import datetime

# Setup serial connection (adjust the port as necessary for your setup)
ser = serial.Serial('COM3', 9600, timeout=3)  # Adjust for your OS: 'COM3' for Windows, '/dev/ttyUSB0' for Linux
time.sleep(2)  # Wait for Arduino to reset

# Setup MongoDB connection
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI
db = client['sensor_data']  # Replace 'sensor_data' with your database name
collection = db['readings']

# Variables to manage client connections and threads
clients_connected = False
stop_event = Event()

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
        "ElectricityUsage": data.get("ElectricityUsage"),
        "Power": data.get("Power"),
        "PumpRunningStatus": data.get("PumpRunningStatus"),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    server.send_message_to_all(json.dumps(message))

# Function to read and process data from serial
def read_from_serial(server):
    while not stop_event.is_set():
        if ser.in_waiting > 0:
            try:
                serial_data = ser.readline().decode('utf-8').rstrip()
                data = json.loads(serial_data)
                print(data)
                if is_valid_data(data):
                    save_to_database(data)
                    if clients_connected:
                        send_data_to_clients(server, data)
            except json.JSONDecodeError:
                print("Error decoding JSON data")
            except Exception as e:
                print(f"Unexpected error in read_from_serial: {e}")

# Validate the incoming data structure
def is_valid_data(data):
    return (data.get("HomeID", -1) >= 0 and
            data.get("CurrentWaterLevel", -1) >= 0 and
            data.get("ElectricityUsage", -1) >= 0 and
            data.get("Power", -1) >= 0 and
            isinstance(data.get("PumpRunningStatus"), bool))

# Function to save data to MongoDB
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
