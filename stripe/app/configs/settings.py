from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

BASE_URL = config("BASE_URL", cast=str)
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", cast=str)
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", cast=str)

