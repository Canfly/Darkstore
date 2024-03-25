from darkstore.celery import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@app.task
def taskone():
     logger.info('ГОВНОГОВНОГОВНОГОВНОГОВНО')
