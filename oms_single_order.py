import asyncio
import websockets
import json

# Authentication message
auth_msg = {
    "jsonrpc": "2.0",
    "id": 9929,
    "method": "public/auth",
    "params": {
        "grant_type": "client_credentials",
        "client_id": "9YgyTMFg",
        "client_secret": "9xYau6uFd8PWR6iHvQNCNM4mFWl2Pr84wu20lS6NePc"
    }
}

# Order message
order_msg = {
    "jsonrpc": "2.0",
    "id": 5275,
    "method": "private/buy",
    "params": {
        "instrument_name": "ETH-PERPETUAL",
        "amount": 40,
        "type": "market",
        "label": "market0000234"
    }
}

async def call_api(auth_msg, order_msg):
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

                # Now send the order message
                await websocket.send(json.dumps(order_msg))
                print("Order placed.")

                # Wait for the order response
                while websocket.open:
                    response = await websocket.recv()
                    print(response)  # Print order response
            elif 'error' in response_data:
                print(f"Authentication failed: {response_data['error']}")
                break

# Run the async function
asyncio.get_event_loop().run_until_complete(call_api(auth_msg, order_msg))
