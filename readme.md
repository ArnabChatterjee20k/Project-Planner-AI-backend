### Local Setup
```
    pip install virtualenv

    virtualenv env

    source env/bin/activate #for linux
    env/scripts/active #for windows

    pip install -r requirements.txt
```

* Create .env by seeing .env.example file

```
    celery -A celery_worker.celery_app worker --loglevel INFO -P solo
```

```
    python app.pys
```