import asyncio
import websockets
import json
from collections import deque
from queue import Queue
import time
import os
import threading

# https://docs.deribit.com/next/?python#deribit-api-v2-1-1

# Order queue and lock
requestQueue = deque()
requestQueue_lock = threading.Lock()
last_file_size = 0

# gloabl msg_id tracker
msg_id = 0

# Authentication message
auth_msg = {
    "jsonrpc": "2.0",
    "id": 0,
    "method": "public/auth",
    "params": {
        "grant_type": "client_credentials",
        "client_id": "9YgyTMFg",
        "client_secret": "9xYau6uFd8PWR6iHvQNCNM4mFWl2Pr84wu20lS6NePc"
    }
}

async def call_api(auth_msg, requestQueue):

    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
        # Send authentication message
        await websocket.send(json.dumps(auth_msg))
        
        # Wait for authentication response
        while websocket.open:
            response = await websocket.recv()
            response_data = json.loads(response)
            print(response_data)  # Print the authentication response

            # Check if authentication was successful
            if 'result' in response_data and response_data['result']['access_token']:
                print("Authentication successful!")
                
                # Start the request queue processing.
                asyncio.create_task(processRequestQueue(websocket, requestQueue))

                # Keep the websocket connection open to receive more messages
                while websocket.open:
                    response = await websocket.recv()
                    print(response)  # Print other responses if needed
            elif 'error' in response_data:
                print(f"Authentication failed: {response_data['error']}")
                break

async def processRequestQueue(websocket, requestQueue):
    while True:
        with requestQueue_lock:  # Lock the queue for thread safety
            if requestQueue:
                order_msg = requestQueue.popleft()  # Get the next order
                await websocket.send(json.dumps(order_msg))  # Send the order message
                print(f"Request pushed in requestQueue: {order_msg}")

        await asyncio.sleep(1)  # Slight delay to prevent busy-waiting

# Function to add orders to the queue
def enqueueBuySellMarketOrder(instrument_name, buySell, amount, order_type, label):
    if not (buySell != "buy" or buySell != "sell"):
        return
    if not order_type == "market":
        return
    order_msg = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "private/" + buySell,
        "params": {
            "instrument_name": instrument_name,
            "amount": amount,
            "type": order_type,
            "label": label
        }
    }
    with requestQueue_lock:  # Lock the queue for thread safety
        requestQueue.append(order_msg)

def enqueueBuySellLimitOrder(instrument_name, buySell, amount, price, order_type, label):
    if not (buySell != "buy" or buySell != "sell"):
        return
    if not order_type == "limit":
        return
    order_msg = {
        "jsonrpc": "2.0",
        "id": msg_id, 
        "method": "private/" + buySell,
        "params": {
            "instrument_name": instrument_name,
            "amount": amount,
            "price": price,
            "type": order_type,
            "label": label
        }
    }
    with requestQueue_lock:  # Lock the queue for thread safety
        requestQueue.append(order_msg)

def enqueueCancelOrder(order_id):
    cancel_msg = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "private/cancel",
        "params": {
            "order_id": order_id
        }
    }
    with requestQueue_lock:  # Lock the queue for thread safety
        requestQueue.append(cancel_msg)

def enqueueModifyOrder(order_id, price, amount):
    modify_msg = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "private/edit",
        "params": {
            "order_id": order_id,
            "amount": amount,
            "price": price,
        }
    }
    with requestQueue_lock:  # Lock the queue for thread safety
        requestQueue.append(modify_msg)

def enqueueGetOpenOrderBook():
    openOrderBook_msg = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "private/get_open_orders",
        "params": {
        }
    }
    with requestQueue_lock:  # Lock the queue for thread safety
        requestQueue.append(openOrderBook_msg)

def enqueueGetCurrentPositions():
    openPositions_msg = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "private/get_positions",
        "params": {
        }
    }
    with requestQueue_lock:  # Lock the queue for thread safety
        requestQueue.append(openPositions_msg)

def file_monitor_thread(file_path):
    global last_file_size,msg_id
    while True:
        # Check if the file exists
        if os.path.isfile(file_path):
            current_file_size = os.path.getsize(file_path)

            # Read new content if the file has grown
            if current_file_size > last_file_size:
                with open(file_path, 'r') as file:
                    file.seek(last_file_size)  # Move to the end of the last read
                    lines = file.read().strip().splitlines()
                    
                    for line in lines:
                        # Parse each line as a comma-separated string
                        if line:
                            parts = line.split(',')
                            type = parts[0].strip()
                            if type == 'N':
                                if len(parts) == 6:  # Assuming the line format: instrument_name, amount, order_type, label
                                    type, buySell, instrument_name, amount, order_type, label = parts
                                    msg_id = msg_id+1
                                    enqueueBuySellMarketOrder(instrument_name.strip(), buySell.strip(), int(amount.strip()), order_type.strip(), label.strip())
                                elif len(parts) == 7:
                                    type, buySell, instrument_name, amount, price, order_type, label = parts
                                    msg_id = msg_id+1
                                    enqueueBuySellLimitOrder(instrument_name.strip(), buySell.strip(), int(amount.strip()), int(price.strip()), order_type.strip(), label.strip())
                            elif type == 'X':                           
                                if len(parts) == 2:
                                    type, order_id = parts
                                    msg_id = msg_id+1
                                    enqueueCancelOrder(order_id.strip())
                            elif type == 'M':
                                if len(parts) == 4:
                                    type, order_id, amount, price = parts
                                    msg_id = msg_id+1
                                    enqueueModifyOrder(order_id.strip(), int(amount.strip()), int(price.strip()))
                            elif type == 'O':
                                if len(parts) == 1:
                                    msg_id = msg_id+1
                                    enqueueGetOpenOrderBook()
                            elif type == 'P':
                                if len(parts) == 1:
                                    msg_id = msg_id+1
                                    enqueueGetCurrentPositions()
            
            last_file_size = current_file_size  # Update the last file size

        time.sleep(1)  # Wait a bit before checking again

# Start the file monitoring thread
threading.Thread(target=file_monitor_thread, args=('requests.txt',), daemon=True).start()

# Run the async function for the WebSocket connection
asyncio.run(call_api(auth_msg, requestQueue))