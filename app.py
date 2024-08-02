from flask import Flask, request, jsonify, render_template
import fitz  # PyMuPDF
import io
import os
import re
import requests
from pymongo import MongoClient
from pdf2image import convert_from_bytes
import pytesseract
from langchain_huggingface import HuggingFaceEmbeddings

app = Flask(__name__, static_folder='static')

# Initializing the HuggingFace embeddings model
model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {}
encode_kwargs = {'normalize_embeddings': False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# MongoDB client setup
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("looma")
faiss_index_path = "faiss_index"
faiss_db = None

def extract_text_from_page(page):
    text = page.get_text()
    if text.strip():  # If text is found, return it
        return text
    else:  # Otherwise, use OCR
        return None

def perform_ocr(image):
    return pytesseract.image_to_string(image)

@app.route('/')
def index():
    return render_template('chatbox.html')

@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    try:
        data = request.json
        chapter_id = data.get('chapter_id')
        
        # Fetching the chapter for the given chapter ID
        chapter = db.chapters.find_one({"_id": chapter_id})
        if not chapter:
            return jsonify({"error": "Chapter not found"}), 404
        
        groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\\.[0-9]{2})?",
                           chapter['_id'], re.IGNORECASE)
        grade_level = groups[1]  # grade level
        subject = groups[2]
        first_page = chapter['pn']
        last_page = chapter['pn'] + chapter['len']
        if first_page == "" or last_page == "":
            return jsonify({"error": "Invalid page numbers"}), 400
        
        # Retrieving the corresponding textbook
        textbook = db.textbooks.find_one({"prefix": grade_level + subject})
        if not textbook:
            return jsonify({"error": "Textbook not found"}), 404
        
        # Constructing the URL to download the PDF
        url = f"https://looma.website/content/{textbook['fp']}{textbook['fn']}"
        resp = requests.get(url)
        if resp.status_code != 200:
            return jsonify({"error": f"Failed to download PDF from {url}. Status code: {resp.status_code}"}), 500
        
        # Extracting text from the PDF
        pdf = io.BytesIO(resp.content)
        text = ""
        with fitz.open(stream=pdf, filetype="pdf") as doc:
            for page_num in range(first_page, last_page):
                page = doc.load_page(page_num)
                extracted_text = extract_text_from_page(page)
                if extracted_text:
                    text += extracted_text
                else:
                    # If no text is found, use OCR
                    images = convert_from_bytes(resp.content, first_page=page_num+1, last_page=page_num+1)
                    for image in images:
                        text += perform_ocr(image)
        
        # Generating a summary using the text
        summary = llama3(f"Summarize the following text: {text}")
        
        return jsonify({"chapter_id": chapter_id, "summary": summary})
    except Exception as e:
        app.logger.error(f"Error generating summary: {e}")
        return jsonify({"error": str(e)}), 500

def llama3(prompt):
    url = "http://localhost:11434/api/chat"  
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
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['message']['content']

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)