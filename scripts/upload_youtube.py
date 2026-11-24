import json
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


ROOT = Path(__file__).resolve().parents[1]
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python scripts/upload_youtube.py <video.mp4> <metadata.json>"
        )

    video_path = Path(sys.argv[1])
    metadata_path = Path(sys.argv[2])
    if not video_path.is_file():
        raise SystemExit(f"Video file not found: {video_path}")
    if not metadata_path.is_file():
        raise SystemExit(f"Metadata file not found: {metadata_path}")

    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    missing = [
        name for name, value in [
            ("YOUTUBE_CLIENT_ID", client_id),
            ("YOUTUBE_CLIENT_SECRET", client_secret),
            ("YOUTUBE_REFRESH_TOKEN", refresh_token),
        ] if not value
    ]
    if missing:
        raise SystemExit("Missing GitHub Actions secrets: " + ", ".join(missing))

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title")
    description = metadata.get("description", "")
    tags = metadata.get("tags", [])
    if not title:
        raise SystemExit("Metadata JSON must contain a non-empty title.")

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    credentials.refresh(Request())

    youtube = build("youtube", "v3", credentials=credentials)
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": "1",
            "defaultLanguage": metadata.get("language", "ur"),
        },
        "status": {
            # Always upload privately. Public publishing remains a human decision.
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
        },
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
    )
    response = None
    while response is None:
        _, response = request.next_chunk()
    print("YOUTUBE_UPLOAD_COMPLETE")
    print("VIDEO_ID=" + response["id"])
    print("VIDEO_URL=https://www.youtube.com/watch?v=" + response["id"])


if __name__ == "__main__":
    main()
