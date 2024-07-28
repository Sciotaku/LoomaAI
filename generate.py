import io
import os
import re

import fitz
import requests
from pymongo import MongoClient

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {}
encode_kwargs = {'normalize_embeddings': False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("db_name")
collection = db.get_collection("chapters")

faiss_db = None
try:
    os.removedirs("faiss_index")
except Exception as e:
    print(e)

for chapter in collection.find({"pn": {"$ne": ""}}):
    try:
        groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?",
                           chapter['_id'], re.IGNORECASE)
        grade_level = groups[1]  # grade level
        subject = groups[2]
        firstPage = chapter['pn']
        lastPage = chapter['pn'] + chapter['len']
        if firstPage == "" or lastPage == "":
            continue
        textbook = db.textbooks.find_one({"prefix": grade_level + subject})

        url = "https://looma.website/content/" + textbook["fp"] + textbook['fn']
        resp = requests.get(url)
        pdf = io.BytesIO(resp.content)
        text = ""
        with fitz.open(stream=pdf) as doc:
            for page in doc.pages(firstPage, lastPage, 1):
                text += page.get_text()

        final_docs = [
            Document(page_content=text, metadata={"source": url, "firstPage": firstPage, "lastPage": lastPage})]

        if faiss_db is None:
            faiss_db = FAISS.from_documents(final_docs, hf)
        faiss_db.add_documents(final_docs)
        faiss_db.save_local("faiss_index")
        print("[Added document to FAISS]", url, firstPage, lastPage)
    except Exception as e:
        print("Error: ", e)