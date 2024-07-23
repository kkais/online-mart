from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request
from app.configs.settings import BASE_URL, STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY
from app.utils.auth import get_current_user
from app.utils.cart import get_current_user_cart, get_current_user_cart_with_product_name, get_inventory_by_product_id
import stripe
import json
import logging


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

stripe.api_key = STRIPE_SECRET_KEY

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Stripe Payment Service is starting...")
    # create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, title="Stripe Payment Service",
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8060", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Stripe Payment Server"
        }
    ])


@app.get("/checkout")
async def get_checkout_session_url(request: Request):
    line_items = []

    user = await get_current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # logger.info(f"\n\nUser:\n\n {user}")
    user_id = user.get("id")
    # logger.info(f"\n\nuser_id:\n\n {user_id}")

    current_user_cart = await get_current_user_cart(user_id)
    # logger.info(f"\n\nCurrent User Cart: \n\n {current_user_cart}")
    if not current_user_cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    current_user_cart_with_product_name = await get_current_user_cart_with_product_name(current_user_cart)
    # logger.info(f"\n\nCurrent User Cart with Product Name:\n\n {current_user_cart_with_product_name}")

    for item in current_user_cart_with_product_name:
        # logger.info(f"\n\nItem:\n\n {item}")
        if int(item.get("product_unit_price")) != int(item.get("unit_price")): 
            raise HTTPException(status_code=400, detail="Price mismatch")
        unit_price = int(item.get("product_unit_price"))

        inventory_by_product_id = await get_inventory_by_product_id(item.get("product_id"))
        # logger.info(f"\n\nGet Inventory By Product Id:\n\n {inventory_by_product_id}")

        if not inventory_by_product_id:
            raise HTTPException(status_code=404, detail="Inventory not found")

        if inventory_by_product_id.get("total_qty") < item.get("qty"):
            raise HTTPException(status_code=400, detail="Insufficient inventory")

        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item.get("product_name"),
                },
                "unit_amount": unit_price,
            },
            "quantity": item.get("qty"),
        })

    checkout_session = stripe.checkout.Session.create(
        line_items=line_items,
        allow_promotion_codes=False,
        invoice_creation=stripe.checkout.Session.CreateParamsInvoiceCreation(
            enabled=True
        ),
        metadata={
            "user_id": str(user_id),
            "email": user.get("email"),
        },
        mode="payment",
        success_url="<http://localhost:8060/success>",
        cancel_url="<http://localhost:8060/cancel>",
        customer_email="kkais786@gmail.com",
    )
    return {
        "url": checkout_session.url
    }

@app.get("/")
async def root():
    return {"Hello": "stripe payment world"}

@app.get("/success")
async def success():
    return {"Stripe": "Successful payment"}

@app.get("/cancel")
async def cancel():
    return {"Stripe": "Cancelled payment"}

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        print("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event["type"] == "checkout.session.completed":
        print("Checkout session completed")
        _object = event.get("data", {}).get("object", {})
        user_id = int(_object.get("metadata", {}).get("user_id"))
        amount_subtotal = _object.get("amount_subtotal", 0) / 100
        amount_total = _object.get("amount_total", 0) / 100
        quantity = _object.get("metadata", {}).get("quantity"),
        currency = _object.get("currency"),
        email = _object.get("customer_details", {}).get("email"),
        name = _object.get("customer_details", {}).get("name"),
        phone = _object.get("customer_details", {}).get("phone"),
        invoice_id = _object.get("invoice", None),
        city = _object.get("customer_details", {}).get("city", None),
        country = _object.get("customer_details", {}).get("country", None),
        line1 = _object.get("customer_details", {}).get("line1", None),
        line2 = _object.get("customer_details", {}).get("line2", None),
        postal_code = _object.get("customer_details", {}).get("postal_code", None),
        state = _object.get("customer_details", {}).get("state", None),
    elif event["type"] == "checkout.session.cancelled":
        print("Checkout session cancelled")
    elif event["type"] == "checkout.session.accepted":
        print("Checkout session accepted")
    elif event["type"] == "checkout.session.pending":
        print("Checkout session pending")
    return {}
    