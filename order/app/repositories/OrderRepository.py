import json
from sqlmodel import Session, select, func
from app.Models.Order import Order, OrderRead, OrderStatus, OrderItem, OrderUpdateSatus
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

class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_orders(self):
        return self.session.exec(select(Order).order_by(Order.id)).all()
        
    
    async def get_order_by_id(self, order_id: int):
        return self.session.exec(select(Order).where(Order.id == order_id)).first()

    async def update_order_status(self, order_id: int, orderUpdateSatus: OrderUpdateSatus):
        order = self.session.get(Order, order_id)
        order.status = orderUpdateSatus.status
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    async def create_order(self, order: Order, request):
        user = await get_current_user(request)
        user_id = user.get("id")
        order.user_id = user_id
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order
    
    async def get_order_history(self, request):
        user = await get_current_user(request)
        user_id = user.get("id")
        return self.session.exec(
            select(Order)
            # .where(Order.status == OrderStatus.COMPLETED)
            .where(Order.user_id == user_id)
            ).all()