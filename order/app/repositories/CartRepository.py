import json
from datetime import datetime
from app.utils.cart import get_inventory_by_product_id
from sqlmodel import Session, select
from fastapi import HTTPException
from app.Models.Cart import  Cart
from app.utils.auth import get_current_user
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

class CartRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_cart(self, request):
        user = await get_current_user(request)
        if user is None:
            return []  
        user_id = user.get("id")
        return await self.get_cart_by_user(user_id)
    
    async def get_cart_by_user(self, user_id: int):
        return self.session.exec(
            select(Cart)
            .where(Cart.user_id == user_id)
            ).all()

    async def create_cart(self, cart: Cart, request):
        user = await get_current_user(request)
        user_id = user.get("id")
        cart.user_id = user_id

        existing_cart_item = self.session.exec(
            select(Cart)
            .where(Cart.user_id == user_id)
            .where(Cart.product_id == cart.product_id)
        ).first()

        inventory_by_product_id = await get_inventory_by_product_id(cart.product_id)
        # logger.info(f"\n\nGet Inventory By Product Id:\n\n {inventory_by_product_id}")

        if not inventory_by_product_id:
            raise HTTPException(status_code=404, detail="Inventory not found")

        if existing_cart_item:
            if int(inventory_by_product_id.get("total_qty")) < int(existing_cart_item.qty + cart.qty):
                raise HTTPException(status_code=400, detail="Insufficient inventory")
            
            existing_cart_item.qty = int(existing_cart_item.qty) + int(cart.qty)
            self.session.add(existing_cart_item)
            self.session.commit()
            self.session.refresh(existing_cart_item)
            return existing_cart_item
        
        else:
            if int(inventory_by_product_id.get("total_qty")) < int(cart.qty):
                raise HTTPException(status_code=400, detail="Insufficient inventory")
            
            self.session.add(cart)
            self.session.commit()
            self.session.refresh(cart)
            return cart
    
    # async def update_cart(self, product_id: int, cartUpdate: CartUpdate, request, action: str):
    async def update_cart(self, product_id: int, request, action: str):
        user = await get_current_user(request)
        if user is None:
            return []  
        user_id = user.get("id")

        cart = self.session.exec(
            select(Cart)
            .where(Cart.user_id == user_id)
            .where(Cart.product_id == product_id)
            ).first()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        if action == "add":
            inventory_by_product_id = await get_inventory_by_product_id(cart.product_id)
            # logger.info(f"\n\nGet Inventory By Product Id:\n\n {inventory_by_product_id}")

            if not inventory_by_product_id:
                raise HTTPException(status_code=404, detail="Inventory not found")
            
            if int(inventory_by_product_id.get("total_qty")) < int(cart.qty + 1):
                raise HTTPException(status_code=400, detail="Insufficient inventory")

            cart.qty = cart.qty + 1

        elif action == "remove":
            cart.qty = cart.qty - 1

        cart.updated_at = datetime.now(tz=None)
        self.session.add(cart)
        self.session.commit()
        self.session.refresh(cart)
        return cart

    async def delete_cart(self, product_id: int, request):
        user = await get_current_user(request)
        if user is None:
            return []  
        user_id = user.get("id")
        try:
            cart = self.session.exec(
                select(Cart)
                .where(Cart.user_id == user_id)
                .where(Cart.product_id == product_id)
                ).one()
            self.session.delete(cart)
            self.session.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False
        

    async def delete_cart_all(self, request):
        user = await get_current_user(request)
        if user is None:
            return []  
        user_id = user.get("id")
        carts = self.session.exec(
            select(Cart)
            .where(Cart.user_id == user_id)
            ).all()
        logger.info("Carts: ", carts)
        if not carts:
            return False
        for cart in carts:
            self.session.delete(cart)
            self.session.commit()
        return True
