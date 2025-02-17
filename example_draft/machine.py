import time
import logging
import requests

API_URL = 'http://localhost:8000'
ORDER_STATE_PENDING = "PENDING"
ORDER_STATE_IN_PROGRESS = "IN_PROGRESS"
ORDER_STATE_COMPLETED = "COMPLETED"
PRODUCT_STATE_ORDERED = "ORDERED"
PRODUCT_STATE_READY = "READY"
DELAY_PER_PRODUCT = 3  # Seconds per product processing

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_pending_orders():
    response = requests.get(f"{API_URL}/orders")
    if response.status_code == 200:
        orders = response.json()
        pending_orders = [o for o in orders if o['state'] == ORDER_STATE_PENDING]
        return sorted(pending_orders, key=lambda x: x['timestamp'])  # Oldest first
    logging.warning("Failed to retrieve orders")
    return []


def set_order_status(order_id, status):
    response = requests.put(f"{API_URL}/orders/{order_id}?state={status}")
    if response.status_code == 200:
        logging.info(f"Order {order_id} status updated to {status}")
    else:
        logging.error(f"Failed to update order {order_id} to {status}")


def get_order_products(order_id):
    response = requests.get(f"{API_URL}/orders/{order_id}/products")
    if response.status_code == 200:
        return response.json()
    logging.warning(f"Failed to retrieve products for order {order_id}")
    return []


def set_product_status(product_id, status):
    response = requests.put(f"{API_URL}/products/{product_id}?state={status}")
    if response.status_code == 200:
        logging.info(f"Product {product_id} status updated to {status}")
    else:
        logging.error(f"Failed to update product {product_id} to {status}")


def process_orders():
    while True:
        orders = get_pending_orders()
        if not orders:
            logging.info("No pending orders. Waiting...")
            time.sleep(5)
            continue

        order = orders[0]
        order_id = order['id']
        logging.info(f"Processing order {order_id}")
        set_order_status(order_id, ORDER_STATE_IN_PROGRESS)

        products = get_order_products(order_id)
        ordered_products = [p for p in products if p['state'] == PRODUCT_STATE_ORDERED]

        for product in ordered_products:
            time.sleep(DELAY_PER_PRODUCT)
            set_product_status(product['id'], PRODUCT_STATE_READY)

        logging.info(f"All products in order {order_id} are ready")
        set_order_status(order_id, ORDER_STATE_COMPLETED)

        logging.info(f"Order {order_id} completed. Checking next order...")


if __name__ == "__main__":
    process_orders()
