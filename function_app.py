import azure.functions as func
import logging
import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

app = func.FunctionApp()

SENDER = os.getenv("SENDER")
SECRET_KEY_FUNC = os.getenv("SECRET_KEY_FUNC")
API_DOMAIN = os.getenv("API_DOMAIN")
SG_KEY = os.getenv("SG_KEY")  

@app.queue_trigger(arg_name="azqueue", queue_name="activate", connection="AzureWebJobsStorage")
def QueueTriggerFunctionActivateAccount(azqueue: func.QueueMessage):
    """
    Procesa mensajes desde la cola 'activate' y envía correos de activación.
    """
    recipient_email = azqueue.get_body().decode('utf-8')
    logging.info('Processing new message from queue: %s', recipient_email)

    try:
        response = requests.post(
            f"{API_DOMAIN}/user/{recipient_email}/code",
            headers={"Authorization": SECRET_KEY_FUNC}
        )
        response.raise_for_status()
        activation_code = response.json().get('code')
        logging.info(f"Activation code for {recipient_email}: {activation_code}")
    except requests.RequestException as e:
        logging.error(f"Error fetching activation code: {str(e)}")
        return

    subject = "Initium: Código de activación de cuenta"
    email_content = f"""
    Estimado usuario,

    Su código de activación es: {activation_code}

    Por favor, utilícelo para activar su cuenta en nuestra plataforma.

    Saludos,
    El equipo de Initium
    """
    message = Mail(
        from_email=SENDER,
        to_emails=recipient_email,
        subject=subject,
        plain_text_content=email_content
    )

    try:
        sg = SendGridAPIClient(SG_KEY)
        response = sg.send(message)
        if response.status_code == 202:  
            logging.info(f"Email sent successfully to {recipient_email}")
        else:
            logging.warning(f"SendGrid responded with status code {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending email via SendGrid: {str(e)}")
