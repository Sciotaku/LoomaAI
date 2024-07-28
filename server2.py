import io
import os
import re
import traceback

import fitz
import requests
from pymongo import MongoClient
from flask import Flask, request, jsonify

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:47017/")
db = client.get_database("looma")
chapter_collection = db.get_collection("chapters")
textbook_collection = db.get_collection("textbooks")

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
        grade = request.json['grade']
        subject_name = request.json['subject_name']
        chapter_number = request.json['chapter_number']
        
        # Find the textbook based on grade and subject name
        query = {'class': f'class{grade}', 'subject': subject_name}
        textbook = textbook_collection.find_one(query)
        if not textbook:
            return jsonify({"error": "Textbook not found"}), 404
        
        # Find the chapter based on textbook ID and chapter number
        prefix = textbook.get('prefix')
        if not prefix:
            return jsonify({"error": "Prefix not found in textbook"}), 404
        
        chapter_query = {'_id': {'$regex': f'^{prefix}{chapter_number}'}}
        chapter = chapter_collection.find_one(chapter_query)
        if not chapter:
            return jsonify({"error": "Chapter not found"}), 404

        # Extract page information from chapter document
        firstPage = chapter.get('pn', '') - 1
        lastPage = chapter.get('pn', '') + chapter.get('len', '') - 2
        if firstPage == "" or lastPage == "":
            return jsonify({"error": "Invalid page numbers"}), 400

        # Construct URL to fetch the PDF
        url = f"https://looma.website/content/{textbook['fp']}{textbook['fn']}"
        resp = requests.get(url)
        pdf = io.BytesIO(resp.content)
        
        # Extract text from the specified pages of the PDF
        text = ""
        with fitz.open(stream=pdf) as doc:
            for page_num in range(firstPage, lastPage + 1):
                text += doc.load_page(page_num).get_text()

        chapter_summary = llama3(f"Summarize the following text for Grade {grade}, Subject {subject_name}, Chapter {chapter_number}: {text}")
        
        return jsonify({"summary": chapter_summary})
    
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Error: {e}")
        print(f"Traceback: {tb}")
        return jsonify({"error": str(e), "traceback": tb}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
