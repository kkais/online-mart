import json
from typing import Annotated
from sqlmodel import Session, select
# from sqlmodel.ext.asyncio.session import AsyncSession
from app.Models import Product_pb2
from app.Models.Product import Product
from aiokafka import AIOKafkaProducer
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


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_products(self):
        return self.session.exec(select(Product)).all()

    async def get_product_by_id(self, product_id: int):
        return self.session.get(Product, product_id)

    async def create_product(self, product: Product, producer: AIOKafkaProducer):
        # product_protbuf = Product_pb2.Product(id=product.id, name=product.name, price=product.price)
        # print(f"Product Created Protobuf: {product_protbuf}")
        # # Serialize the message to a byte string
        # serialized_product = product_protbuf.SerializeToString()
        # print(f"Serialized data: {serialized_product}")

        prouct_dict = {field: getattr(product, field) for field in product.dict()}
        serialized_product = self.serialize_product(prouct_dict)
        # serialized_product["user_id"] = user_id
        

        # Produce message
        await producer.send_and_wait("products_create", serialized_product)
        return product

    async def update_product(self, product_id: int, 
                             updated_product: Product, 
                             user_id: int,
                             producer: AIOKafkaProducer):
        existing_product = self.session.get(Product, product_id)
        if not existing_product:
            return None
        
        logger.info(f"Existing Product: {existing_product}")
        logger.info(f"Updated Product: {updated_product}")

        # TODO: or user is admin and also allowed to update
        if user_id != existing_product.user_id:
            return None
        
        existing_product.name = updated_product.name
        existing_product.price = updated_product.price
        
        logger.info(f"Product Updated: {existing_product}")

        # product_protbuf = Product_pb2.Product(id=existing_product.id, name=existing_product.name, price=existing_product.price)
        # print(f"Product Update Protobuf: {product_protbuf}")
        # # Serialize the message to a byte string
        # serialized_product = product_protbuf.SerializeToString()
        # print(f"Serialized data: {serialized_product}")
        prouct_dict = {field: getattr(existing_product, field) for field in existing_product.dict()}
        logger.info(f"Product Dict: ==> {prouct_dict}")
        serialized_product = self.serialize_product(prouct_dict)

        # Produce message
        await producer.send_and_wait("products_full_update", serialized_product)
        return existing_product

    async def delete_product(self, product_id: int, user_id: int, producer: AIOKafkaProducer):
        product = self.session.get(Product, product_id)
        if not product:
            return None
        
        if user_id != product.user_id:
            return None

        product_dict = {field: getattr(product, field) for field in product.dict()}
        serialized_product = self.serialize_product(product_dict)
        # Produce message
        await producer.send_and_wait("products_delete", serialized_product)
        
        return json.dumps({"message": "Product deleted successfully"})

    def serialize_product(self, product_dict):
        # product_protbuf = Product_pb2.Product(**product_dict)

        product_protbuf = Product_pb2.Product()
        product_protbuf.id = product_dict["id"]
        product_protbuf.name = product_dict["name"]
        product_protbuf.price = product_dict["price"]
        product_protbuf.user_id = product_dict["user_id"]

        logger.info(f"Product Protobuf: {product_protbuf}")
        # Serialize the message to a byte string
        serialized_product = product_protbuf.SerializeToString()
        logger.info(f"Serialized data: {serialized_product}")
        return serialized_product