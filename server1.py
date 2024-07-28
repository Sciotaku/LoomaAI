import io
import os
import re
import traceback
import fitz
import requests
from pymongo import MongoClient
from flask import Flask, request, jsonify
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("db_name")
collection = db.get_collection("chapters")

# Initialize HuggingFace Embeddings and FAISS
model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {}
encode_kwargs = {'normalize_embeddings': False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

faiss_db = None
try:
    os.removedirs("faiss_index")
except Exception as e:
    print(e)

# Define the Llama3 API function
llama3_url = "http://localhost:11434/api/chat"  # Ensure this is the correct URL for your local Llama3 instance

def llama3(prompt):
    data = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(llama3_url, headers=headers, json=data)
    return response.json()['message']['content']

@app.route('/summarize_chapter', methods=['POST'])
def summarize_chapter():
    try:
        textbook_id = request.json['textbook_id']
        chapter_number = request.json['chapter_number']
        
        chapter = collection.find_one({"_id": chapter_number})
        if not chapter:
            return jsonify({"error": "Chapter not found"}), 404

        groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?", chapter['_id'], re.IGNORECASE)
        grade_level = groups[1]
        subject_ab = groups[2]
        
        firstPage = chapter['pn']
        lastPage = chapter['pn'] + chapter['len']
        if firstPage == "" or lastPage == "":
            return jsonify({"error": "Invalid page numbers"}), 400
        
        textbook = db.textbooks.find_one({"prefix": grade_level + subject_ab})
        if textbook is None:
            return jsonify({"error": "Textbook not found"}), 404

        url = "https://looma.website/content/" + textbook["fp"] + textbook['fn']
        resp = requests.get(url)
        pdf = io.BytesIO(resp.content)
        text = ""
        with fitz.open(stream=pdf) as doc:
            for page in doc.pages(firstPage, lastPage, 1):
                text += page.get_text()
        
        # Use the FAISS and HuggingFace logic here if needed
        final_docs = [
            Document(page_content=text, metadata={"source": url, "firstPage": firstPage, "lastPage": lastPage})
        ]
        
        if faiss_db is None:
            faiss_db = FAISS.from_documents(final_docs, hf)
        faiss_db.add_documents(final_docs)
        faiss_db.save_local("faiss_index")
        print("[Added document to FAISS]", url, firstPage, lastPage)
        
        chapter_summary = llama3(f"Summarize the following text: {text}")
        
        return jsonify({"summary": chapter_summary})
    
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error: {e}")
        print(f"Traceback: {tb}")
        return jsonify({"error": str(e), "traceback": tb}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
