from http.client import HTTPException
from fastapi import Request
import httpx
import logging

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Create a logger instance
logger = logging.getLogger(__name__)

async def get_current_user_cart(user_id: int):
    async with httpx.AsyncClient() as client:
        # url = f"http://user-service:8040/user/{token}"
        url = f"http://order-service:8070/cart/{user_id}"
        # url = f"http://order-service:3501/v1.0/invoke/order-service/method/cart/{user_id}"
        
        response = await client.get(url)
        logger.info(response)
        if response.status_code != 200:
            raise HTTPException(response.status_code, "Failed to fetch current user cart")
        user = response.json()
    return user

async def create_current_user_order(user_id: int):
    async with httpx.AsyncClient() as client:
        # url = f"http://user-service:8040/user/{token}"
        url = f"http://order-service:8070/order/{user_id}"
        # url = f"http://order-service:3501/v1.0/invoke/order-service/method/order/{user_id}"
        
        response = await client.post(url)
        logger.info(response)
        if response.status_code != 200:
            raise HTTPException(response.status_code, "Failed to create current user order")
        order = response.json()
    return order

async def get_current_user_cart_with_product_name(current_user_cart):
    async with httpx.AsyncClient() as client:
        for item in current_user_cart:
            url = f"http://pbproduct-service:8050/products/{item.get('product_id')}"
            response = await client.get(url)
            logger.info(response)
            if response.status_code != 200:
                raise HTTPException(response.status_code, "Failed to fetch current user cart with product name")
            item["product_name"] = response.json().get("name")
            item["product_unit_price"] = response.json().get("price")
    return current_user_cart

async def get_inventory_by_product_id(product_id: int):
    async with httpx.AsyncClient() as client:
        url = f"http://inventory-service:8020/inventory/{product_id}"
        response = await client.get(url)
        logger.info(response)
        if response.status_code != 200:
            raise HTTPException(response.status_code, "Failed to fetch inventory by product id")
        inventory = response.json()
    return inventory