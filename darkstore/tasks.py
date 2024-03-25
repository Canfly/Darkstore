from celery import Celery

app = Celery('darkstore', broker='redis://localhost:6379')

@app.task
def taskone():
    print('ГОВНОГОВНОГОВНОГОВНОГОВНО')
