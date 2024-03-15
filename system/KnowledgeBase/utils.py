from system.KnowledgeBase.KnowledgeBase import KnowledgeBase
from flask import g , current_app
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from bs4 import BeautifulSoup as Soup
from langchain_community.document_loaders.youtube import YoutubeLoader
from langchain.prompts import PromptTemplate
from celery import shared_task
from system.models.models import KnowledgeSource
from system.db import db
from celery.signals import task_prerun , task_success
from celery.result import AsyncResult

knowledge = KnowledgeBase()

@shared_task(ignore_result=False)
def index_pdf(file,id,type="pdf"):
    result = PDFPlumberLoader(file)
    knowledge.generate_FAISS(result.load(),location=f"pdf/{id}")


@shared_task(ignore_result=False)
def index_website(url,id,type="website"):
    result = RecursiveUrlLoader( url=url, max_depth=6, extractor=lambda x: Soup(x, "html.parser").text)
    knowledge.generate_FAISS(result.load(),location=f"site/{id}")

@shared_task(ignore_result=False)
def index_youtube(url,id,type="youtube"):
    result = YoutubeLoader.from_youtube_url(url)
    knowledge.generate_FAISS(result.load(),location=f"youtube/{id}")


@task_prerun.connect
def index_prerun_handler(sender=None,task_id=None,task=None,*args,**kwargs):
    source = KnowledgeSource(id=str(kwargs.get("kwargs").get("id")),task_id=task_id,project_id=1,type=kwargs.get("kwargs").get("type"))
    db.session.add(source)
    db.session.commit()

@task_success.connect
def index_success_handler(result=None,sender=None,*args,**kwargs):
    task_id = sender.request.id
    source = KnowledgeSource.query.filter_by(task_id=task_id).first()
    source.indexed = True
    db.session.commit()


### semantic search across all the project ids
def get_relevant_docs(project_id,question):
    sources = KnowledgeSource.query.filter_by(project_id=project_id).all()
    locations = [source.get_location_of_faiss for source in sources]
    result = []
    for location in locations:
        db = knowledge.get_db(location)
        docs = db.similarity_search(question,k=20)
        result.extend(docs)

    return result


def get_from_ai(docs,question):
    prompt_template = """
    Explore the Text Documents. 
    If the answer is present in the context, provide comprehensive details. 
    If not, derive the answer from the video content anyhow.
    \n\n
    Transcript:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    return knowledge.chat(docs=docs,question=question,prompt=prompt)