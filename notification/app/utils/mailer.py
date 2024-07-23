from ssl import create_default_context
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.configs.settings import HOST, USERNAME, PASSWORD, PORT
from app.Models.Email import EmailRequest
from smtplib import SMTP
import logging

logging.basicConfig(level=logging.INFO)

def send_email(data: dict|None = None):
    msg = EmailRequest(**data)
    message = MIMEText(msg.body, 'plain')
    message['Subject'] = msg.subject
    message['From'] = USERNAME
    message['To'] = ", ".join(msg.to)

    try:
        with SMTP(HOST, PORT) as server:
            server.ehlo()
            server.starttls(context=create_default_context())
            server.ehlo()
            server.login(USERNAME, PASSWORD)
            server.send_message(message)
            server.quit()
        logging.info("Email sent successfully")
        return {"status": 200, "message": "Email sent successfully"}
    except Exception as e:
        return {"status": 500, "message": f"Failed to send email: {e}"}
    

    # from_email = FROM_EMAIL
    # password = PASSWORD

    # msg = MIMEMultipart()
    # msg["From"] = from_email
    # msg["To"] = ",".join(to_email)
    # msg["Subject"] = subject

    # msg.attach(MIMEText(body, "plain"))

    # try:
    #     server = smtplib.SMTP("smtp.gmail.com", 587)
    #     server.starttls()
    #     server.login(from_email, password)
    #     text = msg.as_string()
    #     server.sendmail(from_email, to_email, text)
    #     server.quit()
    #     logging.info("Email sent successfully")
    # except Exception as e:
    #     logging.error(f"Failed to send email: {e}")