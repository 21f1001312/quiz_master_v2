# quiz_backend/applications/quiz_worker.py

from celery import Celery, Task
from applications import app 

def make_celery(app):
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    celery.Task = FlaskTask
    return celery

celery = make_celery(app)
