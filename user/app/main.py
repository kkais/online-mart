from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlmodel import Session, select
from typing import Annotated, AsyncGenerator
from app.database.create_schema import create_db_and_tables
from app.Models.User import User, UserLogin, UserRead, TokenData
from app.utils.user_auth import get_secret_from_kong, create_jwt_token, hash_password, get_current_user
from app.utils.session import get_session
from app.repositories.UserRepository import UserRepository
from app.settings import CONSUMER_ID
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

app = FastAPI(lifespan=lifespan, title="User Service",
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8040", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development User Server"
        }
    ])

@app.post("/token/")
async def generate_token(data: TokenData, consumer_id: str):
    secret = get_secret_from_kong(consumer_id)
    payload = {"iss": data.iss}
    token = create_jwt_token(payload, secret)
    return {"token": token}

@app.get("/")
async def read_all_users():
    return {"Hello": "user World"}

@app.get("/user", response_model=UserRead) 
async def read_user(email: str, session: Annotated[Session, Depends(get_session)]):
    user = session.get(UserRead, email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/register", response_model=UserRead)
async def create_user(user: User, session: Annotated[Session, Depends(get_session)]):
    logger.info(f"User: {user}")
    # Create user
    repository = UserRepository(session)
    return await repository.create_user(user)

    
@app.post("/login")
async def login(loginUser: UserLogin, session: Annotated[Session, Depends(get_session)]):
    logger.info(f"Login User: {loginUser}")
    
    # # Validate user
    # repository = UserRepository(session)
    # user = await repository.get_user_by_email(loginUser.email)
    # if user is None:
    #     raise HTTPException(status_code=401, detail="Invalid email or password")
    statement = select(User).where(User.email == loginUser.email, User.hashed_password == hash_password(loginUser.password), User.is_active == True)
    user = session.exec(statement).one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password or user is not active")
    
    # Create token
    secret = get_secret_from_kong(CONSUMER_ID)
    payload = {"iss": user.api_key}
    token = create_jwt_token(payload, secret)
    return {"token": token}


@app.get("/user/{token}")
async def read_user_me(token: str):
    logger.info(f"Token in main: {token}")
    # auth_token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    current_user = await get_current_user(token)
    logger.info(f'Current User in main: {current_user}')
    return current_user

@app.get("/admin")
async def read_admin():
    return {"Hello": "Admin"}

@app.post("/admin")
async def create_admin():
    return {"Hello": "Admin"}

