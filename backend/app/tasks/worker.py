from app.core.celery_app import celery_app


@celery_app.task(name='app.tasks.healthcheck')
def healthcheck() -> str:
    return 'ok'
