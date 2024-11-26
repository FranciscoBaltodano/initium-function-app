import azure.functions as func
import logging
import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar la Function App
app = func.FunctionApp()

# Variables de entorno
SENDER = os.getenv("SENDER")
SECRET_KEY_FUNC = os.getenv("SECRET_KEY_FUNC")
API_DOMAIN = os.getenv("API_DOMAIN")
SG_KEY = os.getenv("SG_KEY")  # Clave de API de SendGrid

@app.queue_trigger(arg_name="azqueue", queue_name="activate", connection="AzureWebJobsStorage")
def QueueTriggerFunctionActivateAccount(azqueue: func.QueueMessage):
    """
    Procesa mensajes desde la cola 'activate' y envía correos de activación.
    """
    # Decodificar el mensaje de la cola
    recipient_email = azqueue.get_body().decode('utf-8')
    logging.info('Processing new message from queue: %s', recipient_email)

    # Llamar a la API externa para obtener el código de activación
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

    # Crear el correo electrónico
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

    # Enviar el correo con SendGrid
    try:
        sg = SendGridAPIClient(SG_KEY)
        response = sg.send(message)
        if response.status_code == 202:  # Código de éxito de SendGrid
            logging.info(f"Email sent successfully to {recipient_email}")
        else:
            logging.warning(f"SendGrid responded with status code {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending email via SendGrid: {str(e)}")
