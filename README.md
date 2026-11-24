# HansiZappo Movie Teller Automation

A free-tier cloud workflow for producing Roman Urdu narrated video drafts.

## Current workflow
- GitHub Actions runs in the cloud (manual trigger or weekly schedule).
- Python creates original star-field cards for each narration segment.
- Edge TTS generates Urdu voice-over.
- FFmpeg combines the cards and narration into an MP4.
- The MP4 is saved as a GitHub Actions artifact for 7 days.

## Run it
1. Replace the sample narration in `episodes/episode-001.json` with an approved script.
2. Open the **Actions** tab.
3. Select **Build Movie Teller Video** and choose **Run workflow**.
4. Download the artifact named `hansizappo-movie-teller-video`.

## Current limitations
This is the first rendering stage only. It does not yet research movies, create movie footage, make thumbnails, or upload to YouTube. No paid API, subscription, billing account, or paid credit is configured. GitHub-hosted runners are temporary and subject to free-tier limits; this is scheduled job execution, not an always-on server. The renderer currently uses original generated cards, not movie clips.

## Files
- `.github/workflows/build-video.yml`: cloud workflow
- `episodes/episode-001.json`: narration input
- `scripts/build_video.py`: voice-over and MP4 renderer
- `requirements.txt`: Python dependencies
