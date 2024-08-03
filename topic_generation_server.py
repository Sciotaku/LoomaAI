from flask import Flask, request, jsonify, render_template
import fitz  # PyMuPDF
import io
import requests
from pymongo import MongoClient
from pdf2image import convert_from_bytes
import pytesseract

app = Flask(__name__, static_folder='static')

# MongoDB client setup
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("looma")

# Text Extraction Functions
def extract_text_from_page(page):
    text = page.get_text()
    if text.strip():
        return text
    else:
        return None

def perform_ocr(image):
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(url, first_page, last_page):
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to download PDF from {url}. Status code: {resp.status_code}")
        return ""
    
    pdf = io.BytesIO(resp.content)
    text = ""
    with fitz.open(stream=pdf, filetype="pdf") as doc:
        for page_num in range(first_page, last_page):
            page = doc.load_page(page_num)
            extracted_text = extract_text_from_page(page)
            if extracted_text:
                text += extracted_text
            else:
                images = convert_from_bytes(resp.content, first_page=page_num+1, last_page=page_num+1)
                for image in images:
                    text += perform_ocr(image)
    return text

def generate_topics_llama3(chapter_text, num_topics=5):
    prompt = f"Extract {num_topics} topics from the following text:\n\n{chapter_text}"
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
    topics = response.json()['message']['content']
    
    topics_list = topics.split('\n')
    return topics_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_topics', methods=['POST'])
def generate_topics():
    data = request.json
    chapter_id = data.get('chapter_id')
    
    chapter = db.chapters.find_one({"_id": chapter_id})
    if not chapter:
        return jsonify({"error": "Chapter not found"}), 404
    
    try:
        grade_level = chapter_id[:-2]
        textbook = db.textbooks.find_one({"prefix": grade_level})
        if not textbook:
            return jsonify({"error": "Textbook not found"}), 404
        
        first_page = chapter['pn']
        last_page = chapter['pn'] + chapter['len']
        url = f"https://looma.website/content/{textbook['fp']}{textbook['fn']}"
        chapter_text = extract_text_from_pdf(url, first_page, last_page)
        
        topics = generate_topics_llama3(chapter_text)
        return jsonify({"chapter_id": chapter_id, "topics": topics})
    
    except Exception as e:
        app.logger.error(f"Error generating topics: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
