from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("looma")

# Function to get details of a specific chapter
def get_chapter_details(chapter_id):
    chapters = db.get_collection("chapters")
    chapter = chapters.find_one({"_id": chapter_id})
    if chapter:
        print(f"\nDetails of Chapter {chapter_id}:")
        for key, value in chapter.items():
            print(f"{key}: {value}")
    else:
        print(f"Chapter with ID {chapter_id} not found.")

if __name__ == "__main__":
    # Check details of a specific chapter
    chapter_id = "10S01"  # You can change this ID to any other chapter ID
    get_chapter_details(chapter_id)
