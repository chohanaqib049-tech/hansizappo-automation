# Google Cloud setup — HansiZappo Movie Teller

## Active project
- Project name: HansiZappo Movie Teller
- Project number: 515671790007
- Project ID: hansizappo-movie-teller

Do not use the retired NIGHTFALL BROADCAST project for new publishing setup.

## Direct console links
- YouTube Data API v3: https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=hansizappo-movie-teller
- APIs & Services dashboard: https://console.cloud.google.com/apis/dashboard?project=hansizappo-movie-teller
- OAuth / Credentials: https://console.cloud.google.com/apis/credentials?project=hansizappo-movie-teller
- Google Auth overview: https://console.cloud.google.com/auth/overview?project=hansizappo-movie-teller

## Required setup
1. Enable YouTube Data API v3.
2. Configure the OAuth consent / Google Auth audience for the account that will authorize the channel.
3. Create an OAuth 2.0 client ID appropriate for the eventual hosting flow.
4. Authorize the channel owner account and request only the required scopes:
   - https://www.googleapis.com/auth/youtube.upload
   - https://www.googleapis.com/auth/yt-analytics.readonly (only when analytics automation is implemented)
5. Store credentials only in GitHub Actions secrets or another secure secret store. Never commit client secrets, access tokens, or refresh tokens.

## Zero-budget guardrails
- Do not start a Google Cloud free trial.
- Do not attach a billing account or enable paid services.
- YouTube API authorization requires the channel owner's explicit Google consent.
- API keys alone cannot upload videos or access private channel analytics; those actions require OAuth 2.0.
- No video should be automatically published until the owner has reviewed and approved the publishing workflow.

## Current repository status
The existing GitHub Actions workflow renders a single checked-in episode and stores an MP4 artifact. It does not yet authenticate to YouTube, upload, schedule, or collect private analytics. Do not schedule the same episode for repeated uploads.
