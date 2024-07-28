import requests

def get_chapter_summary(grade, subject_name, chapter_number):
    url = "http://localhost:5001/summarize_chapter"
    data = {
        "grade": grade,
        "subject_name": subject_name,
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
    # Replace these with actual values
    grade = 10
    subject_name = "Science"
    chapter_number = 1
    
    summary = get_chapter_summary(grade, subject_name, chapter_number)
    print(f"Summary of Chapter {chapter_number} for Grade {grade}, Subject {subject_name}:\n{summary}")

if __name__ == '__main__':
    main()
