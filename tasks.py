from celery import Celery
from music_classification import MusicClassification,MusicConfig

def make_celery(app):
    celery = Celery(
        "server",
        backend=app.config['result_backend'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def load_cnn_model(app,number):
    config_file = f"./machine_learning/model_results/results_{number}/model_config.txt"
    config = MusicConfig.read_config(config_file)
    mclas = MusicClassification(config)
    mclas.load_saved_model(number)
    app.mclas = mclas
