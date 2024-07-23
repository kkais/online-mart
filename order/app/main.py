from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlmodel import Session
from app.utils.session import get_session
from app.Models.Order import Order, OrderRead, OrderStatus, OrderUpdateSatus
from app.Models.Cart import Cart, CartRead, CartUpdate
from app.database.create_schema import create_db_and_tables
from app.repositories.OrderRepository import OrderRepository
from app.repositories.CartRepository import CartRepository
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

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, title="Order Service",
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8070", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Order Server"
        }
    ])

@app.get("/")
async def root():
    return {"Hello": "order world"}

@app.get("/orders", response_model=list[OrderRead])
async def get_orders(session: Annotated[Session, Depends(get_session)]):
    order_repository = OrderRepository(session)
    orders = await order_repository.get_orders()
    return orders

@app.post("/orders", response_model=OrderRead)
async def create_order(order: Order, request: Request, session: Annotated[Session, Depends(get_session)]):
    order_repository = OrderRepository(session)
    order = await order_repository.create_order(order, request)
    return OrderRead.model_validate(order)

@app.get("/orders/history", response_model=list[OrderRead])
async def get_order_history(request: Request, session: Annotated[Session, Depends(get_session)]):
    order_repository = OrderRepository(session)
    orders = await order_repository.get_order_history(request)
    return orders

@app.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, session: Annotated[Session, Depends(get_session)]):
    order_repository = OrderRepository(session)
    order = await order_repository.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@app.patch("/orders/{order_id}/status", response_model=OrderRead)
async def update_order_status(order_id: int, status: OrderUpdateSatus, session: Annotated[Session, Depends(get_session)]):
    logger.info(f"Order ID: {order_id}, Status: {status}")
    order_repository = OrderRepository(session)
    order = await order_repository.update_order_status(order_id, status)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderRead.model_validate(order)

@app.get("/cart/{user_id}", response_model=list[CartRead])
async def get_cart_by_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    cart_repository = CartRepository(session)
    cart = await cart_repository.get_cart_by_user(user_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart

@app.get("/cart", response_model=list[CartRead])
async def get_cart(request: Request, session: Annotated[Session, Depends(get_session)]):
    cart_repository = CartRepository(session)
    cart = await cart_repository.get_cart(request)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart

@app.post("/cart", response_model=CartRead)
async def create_cart(cart: Cart, request: Request, session: Annotated[Session, Depends(get_session)]):
    logger.info(f"Cart: {cart}")
    cart_repository = CartRepository(session)
    cart = await cart_repository.create_cart(cart=cart, request=request)
    # if not cart:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart

@app.patch("/cart/add/{product_id}", response_model=Cart)
async def update_cart(product_id: int, request: Request, session: Annotated[Session, Depends(get_session)]):
    cart_repository = CartRepository(session)
    return await cart_repository.update_cart(product_id, request, "add")

@app.patch("/cart/remove/{product_id}", response_model=Cart)
async def update_cart(product_id: int, request: Request, session: Annotated[Session, Depends(get_session)]):
    cart_repository = CartRepository(session)
    return await cart_repository.update_cart(product_id, request, "remove")

@app.delete("/cart/all")
async def delete_cart_all(request: Request, session: Annotated[Session, Depends(get_session)]):
    cart_repository = CartRepository(session)
    result = await cart_repository.delete_cart_all(request)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return {"message": "Cart deleted successfully"}

@app.delete("/cart/{product_id}")
async def delete_cart(product_id: int, request: Request, session: Annotated[Session, Depends(get_session)]):
    cart_repository = CartRepository(session)
    result = await cart_repository.delete_cart(product_id, request)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return {"message": "Cart item deleted successfully"}
