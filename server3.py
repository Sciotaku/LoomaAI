import io
import json
import fitz
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

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

def extract_text_from_pdf(pdf_url):
    response = requests.get(pdf_url)
    pdf = io.BytesIO(response.content)
    text = ""
    with fitz.open(stream=pdf) as doc:
        for page_num in range(len(doc)):
            text += doc.load_page(page_num).get_text()
    return text

@app.route('/summarize_chapter', methods=['POST'])
def summarize_chapter():
    try:
        grade = request.json['grade']
        subject_name = request.json['subject_name']
        chapter_title = request.json['chapter_title']

        with open('looma_data.json', 'r') as f:
            looma_data = json.load(f)

        pdf_url = looma_data.get(grade, {}).get(subject_name, {}).get(chapter_title)
        if not pdf_url:
            return jsonify({"error": "PDF URL not found"}), 404

        text = extract_text_from_pdf(pdf_url)
        chapter_summary = llama3(f"Summarize the following text for Grade {grade}, Subject {subject_name}, Chapter {chapter_title}: {text}")
        
        return jsonify({"summary": chapter_summary})
    
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error: {e}")
        print(f"Traceback: {tb}")
        return jsonify({"error": str(e), "traceback": tb}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
