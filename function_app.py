import azure.functions as func
import datetime
import json
import logging
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import requests


import ssl
from email.mime.multipart import MIMEMultipart
from email.header import Header


load_dotenv()

app = func.FunctionApp()

SENDER = os.getenv("SENDER")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SECRET_KEY_FUNC = os.getenv("SECRET_KEY_FUNC")
API_DOMAIN = os.getenv("API_DOMAIN")


@app.queue_trigger(arg_name="azqueue", queue_name="activate", connection="AzureWebJobsStorage")
def QueueTriggerFunctionActivateAccount(azqueue: func.QueueMessage):
    body = azqueue.get_body().decode('utf-8')

    logging.info('Processing new message from queue: %s', body)

    sender = SENDER
    password = PASSWORD
    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT
    secret_key_func = SECRET_KEY_FUNC

    subject = 'Initium: Código de activación de cuenta'


    response = requests.post(
        f"{API_DOMAIN}/user/{body}/code",
        headers={"Authorization": secret_key_func}
    )
    response.raise_for_status()
    code = response.json().get('code')
    message = MIMEText(f'Su código de activación es: {code}', 'plain', 'utf-8')
    message['From'] = sender
    message['To'] = body
    message['Subject'] = Header(subject, 'utf-8')

    try: 
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(sender, password)
            server.sendmail(sender, body, message.as_string())
        logging.info('Email sent successfully to %s', body)
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
    logging.info('Queue Trigger processed the message: %s', body)
