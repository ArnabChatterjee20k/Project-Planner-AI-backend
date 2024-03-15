from flask import Flask,render_template,request,redirect,url_for ,jsonify
from system.utils.create_queue import create_queue
from dotenv import load_dotenv
from system.KnowledgeBase.utils import *
from celery import Celery, Task , current_app
from celery.result import AsyncResult
from flask_sqlalchemy import SQLAlchemy
from system.db import db
from uuid import uuid4
load_dotenv(".env")
from system.models.models import *


def celery_init_app(app: Flask) -> Celery:
    create_queue()
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.Task = FlaskTask
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app():
    app = Flask(__name__,template_folder="./views",static_folder="./contents")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    app.config['UPLOAD_FOLDER'] = "system/uploads/"
    db.init_app(app)
    with app.app_context():
        db.create_all()

    CELERY_BROKER_BACKEND = "sqla+sqlite:///celery.sqlite"
    CELERY_CACHE_BACKEND = "db+sqlite:///celery.sqlite"
    CELERY_RESULT_BACKEND = "db+sqlite:///celery.sqlite"

    app.config.from_mapping(
    CELERY=dict(
        broker_url=CELERY_BROKER_BACKEND,
        result_backend=CELERY_RESULT_BACKEND,
        task_ignore_result=True,
        result_persistent = True,
        result_extended = True,
        celery_task_track_started = True
    ),
)
    app.config.from_prefixed_env()
    celery_init_app(app)
    app.app_context().push() # pushing context so that celery workers can use it

    @app.post("/study")
    def create_project():
        name = request.form.get("name")
        description = request.form.get("description")
        study = Study(name=name,description=description)
        db.session.add(study)
        db.session.commit()
        return jsonify({"status":"Success","id":study.id})

    @app.post("/upload")
    def upload():
        type = request.form.get("type")
        id = uuid4()
        task=""
        if type=="pdf":
            file = request.files.get("file")
            file_ext = file.filename.split(".")[-1]
            new_filename = f"{id}.{file_ext}"
            file.save(new_filename)
            task = index_pdf.delay(file=new_filename,id=id,type="pdf")

        elif type == "website":
            url = request.form.get("url")
            task = index_website.delay(url=url,id=id,type="website")
        
        else:
            url = request.form.get("url")
            task = index_youtube.delay(url=url,id=id,type="youtube")

        return {"task_id":task.id}


    @app.get("/result/<id>")
    def task_result(id: str) -> dict[str, object]:
        result = AsyncResult(id)
        return {
            "id":result.task_id,
            "ready": result.ready(),
            "state":result.state,
            "kwargs":result.kwargs,
            "successful": result.successful(),
            "value": result.result if result.ready() else None,
        }
    return app