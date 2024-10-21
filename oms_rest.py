import requests
import json
import time
import websocket
import threading
import auth

# Constants
BASE_URL = 'https://test.deribit.com/api/v2'
CLIENT_ID = '9YgyTMFg'
CLIENT_SECRET = '9xYau6uFd8PWR6iHvQNCNM4mFWl2Pr84wu20lS6NePc'

# Boilerplate class for managing orders
class DeribitOrderManager:
    def __init__(self):
        self.token = auth.get_auth_token()
        self.headers = {'Authorization': f'Bearer {self.token}'}

    # Function to place an order
    def place_order(self, instrument_name, amount, price, side='buy'):
        endpoint = f'{BASE_URL}/private/{side}'
        data = {
            'instrument_name': instrument_name,
            'amount': amount,
            'type': 'limit',  # Can be 'limit' or 'market'
            'price': price
        }
        response = requests.post(endpoint, json=data, headers=self.headers)
        return response.json()

    # Function to cancel an order
    def cancel_order(self, order_id):
        endpoint = f'{BASE_URL}/private/cancel'
        data = {'order_id': order_id}
        response = requests.post(endpoint, json=data, headers=self.headers)
        return response.json()

    # Function to modify an order
    def modify_order(self, order_id, new_amount, new_price):
        endpoint = f'{BASE_URL}/private/edit'
        data = {
            'order_id': order_id,
            'amount': new_amount,
            'price': new_price
        }
        response = requests.post(endpoint, json=data, headers=self.headers)
        return response.json()

    # Function to get the orderbook for an instrument
    def get_orderbook(self, instrument_name, depth=5):
        endpoint = f'{BASE_URL}/public/get_order_book'
        params = {'instrument_name': instrument_name, 'depth': depth}
        response = requests.get(endpoint, params=params)
        return response.json()

    # Function to view current positions
    def get_positions(self, currency='BTC'):
        endpoint = f'{BASE_URL}/private/get_positions'
        params = {'currency': currency}
        response = requests.get(endpoint, params=params, headers=self.headers)
        return response.json()

# Example usage
if __name__ == '__main__':
    manager = DeribitOrderManager()

    # Place an order
    print("Placing order...")
    order_response = manager.place_order(instrument_name='BTC-PERPETUAL', amount=10, price=30000, side='buy')
    print(json.dumps(order_response, indent=4))

    exit(1)
    # Cancel an order
    print("Canceling order...")
    cancel_response = manager.cancel_order(order_id=order_response['result']['order']['order_id'])
    print(json.dumps(cancel_response, indent=4))

    # Modify an order
    print("Modifying order...")
    modify_response = manager.modify_order(order_id=order_response['result']['order']['order_id'], new_amount=20, new_price=29000)
    print(json.dumps(modify_response, indent=4))

    # Fetch orderbook
    print("Fetching orderbook...")
    orderbook_response = manager.get_orderbook(instrument_name='BTC-PERPETUAL', depth=5)
    print(json.dumps(orderbook_response, indent=4))

    # View positions
    print("Viewing positions...")
    positions_response = manager.get_positions(currency='BTC')
    print(json.dumps(positions_response, indent=4))