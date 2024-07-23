# main.py
from contextlib import asynccontextmanager
from http.client import HTTPException
from typing import Annotated
from app.utils.auth import get_current_user
from sqlmodel import Session
from fastapi import FastAPI, Depends, status, Request
# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import JSONResponse
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
import asyncio
import json
from app.database.create_schema import create_db_and_tables
from app.Models import Product_pb2
from app.Models.Product import Product
from app.kafka.consumers.consumer import consume_messages
from app.kafka.producers.producer import get_kafka_producer
from app.repositories.ProductRepository import ProductRepository
from app.utils.session import get_session

# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
# loop = asyncio.get_event_loop()
@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    # loop.run_until_complete(consume_messages('todos', 'broker:19092'))
    task = asyncio.create_task(consume_messages(["products_create", "products_full_update", "products_partial_update", "products_delete"], 'broker:19092'))
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8050", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Product Development Server"
        }
        ])


@app.get("/")
def read_root():
    return {"Hello": "Proto Product Service API"}

@app.post("/products/", response_model=Product)
async def create_product(product: Product, 
                         request: Request,
                         session: Annotated[Session, Depends(get_session)], 
                         producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
                        )->Product:
    # '''
    # product_dict = {field: getattr(product, field) for field in product.dict()}
    # product_json = json.dumps(product_dict).encode("utf-8")
    # print("Product JSON:", product_json)
    # # Produce message
    # await producer.send_and_wait("products", product_json)
    # '''

    # product_protbuf = Product_pb2.Product(id=product.id, name=product.name, price=product.price)
    # print(f"Product Create Protobuf: {product_protbuf}")
    # # Serialize the message to a byte string
    # serialized_product = product_protbuf.SerializeToString()
    # print(f"Serialized data: {serialized_product}")
    # # Produce message
    # await producer.send_and_wait("products_create", serialized_product)

    # return product
    print("Product in create_product of main: ", product)
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    product.user_id = user.get('id')
    # Create product
    repository = ProductRepository(session)
    return await repository.create_product(product, producer)

@app.put("/products/{id}", response_model=Product)
async def update_product(id: int, 
                         product: Product,
                         request: Request,
                         session: Annotated[Session, Depends(get_session)],
                         producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
                        )->Product:

    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user.get('id')
    # Update product
    repository = ProductRepository(session)
    return await repository.update_product(id, product, user_id, producer)

    # # session.exec(select(Product).where(Product.id == id).update(product.dict(exclude_unset=True)))
    # existing_product = session.get(Product, id)
    # if not existing_product:
    #     raise HTTPException(status_code=404, detail="Product not found")
    
    # product_dict = {field: getattr(product, field) for field in product.dict()}
    # product_dict["id"] = id

    # print(f"Product Dict: {product_dict}")

    # # product_protbuf = Product_pb2.Product(id=product.id, name=product.name, price=product.price)
    # product_protbuf = Product_pb2.Product(**product_dict)
    # print(f"Product Update Protobuf: {product_protbuf}")
    
    # # Serialize the message to a byte string
    # serialized_product = product_protbuf.SerializeToString()
    # print(f"Serialized data: {serialized_product}")
    # # Produce message
    # await producer.send_and_wait("products_full_update", serialized_product)
    # return product

@app.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id: int,
                         request: Request,
                         session: Annotated[Session, Depends(get_session)],
                         producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
                        ):

    # Delete product

    repository = ProductRepository(session)
    try:
        user = await get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user_id = user.get('id')
        result = await repository.delete_product(id, user_id, producer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return status.HTTP_204_NO_CONTENT

    # product = session.get(Product, id)
    # if not product:
    #     raise HTTPException(status_code=404, detail="Product not found")
        
    # product_dict = {field: getattr(product, field) for field in product.dict()}
    # product_protbuf = Product_pb2.Product(**product_dict)
    # print(f"Product Delete Protobuf: {product_protbuf}")
    # # Serialize the message to a byte string
    # serialized_product = product_protbuf.SerializeToString()
    # print(f"Serialized data: {serialized_product}")
    # # Produce message
    # await producer.send_and_wait("products_delete", serialized_product)

    # return product
   
    # result = await repository.delete_product(id, producer)
    # if not result:
    #     raise HTTPException(status_code=404, detail="Product not found")
    # return result

    # json_compatible_result_data = jsonable_encoder(result)
    # return JSONResponse(content=json_compatible_result_data)

@app.get("/products/", response_model=list[Product])
async def read_products(session: Annotated[Session, Depends(get_session)]):
    repository = ProductRepository(session)
    return await repository.get_products()

@app.get("/products/{id}", response_model=Product)
async def read_product(id: int, session: Annotated[Session, Depends(get_session)]):
    repository = ProductRepository(session)
    return await repository.get_product_by_id(id)