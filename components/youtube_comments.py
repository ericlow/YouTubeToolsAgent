import os
import re
import json
import csv
import argparse
from urllib.parse import urlparse, parse_qs
import googleapiclient.discovery
import googleapiclient.errors


def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    # Handle different URL formats
    parsed_url = urlparse(url)

    if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed_url.path[1:]
    if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]

    # Check if it's just a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_video_comments(api_key, video_id, max_results=100):
    """Retrieve comments for a YouTube video using the YouTube Data API."""
    # Set up the API client
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)

    comments = []
    next_page_token = None

    # Fetch comments page by page
    while True:
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,  # Maximum allowed by API
                pageToken=next_page_token
            )
            response = request.execute()

            # Process comments from this page
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "author": comment["authorDisplayName"],
                    "published_at": comment["publishedAt"],
                    "updated_at": comment["updatedAt"],
                    "like_count": comment["likeCount"],
                    "text": comment["textDisplay"]
                })

            # Check if we've reached the desired maximum
            if len(comments) >= max_results:
                comments = comments[:max_results]
                break

            # Get the next page token
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error occurred: {e}")
            break

    return comments


def save_comments_to_csv(comments, filename):
    """Save comments to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['author', 'published_at', 'updated_at', 'like_count', 'text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for comment in comments:
            writer.writerow(comment)

    print(f"Saved {len(comments)} comments to {filename}")


def save_comments_to_json(comments, filename):
    """Save comments to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(comments, jsonfile, indent=2, ensure_ascii=False)

    print(f"Saved {len(comments)} comments to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Download YouTube video comments.')
    parser.add_argument('url', help='YouTube video URL or ID', default='')
    parser.add_argument('--api-key', help='YouTube Data API key', required=True)
    parser.add_argument('--max', type=int, default=100, help='Maximum number of comments to download')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Output format (csv or json)')
    parser.add_argument('--output', help='Output filename (without extension)')

    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
        print(f"Downloading comments for video ID: {video_id}")

        comments = get_video_comments(args.api_key, video_id, args.max)
        print(f"Retrieved {len(comments)} comments")

        # Determine output filename
        if args.output:
            filename = f"{args.output}.{args.format}"
        else:
            filename = f"comments_{video_id}.{args.format}"

        # Save in the specified format
        if args.format == 'csv':
            save_comments_to_csv(comments, filename)
        else:
            save_comments_to_json(comments, filename)

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()