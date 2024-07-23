from http.client import HTTPException
from fastapi import Request
import httpx
import logging

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

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

async def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    logger.info(f"Token: {token}")
    async with httpx.AsyncClient() as client:
        url = f"http://user-service:8040/user/{token}"
        # url = f"http://user-service:3501/v1.0/invoke/user-service/method/user/{token}"
        response = await client.get(url)
        logger.info(response)
        if response.status_code != 200:
            raise HTTPException(response.status_code, "Failed to fetch user from Kong")
        user = response.json()
    return user