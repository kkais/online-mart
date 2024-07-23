import hashlib
import httpx
from fastapi import HTTPException, Depends
from sqlmodel import select
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, CONSUMER_ID
from datetime import datetime, timedelta
from jose import jwt
from app.utils.session import get_session
from app.Models.User import User
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_secret_from_kong(consumer_id: str) -> str:
    with httpx.Client() as client:
        print(f'consumer_id: {consumer_id}')
        url = f"http://kong:8001/consumers/{consumer_id}/jwt"
        response = client.get(url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code,
                                detail="Failed to fetch secret from Kong")
        
        kong_data = response.json()
        print(f'Kong Data: {kong_data}')

        if not kong_data['data'][0]["secret"]:
            raise HTTPException(
                status_code=404, detail="No JWT credentials found for the specified consumer")

        secret = kong_data['data'][0]["secret"]
        print(f'Secret: {secret}')
        
        return secret
    
def create_jwt_token(data: dict, secret: str):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Limit expiration time to 2038-01-19 03:14:07 UTC
    expire = min(expire, datetime(2038, 1, 19, 3, 14, 7))
    to_encode.update({"exp": expire})

    headers = {
        "typ": "JWT",
        "alg": ALGORITHM
    }
    
    encoded_jwt = jwt.encode(to_encode, secret,
                             algorithm=ALGORITHM, 
                             headers=headers)
    
    return encoded_jwt

def decode_jwt_token(token: str, consumer_id: str):
    secret = get_secret_from_kong(consumer_id)
    return jwt.decode(token, secret, algorithms=[ALGORITHM])

def get_user_key_from_jwt_token(token: str):
    decoded_token = decode_jwt_token(token, CONSUMER_ID)
    return decoded_token['iss']

async def get_user(user_key: str):
    # with httpx.Client() as client:
    #     url = f"http://kong:8001/users/{user_key}"
    #     response = client.get(url)
    #     if response.status_code != 200:
    #         raise HTTPException(status_code=response.status_code,
    #                             detail="Failed to fetch user from Kong")
    #     user = response.json()
    #     return user
    session = next(get_session())
    statement = select(User).where(User.api_key == user_key)
    logger.info(f'Statement : {statement}')
    user = session.exec(statement).one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # repository = UserRepository(session)
    # user = repository.get_user_by_api_key(user_key)
    return user

async def get_current_user(token: str):
    token = token.split(" ")[1]
    logger.info(f'Token in get_current_user: {token}')
    user_key = get_user_key_from_jwt_token(token)
    logger.info(f'User Key: {user_key}')
    user =  await get_user(user_key)
    logger.info(f'Current User: {user}')
    return user

def get_current_active_user(current_user: str = Depends(get_current_user)):
    if not current_user['is_active']:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(current_user: str = Depends(get_current_user)):
    if current_admin := current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_admin

def hash_password(password: str):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# def verify_password(plain_password: str, hashed_password: str):
#     return hashed_password == hash_password(plain_password)

