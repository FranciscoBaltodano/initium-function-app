import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()

@app.queue_trigger(arg_name="azqueue", queue_name="activate", connection="SA") 
def queue_trigger(azqueue: func.QueueMessage):
    body = azqueue.get_body().decode('utf-8')
    logging.info(f'QUEUE ACTIVADOOOOOOOO, EL BODY ES: {body}'), 