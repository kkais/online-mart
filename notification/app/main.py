from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from app.Models.Email import EmailRequest
from app.utils.mailer import send_email
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


app = FastAPI(title="Notification Service",
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8030", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Nofification Server"
        }
    ])

@app.get("/")
async def root():
    return {"Hello": "notification world"}

@app.post("/send-email")
async def schedule_email(request: EmailRequest, tasks: BackgroundTasks):
    data = request.dict()
    tasks.add_task(send_email, data)
    return {"status": status.HTTP_200_OK, "message": "Email has been sent successfully!"}
