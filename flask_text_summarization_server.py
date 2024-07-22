from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    chapter_text = data['text']
    
    llama3_url = "http://localhost:11434/api/chat"
    llama3_data = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": f"Provide a short summary of the following text: {chapter_text}"
            }
        ],
        "stream": False
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(llama3_url, headers=headers, json=llama3_data)
    
    if response.status_code == 200:
        summary = response.json()['message']['content']
        return jsonify({"summary": summary})
    else:
        return jsonify({"error": f"Error: {response.status_code}, {response.text}"}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Changed to port 5001
