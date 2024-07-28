import requests

def get_chapter_summary(textbook_id, chapter_number):
    url = "http://localhost:5001/summarize_chapter"
    data = {
        "textbook_id": textbook_id,
        "chapter_number": chapter_number
    }
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['summary']
    else:
        return response.json()['error']

def main():
    textbook_id = "your_textbook_id"  
    chapter_number = "your_chapter_id" 
    
    summary = get_chapter_summary(textbook_id, chapter_number)
    print(f"Summary of Chapter {chapter_number}:\n{summary}")

if __name__ == '__main__':
    main()
