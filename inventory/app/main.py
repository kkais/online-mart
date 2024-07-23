from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from fastapi import FastAPI, Depends
from sqlmodel import Session
from app.utils.session import get_session
from app.Models.Inventory import Inventory, InventoryBalance, InventoryRead
from app.database.create_schema import create_db_and_tables
from app.repositories.InventoryRepository import InventoryRepository
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

app = FastAPI(lifespan=lifespan, title="Inventory Service",
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8020", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Inventory Server"
        }
    ])

@app.get("/")
async def root():
    return {"Hello": "inventory world"}

@app.get("/inventory", response_model=list[InventoryRead])
async def read_inventory(session: Annotated[Session, Depends(get_session)]):
    repository = InventoryRepository(session)
    return await repository.get_inventory()

@app.get("/inventory/{product_id}", response_model=InventoryBalance)
async def read_inventory_by_product_id(product_id: int, session: Annotated[Session, Depends(get_session)]):
    repository = InventoryRepository(session)
    return await repository.get_inventory_by_product_id(product_id)
    
@app.post("/inventory", response_model=Inventory)
@app.post("/reduce-inventory", response_model=Inventory)
async def create_inventory(inventory: Inventory, session: Annotated[Session, Depends(get_session)]):
    repository = InventoryRepository(session)
    return await repository.create_inventory(inventory)
    