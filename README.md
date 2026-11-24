# HansiZappo Movie Teller Automation

A zero-budget cloud workflow for producing Urdu-narrated movie-explainer drafts.

## Current episode
- Latest episode: The Martian (2015), Episode 002; Interstellar remains Episode 001
- Format: full-story explanation with spoilers and ending interpretation
- Voice: offline Piper Urdu voice (ur_PK-fasih-medium); narration input is Urdu script and spoken output is Pakistani Urdu
- Scene cards: Roman Urdu
- Visuals: original scene-inspired illustrations generated with Pillow; no copied film frames or movie footage
- Output: 1280x720 MP4 assembled with FFmpeg
- Latest measured runtime: approximately 6 minutes 3 seconds

## Run it
1. Open the **Actions** tab.
2. Select **Build Movie Teller Video** and set `episode_file` to `episodes/episode-002.json`.
3. Choose **Run workflow**.
4. Download the artifact named `hansizappo-movie-teller-video`.

A push to the main branch also starts a build automatically. YouTube upload is never triggered by a push. It is available only when manually running the workflow and explicitly checking the `upload_to_youtube` option; the upload script always sets visibility to **private**.

## Zero-budget and copyright notes
No paid API, subscription, billing account, or paid credit is configured. GitHub-hosted runners are temporary and subject to free-tier limits; this is scheduled job execution, not an always-on server. The narration is original commentary and the visuals are original illustrations rather than copied frames from Interstellar. This is a review draft, not an automatically published YouTube upload. Publishing publicly requires a separate owner action in YouTube Studio. The optional API upload is private-only. It requires GitHub Actions secrets named `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN`; never commit or paste these values into chat.

## Files
- `.github/workflows/build-video.yml`: cloud workflow with manual, opt-in private upload
- `scripts/upload_youtube.py`: YouTube Data API uploader (private-only)
- `episodes/episode-001.json`: Interstellar narration; `episodes/episode-002.json`: The Martian narration and Roman Urdu scene-card captions
- `scripts/build_video.py`: offline voice-over and MP4 renderer
- `publishing/the-martian-episode-002-metadata.json`: The Martian YouTube metadata
- `requirements.txt`: Python dependencies
