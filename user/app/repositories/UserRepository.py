import json
from sqlmodel import Session, select
# from sqlmodel.ext.asyncio.session import AsyncSession
from app.Models.User import User, UserLogin, UserRead, TokenData
import logging

from app.utils.user_auth import hash_password

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


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_users(self):
        return self.session.exec(select(User)).all()

    async def get_user_by_id(self, user_id: int):
        return await self.session.get(User, user_id)
    
    async def get_user_by_api_key(self, api_key: str):
        return await self.session.get(User, api_key)

    async def create_user(self, user: User):
        user.hashed_password = hash_password(user.hashed_password)
        user.is_active = True
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return UserRead.model_validate(user) # return user


    async def update_user(self, user_id: int, updated_user: User):
        existing_user = self.session.get(User, user_id)
        if not existing_user:
            return None
        
        logger.info(f"Existing User: {existing_user}")
        logger.info(f"Updated User: {updated_user}")

        existing_user.first_name = updated_user.first_name
        existing_user.last_name = updated_user.last_name
        existing_user.email = updated_user.email
        existing_user.is_active = updated_user.is_active
        existing_user.api_key = updated_user.api_key
        
        logger.info(f"User Updated: {existing_user}")

        self.session.add(existing_user)
        self.session.commit()
        self.session.refresh(existing_user)
        return existing_user

    async def delete_user(self, user_id: int):
        user = self.session.get(User, user_id)
        if not user:
            return None

        self.session.delete(user)
        self.session.commit()
        
        return json.dumps({"message": "Product deleted successfully"})