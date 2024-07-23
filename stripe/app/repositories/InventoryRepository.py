import json
from sqlmodel import Session, select, func
from app.Models.Inventory import Inventory, InventoryBalance
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

class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_inventory(self):
        return self.session.exec(select(Inventory)).all()
    
    async def get_inventory_by_product_id(self, product_id: int):
        return self.session.exec(select(Inventory.product_id, func.sum(Inventory.qty).label("total_qty")) 
                                 .where(Inventory.product_id == product_id)
                                 .group_by(Inventory.product_id)
                                 ).first()

    async def create_inventory(self, inventory: Inventory):
        self.session.add(inventory)
        self.session.commit()
        self.session.refresh(inventory)
        return Inventory.model_validate(inventory)