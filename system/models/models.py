from sqlalchemy import Column,String,Boolean
from system.db import db

class Study(db.Model):
    id = db.Column("id",db.Integer,primary_key=True,auto_increment=True)
    name = db.Column("name",db.String)
    description = db.Column("description",db.String)
    knowledge_sources = db.relationship("KnowledgeSource",back_populates="study")

class KnowledgeSource(db.Model):
    id = db.Column("id",db.String,primary_key=True,auto_increment=True)
    type = db.Column("type",db.String)
    task_id = db.Column("task_id",db.String)
    indexed = db.Column("indexed",db.Boolean,default=False)
    project_id = db.Column(db.Integer,db.ForeignKey("study.id"))
    study = db.relationship("Study",back_populates="knowledge_sources")

    @property
    def get_location_of_faiss(self):
        id = self.id
        type = self.type
        if type=="website":
            type = "site"
        return f"{type}/{id}"