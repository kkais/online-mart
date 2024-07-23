from starlette.config import Config

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

HOST = config("MAIL_HOST", cast=str)
USERNAME = config("MAIL_USERNAME", cast=str)
PASSWORD = config("MAIL_PASSWORD", cast=str)
PORT = config("MAIL_PORT", cast=int)
