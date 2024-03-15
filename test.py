from system.db import db
from system.models.models import *
from system import create_app
app = create_app()
with app.app_context():
    db.session.delete(KnowledgeSource.query.get("fd59cda6-f341-4a79-b66d-03adab344c00"))
    db.session.commit()