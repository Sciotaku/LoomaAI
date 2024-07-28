import requests

def generate_summary(chapter_id):
    url = "http://localhost:5001/generate_summary"
    data = {"chapter_id": chapter_id}
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        summary = response.json()['summary']
        print(f"Summary for Chapter {chapter_id}:")
        print(summary)
    else:
        print(f"Error: {response.json()['error']}")

if __name__ == "__main__":
    chapter_id = input("Enter the chapter ID (e.g., 10S01): ")
    generate_summary(chapter_id)