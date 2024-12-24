import os
import pandas as pd
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv

class YouTubeCommentScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def extract_video_id(self, url):
        """Extract YouTube video ID from a URL."""
        video_id_match = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
        if video_id_match:
            return video_id_match.group(1)
        else:
            raise ValueError("Invalid YouTube URL. Video ID could not be extracted.")

    def get_video_comments(self, video_id):
        """Retrieve comments from a YouTube video."""
        comments = []

        request = self.youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )
        while request:
            response = request.execute()

            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    "Comment": snippet['textDisplay'],
                    "Likes": snippet['likeCount'],
                    "Author": snippet['authorDisplayName'].replace('@', ''),
                    "Author URL": snippet['authorChannelUrl'],
                    "Published At": snippet['publishedAt']
                })

            request = self.youtube.commentThreads().list_next(request, response)

        return comments

    def save_to_csv(self, data, file_name):
        """Save comments to a CSV file."""
        df = pd.DataFrame(data)
        df.to_csv(file_name, index=False, encoding='utf-8-sig')

    def sort_comments(self, comments, sort_by, ascending=False):
        """Sort comments by a specific key."""
        return sorted(comments, key=lambda x: x.get(sort_by, 0), reverse=not ascending)

    def run(self, url, sort_by="Likes", ascending=False):
        """Main method to run the scraper."""
        try:
            print("Extracting video ID from URL...")
            video_id = self.extract_video_id(url)
            print(f"Video ID: {video_id}")

            print("Fetching comments...")
            comments = self.get_video_comments(video_id)
            print(f"Fetched {len(comments)} comments.")

            print("Sorting comments...")
            sorted_comments = self.sort_comments(comments, sort_by, ascending)

            file_name = "youtube_comments.csv"
            print(f"Saving comments to {file_name}...")
            self.save_to_csv(sorted_comments, file_name)

            print(f"Comments saved to '{file_name}' successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    load_dotenv()

    # Initialize API key
    API_KEY = os.getenv("YOUTUBE_API_KEY")

    if not API_KEY:
        print("API key not found in environment variables. Please set 'YOUTUBE_API_KEY' in your .env file.")
        exit(1)

    scraper = YouTubeCommentScraper(API_KEY)
    print()

    # Input YouTube URL and sorting preference
    youtube_url = input("Enter the YouTube video URL: ")
    sort_criteria = input("Enter the sorting criteria (Likes or Published At): ")
    order = input("Sort ascending? (yes or no): ").strip().lower() == "yes"

    # Run the scraper
    scraper.run(youtube_url, sort_by=sort_criteria, ascending=order)
