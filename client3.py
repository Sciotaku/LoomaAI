import requests

def get_chapter_summary(grade, subject_name, chapter_title):
    url = "http://localhost:5001/summarize_chapter"
    data = {
        "grade": grade,
        "subject_name": subject_name,
        "chapter_title": chapter_title
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
    grade = "10"
    subject_name = "Science"
    chapter_title = "Scientific Learning"
    
    summary = get_chapter_summary(grade, subject_name, chapter_title)
    print(f"Summary of {chapter_title} for {grade}, {subject_name}:\n{summary}")

if __name__ == '__main__':
    main()