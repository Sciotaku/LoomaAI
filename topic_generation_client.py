import requests

def get_chapter_topics(chapter_id):
    url = "http://localhost:5001/generate_topics"
    data = {"chapter_id": chapter_id}
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()

def main():
    chapter_id = input("Enter the chapter ID (e.g., 10S01): ")
    try:
        result = get_chapter_topics(chapter_id)
        if 'topics' in result:
            print(f"Topics for Chapter {chapter_id}:")
            for topic in result['topics']:
                print(f"- {topic}")
        else:
            print(f"Error: {result['error']}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
