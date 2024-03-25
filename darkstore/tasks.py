from celery import shared_task


@app.task
def taskone():
    print('ГОВНОГОВНОГОВНОГОВНОГОВНО')
