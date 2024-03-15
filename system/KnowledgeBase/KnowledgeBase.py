from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv
from os import environ
load_dotenv(".env")
class KnowledgeBase:
    def __init__(self):
        self.API_KEY = environ.get("GOOGLE_API_KEY")
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=self.API_KEY)
        self.model = ChatGoogleGenerativeAI(model="gemini-pro",
                             temperature=0.3,google_api_key=self.API_KEY)
    def generate_FAISS(self,data,location,chunk_size=1000):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
        docs = text_splitter.split_documents(data)
        db = FAISS.from_documents(docs, self.embeddings)
        db.save_local(location)
    
    def get_db(self,location):
        return FAISS.load_local(location,embeddings=self.embeddings,allow_dangerous_deserialization=True)
    

    def chat(self,question,docs:list[Document],prompt:PromptTemplate):
        chain = load_qa_chain(self.model, chain_type="stuff", prompt=prompt)
        return chain( {"input_documents":docs, "question": question} , return_only_outputs=True)