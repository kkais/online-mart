import asyncio
import json
from aiokafka import AIOKafkaConsumer
from sqlmodel import create_engine, Session, select
from app.Models.Product import Product
from app.Models import Product_pb2
from app import settings
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)

def get_session():
    with Session(engine) as session:
        yield session

async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        *topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-group",
        auto_offset_reset='earliest'
    )

    while True:
        try:
            # Start the consumer.
            await consumer.start()
            logging.info("Consumer started")
            break
        except Exception as e:
            logging.error(f"Failed to start consumer: {e}")
            await asyncio.sleep(5)
    
    try:
        # Continuously listen for messages.
        async for message in consumer:
            try:
                # print(f"Received message: {message.value.decode()} on topic {message.topic}")
                logging.info(f"\n\nReceived message on topic: {topic}")
                logging.info(f"\n\nReceived message: {message}")
                logging.info(f"\n\nReceived message value: {message.value}")
                logging.info(f"\n\nReceived message topic: {message.topic}")


                # Here you can add code to process each message.
                # Example: parse the message, store it in a database, etc.

                # '''
                # product_data = json.loads(message.value.decode('utf-8'))
                # # product_obj = Product(**product_data)
                # product = Product.model_validate(product_data)
                # '''
                session = next(get_session())

                # match topic.action:
                #     case 'create':
                # if message.topic == 'products_create' or \
                #     message.topic == 'products_full_update' or \
                #     message.topic == 'products_partial_update':
                newProduct = Product_pb2.Product()
                newProduct.ParseFromString(message.value)
                logging.info(f"\n\n Consumer Deserialized data: {newProduct}")
                product = Product.model_validate(newProduct)
                # elif message.topic == 'products_delete':
                #     newProduct = Product_pb2.ProductRead()
                #     newProduct.ParseFromString(message.value)
                #     logging.info(f"\n\n Consumer Deserialized data: {newProduct}")
                #     product = ProductRead.model_validate(newProduct)

                if message.topic == 'products_create':
                    logging.info(f"Adding Product: {product}")
                    session.add(product)
                    session.commit()
                    session.refresh(product)

                elif message.topic == 'products_full_update':
                    logging.info(f"Updating Full Product: {product}")
                    statement = select(Product).where(Product.id == product.id)
                    existing_product = session.execute(statement).first()
                    logging.info(f"Existing Product in Consumer: {existing_product}")

                    if existing_product:
                        existing_product[0].name = product.name
                        existing_product[0].price = product.price
                        existing_product[0].updated_at = datetime.now(tz=None)
                        session.add(existing_product[0])
                        session.commit()
                        session.refresh(existing_product[0])

                elif message.topic == 'products_partial_update':
                    logging.info(f"Updating Partial Product: {product}")
                    existing_product = session.execute(select(Product).where(Product.id == product.id)).first()
                    logging.info(f"Existing Product: {existing_product}")

                    if existing_product:
                        existing_product[0].name = product.name
                        existing_product[0].price = product.price
                        session.add(existing_product[0])
                        session.commit()
                        session.refresh(existing_product[0])
                        
                elif message.topic == 'products_delete':
                    logging.info(f"Deleting Product: {product}")
                    statement = select(Product).where(Product.id == product.id)
                    existing_product = session.execute(statement).first()
                    logging.info(f"Existing Product: {existing_product}")
                    session.delete(existing_product[0])
                    session.commit()
                    
                else:
                    logging.info('No action specified')

                # case 'partial_update':
                #     newProduct = Product_pb2.Product()
                #     newProduct.ParseFromString(message.value)
                #     logging.info(f"\n\n Consumer Partial Update Deserialized data: {newProduct}")
                #     product = Product.model_validate(newProduct)
                #     dbProduct = session.get(Product, product.id)
                        
                #     if not dbProduct:
                #         logging.info('Product not found')
                #         return

                #     dbProduct.name = product.name
                #     session.add(dbProduct)
                #     product = dbProduct
                    # case 'update':
                    #     newProduct = Product_pb2.Product()
                    #     newProduct.ParseFromString(message.value)
                    #     logging.info(f"\n\n Consumer Update Deserialized data: {newProduct}")
                    #     product = Product.model_validate(newProduct)
                    #     dbProduct = session.get(Product, product.id)
                        
                    #     if not dbProduct:
                    #         logging.info('Product not found')
                    #         return
                        
                    #     dbProduct.name = product.name
                    #     dbProduct.price = product.price
                    #     session.add(dbProduct)
                    #     product = dbProduct

                    # case 'delete':
                    #     productID = Product_pb2.ProductRead()
                    #     productID.ParseFromString(message.value)

                    #     if not dbProduct:
                    #         logging.info('Product not found')
                    #         return

                    #     dbProduct = session.get(Product, product.id)
                    #     session.delete(dbProduct)

                    # case _:
                    #     logging.info('No action specified')

                

            except Exception as e:
                logging.error(e)

    except Exception as e:
        logging.error(e)
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()